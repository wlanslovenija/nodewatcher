from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors


class PurgeInvalidNodes(processors.NetworkProcessor):
    def process(self, context, nodes):
        """
        Finds nodes that haven't been claimed by any processor and are invalid. Such
        nodes are removed from the database.
        """

        self.logger.info("Purging unclaimed stale nodes...")
        for node in core_models.Node.objects.regpoint('monitoring').filter(statusmonitor_status='invalid').exclude(pk__in=nodes):
            node.delete()

        return context, nodes
