import datetime

from nodewatcher import celery

from nodewatcher.modules.monitor.http.survey import extract_nodes
from nodewatcher.modules.analysis.channel_allocation import allocation_algorithms
from . import models

# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.modules.analysis.channel_allocation.tasks.allocation'] = {
    'task': 'nodewatcher.modules.analysis.channel_allocation.tasks.allocation',
    'schedule': datetime.timedelta(seconds=10),
}


@celery.app.task(queue='monitor', bind=True)
def allocation(self):
    """
    Assigns an optimal channel to each known node in the graph to maximize spectral efficiency.
    """

    extracted_graph = extract_nodes.all_nodes_survey_graph(datetime.datetime.utcnow())
    if not extracted_graph:
        return

    # Run the coloring algorithm on the meta graph.
    node_channels = allocation_algorithms.meta_algorithm(extracted_graph['graph'], extracted_graph['known_nodes'])
    for node in node_channels:
        n = models.NodeChannel(node_interface=node, node_channel=node_channels[node])
        n.save()
