import datetime

from django.core import mail

from nodewatcher import celery

from nodewatcher.modules.monitor.http.survey.management.commands.export_survey_data import all_nodes_survey_graph
from .algorithm import rogue_node_detection_algorithm


# Register the periodic schedule.
celery.app.conf.CELERYBEAT_SCHEDULE['nodewatcher.modules.analysis.rogue_nodes.tasks.rogue_node_detection'] = {
    'task': 'nodewatcher.modules.analysis.rogue_nodes.tasks.rogue_node_detection',
    'schedule': datetime.timedelta(days=1),
}


@celery.app.task(queue='monitor', bind=True)
def rogue_node_detection(self):
    """
    Detects rogues nodes and issues a warning to its neighbors that are monitored by nodewatcher.
    """

    extracted_graph = all_nodes_survey_graph(datetime.datetime.utcnow())

    if not extracted_graph:
        return

    # Run the algorithm on the meta graph.
    unknown_node_list = rogue_node_detection_algorithm(extracted_graph['graph'], extracted_graph['known_nodes'])

    rogue_node_list = filter(lambda unknown_node: unknown_node['probability_being_rogue'] > 0.9, unknown_node_list)

    if rogue_node_list:
        mail.mail_admins(
            subject="Rogue nodes detected",
            message="We detected the following rogue nodes: {0}".format(rogue_node_list),
            fail_silently=False,
        )
