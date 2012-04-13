import copy
import logging
import multiprocessing
import traceback

from django.conf import settings
from django.db import connection, transaction

from web.core.monitor import processors as monitor_processors
from web.nodes import models as nodes_models

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
  Runs stage processors on a given node.
  """
  context, node, stage = args
  for p in monitor_processors.processors:
    try:
      getattr(p, stage)(context, node)
      transaction.commit()
    except KeyboardInterrupt:
      transaction.rollback()
      raise
    except:
      transaction.rollback()
      logger.error("First stage processor has failed with exception:")
      logger.error(traceback.format_exc())

class Worker(object):
  @transaction.commit_manually
  def cycle(self):
    """
    Performs a single monitoring cycle.
    """
    nodes = set()
    context = monitor_processors.ProcessorContext()
    
    # Pre-processing
    for p in monitor_processors.processors:
      try:
        logger.info("Running preprocessor %s..." % p.__class__.__name__)
        context, nodes = p.preprocess(context, nodes)
        transaction.commit()
      except KeyboardInterrupt:
        transaction.rollback()
        raise
      except:
        transaction.rollback()
        logger.error("Preprocessor has failed with exception:")
        logger.error(traceback.format_exc())

    # Find nodes that haven't been claimed by any processor and are invalid; such
    # nodes should be removed from the database
    logger.info("Purging unclaimed stale nodes...")
    with transaction.commit_on_success():
      for node in nodes_models.Node.objects.regpoint("monitoring") \
        .filter(statusmonitor_status = "invalid") \
        .exclude(pk__in = nodes):
        node.delete()

    # Perform per-node processing in two stages
    logger.info("Running per-node first pass processors...")
    self.workers.map(stage_worker, ((context, node, "process_first_pass") for node in nodes))
    logger.info("First pass completed.")

    logger.info("Running per-node second pass processors...")
    self.workers.map(stage_worker, ((context, node, "process_second_pass") for node in nodes))
    logger.info("Second pass completed.")

    # TODO post-processing

    logger.info("All done.")

  def prepare_workers(self):
    # Close the connection before forking the workers as otherwise resources will be
    # shared and chaos will ensue
    connection.close()

    # Prepare worker processes
    self.workers = multiprocessing.Pool(settings.MONITOR_WORKERS)
    logger.info("Ready with %d workers." % settings.MONITOR_WORKERS)

  def run(self):
    print BANNER
    logger.info("Preparing the worker pool...")
    self.prepare_workers()

    logger.info("Entering monitoring cycle...")
    try:
      self.cycle()
    except KeyboardInterrupt:
      logger.info("Aborted by user.")
    finally:
      # Ensure that the worker pool gets cleaned up after processing is completed
      self.workers.close()
      self.workers.join()

