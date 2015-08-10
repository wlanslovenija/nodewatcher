from django.db import transaction

from celery.task import task as celery_task

from . import processors as monitor_processors, worker as monitor_worker
from .config import config as monitor_config


@celery_task(bind=True)
def run_pipeline(self, run_id, base_context=None):
    """
    Runs an on-demand monitoring run pipeline. Compared to a scheduled run, this
    is a much more simplified version as it is designed to be used to process
    push updates for a single node.

    :param run_id: Monitoring run identifier
    :param base_context: Optional base context dictionary
    """

    run_info = monitor_config.get_run(run_id)
    if not run_info['on_demand']:
        return

    # Prepare the on-demand monitoring run. The execution is a bit different than the
    # scheduled runs as here we don't spawn any additional workers or perform any
    # parallelization.
    nodes = set()
    context = monitor_processors.ProcessorContext()

    if base_context is not None:
        context.merge_with(base_context)

    for processor_list in run_info['processors']:
        lead_proc = processor_list[0]
        if issubclass(lead_proc, monitor_processors.NetworkProcessor):
            if lead_proc.requires_transaction:
                with transaction.atomic():
                    context, nodes = lead_proc().process(context, nodes)
            else:
                context, nodes = lead_proc().process(context, nodes)
        elif issubclass(lead_proc, monitor_processors.NodeProcessor):
            # Node processor also behaves differently, as we only process a single node. This is
            # to prevent runs from consuming too many resources as on-demand runs are meant for
            # push updates from a single node.
            if nodes:
                node = nodes.pop()

                # Store the per-node context, so we can limit its scope only to specific nodes in
                # order to avoid excessive context copying.
                node_local_context = context.for_node
                del context.for_node

                monitor_worker.stage_worker((
                    context,
                    node_local_context.get(node.pk, monitor_processors.ProcessorContext()),
                    node.pk,
                    processor_list
                ))

                # Restore per-node context for further network processors.
                context.for_node = node_local_context
