import logging
import multiprocessing
import time
import traceback

from django.conf import settings
from django.core import exceptions
from django.db import connection, transaction
from django.utils import importlib

from . import processors as monitor_processors
from .. import models as core_models

# Welcome banner
BANNER = """
--------------------------------------------------------
            nodewatcher monitoring system
--------------------------------------------------------
"""

# Logger instance
logger = logging.getLogger('monitor.worker')


@transaction.commit_manually
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
                processor = p()
                context = processor.process(context, node)
                transaction.commit()
                cleanup_queue.append(processor)
            except KeyboardInterrupt:
                transaction.rollback()
                raise
            except:
                transaction.rollback()
                logger.error("Processor for node '%s' has failed with exception:" % node.pk)
                logger.error(traceback.format_exc())
                break
    finally:
        # Invoke all cleanup functions in reverse order
        for processor in cleanup_queue[::-1]:
            try:
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


class MonitorRun(object):

    def __init__(self, name, config):
        self.name = name
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
            self.workers = multiprocessing.Pool(self.config['workers'], maxtasksperchild=1000)
        except TypeError:
            # Compatibility with Python 2.6 that doesn't have the maxtasksperchild argument
            self.workers = multiprocessing.Pool(self.config['workers'])

        logger.info("Ready with %d workers for run '%s'." % (self.config['workers'], self.name))

    @transaction.commit_manually
    def cycle(self):
        """
        Performs a single monitoring cycle.
        """

        nodes = set()
        context = monitor_processors.ProcessorContext()

        for processor_list in self.config['processors']:
            lead_proc = processor_list[0]
            if issubclass(lead_proc, monitor_processors.NetworkProcessor):
                # Network processors run serially and may modify the nodes list
                logger.info("Running network processor %s..." % lead_proc.__name__)

                try:
                    context, nodes = lead_proc().process(context, nodes)
                    transaction.commit()
                except KeyboardInterrupt:
                    transaction.rollback()
                    raise
                except:
                    transaction.rollback()
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

        logger.info("All done.")

    def start(self):
        logger.info("Preparing the worker pool for run '%s'..." % self.name)
        self.prepare_workers()

        logger.info("Run '%s' entering monitoring cycle..." % self.name)
        try:
            cycle = 0
            while True:
                start = time.time()
                self.cycle()

                cycle += 1
                if self.config['cycles'] is not None and cycle >= self.config['cycles']:
                    logger.info("Reached %d cycles." % cycle)
                    break

                # Sleep for the right amount of time that cycles will be triggered
                # on every "interval" seconds (but no less then 30 seconds apart)
                cycle_duration = time.time() - start
                time.sleep(max(30, self.config['interval'] - cycle_duration))
        except KeyboardInterrupt:
            logger.info("Aborted by user.")
        finally:
            # Ensure that the worker pool gets cleaned up after processing is completed
            logger.info("Stopping worker processes...")
            self.workers.terminate()


class Worker(object):
    """
    Monitoring daemon.
    """

    def prepare_processors(self):
        """
        Loads all processors as specified in configuration and groups them
        accoording to their types.
        """

        self.runs = {}
        for run, config in settings.MONITOR_RUNS.iteritems():
            processors = []
            for proc_module in config['processors']:
                i = proc_module.rfind('.')
                module, attr = proc_module[:i], proc_module[i + 1:]
                try:
                    module = importlib.import_module(module)
                    processor = getattr(module, attr)
                except (ImportError, AttributeError):
                    raise exceptions.ImproperlyConfigured("Error importing monitoring processor %s!" % proc_module)

                if not processors:
                    processors.append([processor])
                else:
                    prev_class = processors[-1][-1]
                    curr_class = processor

                    # Consecutive node processors are grouped together so they will all be run in parallel
                    # on the list of nodes that has been prepared by recent network processor invocations
                    if issubclass(prev_class, monitor_processors.NodeProcessor) and issubclass(curr_class, monitor_processors.NodeProcessor):
                        processors[-1].append(processor)
                    else:
                        processors.append([processor])

            self.runs[run] = {
                'interval': config['interval'],
                'workers': config['workers'],
                'processors': processors,
            }

    def start_run(self, run, cycles=None, process_only_node=None):
        # Create a run descriptor
        self.runs[run]['cycles'] = cycles
        self.runs[run]['process_only_node'] = process_only_node
        rd = MonitorRun(run, self.runs[run])

        # Fork a process for this run
        p = multiprocessing.Process(target=main_worker, args=(rd,))
        p.start()
        return p

    def run(self, cycles=None, process_only_node=None, run=None):
        """
        Runs the monitoring process.
        """

        # Show the welcome banner
        print BANNER

        logger.info("Loading processors...")
        self.prepare_processors()

        logger.info("Starting monitoring runs...")
        runs = []
        for r in self.runs.keys():
            if run is not None and r != run:
                continue
            runs.append(self.start_run(r, cycles, process_only_node))

        for p in runs:
            p.join()
