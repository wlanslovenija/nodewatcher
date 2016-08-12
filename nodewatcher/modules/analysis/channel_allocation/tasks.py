import datetime

from nodewatcher import celery

from nodewatcher.core.monitor import models as wifi_models
from ...monitor.http.survey import extract_nodes
from . import allocation_algorithms
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
    interface_dict = allocation_algorithms.meta_algorithm(extracted_graph['graph'], extracted_graph['known_nodes'])

    for interface in interface_dict:
        n = models.NodeChannel(
            interface=wifi_models.WifiInterfaceMonitor.objects.get(bssid=interface),
            optimal_channel=interface_dict[interface]
        )
        n.save()
