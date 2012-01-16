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
    nodes = list(nodes_models.Node.objects.all())
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

    # TODO where is node removal handled?

    #print nodes

  def run(self):
    print BANNER
    logger.info("Entering monitoring cycle...")
    self.cycle()

