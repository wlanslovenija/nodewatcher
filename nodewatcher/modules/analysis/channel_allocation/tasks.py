import datetime

from nodewatcher import celery

from nodewatcher.modules.monitor.http.survey import extract_nodes
from nodewatcher.modules.analysis.channel_allocation import allocation_algorithms


# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.modules.analysis.channel_allocation.tasks.allocation'] = {
    'task': 'nodewatcher.modules.analysis.channel_allocation.tasks.allocation',
    'schedule': datetime.timedelta(days=1),
}


@celery.app.task(queue='monitor', bind=True)
def allocation(self):
    """
    Assigns an optiomal channel to each known node in the graph to maximize spectral efficiency.
    """

    extracted_graph = extract_nodes.all_nodes_survey_graph(datetime.datetime.utcnow())

    if not extracted_graph:
        return

    # Run the coloring algorithm on the meta graph.
    node_channels = allocation_algorithms.meta_algorithm(extracted_graph['graph'])

    # Compare the optimal channel with the actual channel of every node.
    for node in node_channels:
        if node['optimal_channel'] != node['current_channel']:
            # Issue a warning for that node.
            pass
