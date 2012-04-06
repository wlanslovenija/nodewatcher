import logging
import multiprocessing
import traceback

from django.db import transaction

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

class Worker(object):
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
        sid = transaction.savepoint()
        context, nodes = p.preprocess(context, nodes)
        transaction.savepoint_commit(sid)
      except:
        transaction.savepoint_rollback(sid)
        logger.error("Preprocessor has failed with exception:")
        logger.error(traceback.format_exc())

    # Find nodes that haven't been claimed by any processor and are invalid; such
    # nodes should be removed from the database
    logger.info("Purging unclaimed stale nodes...")
    for node in nodes_models.Node.objects.regpoint("monitoring") \
      .filter(statusmonitor_status = "invalid") \
      .exclude(pk__in = nodes):
      node.delete()

    # Perform per-node processing in two stages
    logger.info("Running per-node first stage processors...")
    # TODO make this run in parallel
    for node in nodes:
      for p in monitor_processors.processors:
        try:
          sid = transaction.savepoint()
          context = p.process_first_pass(context, node)
          transaction.savepoint_commit(sid)
        except:
          transaction.savepoint_rollback(sid)
          logger.error("First stage processor has failed with exception:")
          logger.error(traceback.format_exc())

    # TODO second pass

    # TODO post-processing

  def run(self):
    print BANNER
    logger.info("Entering monitoring cycle...")
    self.cycle()

