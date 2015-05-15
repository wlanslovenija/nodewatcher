import logging
import multiprocessing
import time
import traceback

from django import db
from django.db import connection, transaction

from . import processors as monitor_processors, exceptions
from .config import config as monitor_config
from .. import models as core_models

# Logger instance
logger = logging.getLogger('monitor.worker')


def stage_worker(args):
    """
    Runs a list of (node) processors on a given node.
    """

    context, node_pk, processors = args
    node = core_models.Node.objects.get(pk=node_pk)
    cleanup_queue = []
    try:
        for p in processors:
            try:
                abort_requested = False
                with transaction.atomic():
                    processor = p()
                    try:
                        context = processor.process(context, node)
                    except exceptions.NodeProcessorAbort:
                        # Do not run any further processors, but do not report this as an error and
                        # do not rollback the transaction.
                        abort_requested = True

                cleanup_queue.append(processor)
                if abort_requested:
                    break
            except KeyboardInterrupt:
                raise
            except:
                logger.error("Processor for node '%s' has failed with exception:" % node.pk)
                logger.error(traceback.format_exc())
                break
    finally:
        # Invoke all cleanup functions in reverse order
        for processor in cleanup_queue[::-1]:
            try:
                with transaction.atomic():
                    processor.cleanup(context, node)
            except:
                logger.warning("Processor cleanup method for node '%s' has failed with exception:" % node.pk)
                logger.warning(traceback.format_exc())


def main_worker(run):
    """
    Starts the given run.
    """

    global logger
    logger = logger.getChild('run.%s' % run.name)
    run.start()


def cycle_worker(run):
    """
    Starts a cycle of the given run.
    """

    run.cycle()


class MonitorRun(object):

    def __init__(self, config):
        self.name = config['name']
        self.config = config

    def prepare_workers(self):
        """
        Prepares a pool of worker processes that will be used for parallel
        execution of node processors.
        """

        # Close the connection before forking the workers as otherwise resources will be
        # shared and chaos will ensue
        connection.close()

        # Prepare worker processes
        try:
            self.workers = multiprocessing.Pool(
                self.config['workers'],
                maxtasksperchild=self.config['max_tasks_per_child'],
            )
        except TypeError:
            # Compatibility with Python 2.6 that doesn't have the maxtasksperchild argument
            self.workers = multiprocessing.Pool(self.config['workers'])

        logger.info("Ready with %d workers for run '%s'." % (self.config['workers'], self.name))

    def cycle(self):
        """
        Performs a single monitoring cycle.
        """

        logger.info("Preparing the worker pool for run '%s'..." % self.name)
        self.prepare_workers()

        try:
            nodes = set()
            context = monitor_processors.ProcessorContext()

            for processor_list in self.config['processors']:
                lead_proc = processor_list[0]
                if issubclass(lead_proc, monitor_processors.NetworkProcessor):
                    # Network processors run serially and may modify the nodes list
                    logger.info("Running network processor %s..." % lead_proc.__name__)

                    try:
                        if lead_proc.requires_transaction:
                            with transaction.atomic():
                                context, nodes = lead_proc(worker_pool=self.workers).process(context, nodes)
                        else:
                            context, nodes = lead_proc(worker_pool=self.workers).process(context, nodes)
                    except KeyboardInterrupt:
                        raise
                    except:
                        logger.error("Processor has failed with exception:")
                        logger.error(traceback.format_exc())
                elif issubclass(lead_proc, monitor_processors.NodeProcessor):
                    # Node processors run in parallel on all nodes
                    logger.info("Running the following node processors:")
                    for p in processor_list:
                        logger.info("  - %s" % p.__name__)

                    if self.config['process_only_node'] is not None:
                        logger.info("Limiting only to the following node: %s" % self.config['process_only_node'])
                        self.workers.map_async(stage_worker, ((context, node.pk, processor_list) for node in nodes if node.pk == self.config['process_only_node'])).get(0xFFFF)
                    else:
                        self.workers.map_async(stage_worker, ((context, node.pk, processor_list) for node in nodes)).get(0xFFFF)
                else:
                    logger.warning("Ignoring unkown type of processor '%s'!" % lead_proc.__name__)

            self.workers.terminate()
            self.workers = None
        finally:
            # Ensure that the worker pool gets cleaned up after processing is completed
            if self.workers:
                logger.info("Stopping worker processes...")
                self.workers.terminate()

        logger.info("All done.")

    def start(self):
        logger.info("Run '%s' entering monitoring cycle..." % self.name)
        try:
            cycle = 0
            while True:
                start = time.time()

                # Spawn monitoring cycle in its own process to isolate potential leaks
                p = multiprocessing.Process(target=cycle_worker, args=(self,))
                p.start()
                p.join()
                del p

                # Log the amount of time a cycle took
                cycle_duration = time.time() - start
                logger.info("Run took %d%% of configured period time." % int(100 * cycle_duration / self.config['interval']))

                if self.config['cycles'] is not None:
                    # Only increase cycle counter when limit is set
                    cycle += 1

                    if cycle >= self.config['cycles']:
                        logger.info("Reached %d cycles." % cycle)
                        break

                # Sleep for the right amount of time that cycles will be triggered
                # on every "interval" seconds (but no less then 30 seconds apart)
                time.sleep(max(30, self.config['interval'] - cycle_duration))
        except KeyboardInterrupt:
            logger.info("Aborted by user.")


class Worker(object):
    """
    Monitoring daemon.
    """

    def start_run(self, run, cycles=None, process_only_node=None):
        # Create a run descriptor.
        run_info = run.copy()
        run_info['cycles'] = cycles
        run_info['process_only_node'] = process_only_node
        rd = MonitorRun(run_info)

        # Fork a process for this run
        p = multiprocessing.Process(target=main_worker, args=(rd,))
        p.start()
        return p

    def run(self, cycles=None, process_only_node=None, filter_run=None):
        """
        Runs the monitoring process.
        """

        logger.info("Starting the nodewatcher monitoring system.")

        # Before running the process, ensure that the database is ready. This
        # is so we fail early instead of later when calling a processor.
        try:
            with transaction.atomic():
                pass
        except db.DatabaseError:
            logger.error("Failed to establish a database connection, exiting.")
            return

        logger.info("Starting monitoring runs...")
        runs = []
        for run in monitor_config.get_runs():
            if filter_run is not None and run != filter_run:
                continue

            # Ignore runs without any scheduling information.
            if run['on_demand']:
                continue

            runs.append(self.start_run(run, cycles, process_only_node))

        for p in runs:
            p.join()
