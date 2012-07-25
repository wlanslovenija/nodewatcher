import logging
import multiprocessing
import traceback

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import connection, transaction
from django.utils import importlib

from nodewatcher.monitor import processors as monitor_processors

# Welcome banner
BANNER = """
--------------------------------------------------------
            nodewatcher monitoring system
--------------------------------------------------------
"""

# Logger instance
logger = logging.getLogger("monitor.worker")

@transaction.commit_manually
def stage_worker(args):
  """
  Runs a list of (node) processors on a given node.
  """
  context, node, processors = args
  for p in processors:
    try:
      context = p().process(context, node)
      transaction.commit()
    except KeyboardInterrupt:
      transaction.rollback()
      raise
    except:
      transaction.rollback()
      logger.error("Processor has failed with exception:")
      logger.error(traceback.format_exc())

class Worker(object):
  """
  Monitoring daemon.
  """
  def prepare_processors(self):
    """
    Loads all processors as specified in configuration and groups them
    accoording to their types.
    """
    self.processors = []
    for proc_module in settings.MONITOR_PROCESSORS:
      i = proc_module.rfind(".")
      module, attr = proc_module[:i], proc_module[i+1:]
      try:
        module = importlib.import_module(module)
        processor = getattr(module, attr)
      except (ImportError, AttributeError):
        raise ImproperlyConfigured("Error importing monitoring processor %s!" % proc_module)

      if not self.processors:
        self.processors.append([processor])
      else:
        prev_class = self.processors[-1][-1]
        curr_class = processor

        # Consecutive node processors are grouped together so they will all be run in parallel
        # on the list of nodes that has been prepared by recent network processor invocations
        if issubclass(prev_class, monitor_processors.NodeProcessor) and \
          issubclass(curr_class, monitor_processors.NodeProcessor):
          self.processors[-1].append(processor)
        else:
          self.processors.append([processor])

  def prepare_workers(self):
    """
    Prepares a pool of worker processes that will be used for parallel
    execution of node processors.
    """
    # Close the connection before forking the workers as otherwise resources will be
    # shared and chaos will ensue
    connection.close()

    # Prepare worker processes
    self.workers = multiprocessing.Pool(settings.MONITOR_WORKERS)
    logger.info("Ready with %d workers." % settings.MONITOR_WORKERS)

  @transaction.commit_manually
  def cycle(self):
    """
    Performs a single monitoring cycle.
    """
    nodes = set()
    context = monitor_processors.ProcessorContext()

    for processor_list in self.processors:
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
        self.workers.map(stage_worker, ((context, node, processor_list) for node in nodes))
      else:
        logger.warning("Ignoring unkown type of processor '%s'!" % lead_proc.__name__)

    logger.info("All done.")

  def run(self):
    """
    Runs the monitoring process.
    """
    # Show the welcome banner
    print BANNER

    logger.info("Loading processors...")
    self.prepare_processors()

    logger.info("Preparing the worker pool...")
    self.prepare_workers()

    logger.info("Entering monitoring cycle...")
    try:
      # TODO this should be run in a loop or something
      self.cycle()
    except KeyboardInterrupt:
      logger.info("Aborted by user.")
    finally:
      # Ensure that the worker pool gets cleaned up after processing is completed
      logger.info("Stopping worker processes...")
      self.workers.close()
      self.workers.join()

