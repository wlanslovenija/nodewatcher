import itertools

from django.db.models import signals as model_signals

from django_datastream import datastream

from nodewatcher.core.monitor import processors as monitor_processors
from nodewatcher.core.registry import registration

from . import exceptions, models
from .pool import pool


class TrackRegistryModels(monitor_processors.NodeProcessor):
    """
    A processor that tracks registry models for changes, so that the datastream
    processor can know where to generate the streams from.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        # Start tracking the models
        context.datastream.tracked_models = {}

        def registry_track_save(sender, instance=None, **kwargs):
            if not isinstance(instance, registration.bases.NodeMonitoringRegistryItem):
                return

            context.datastream.tracked_models[(sender, instance.pk)] = instance

        def registry_track_delete(sender, instance=None, **kwargs):
            if not isinstance(instance, registration.bases.NodeMonitoringRegistryItem):
                return

            try:
                del context.datastream.tracked_models[(sender, instance.pk)]
            except KeyError:
                pass

        model_signals.post_save.connect(registry_track_save, weak=False, dispatch_uid="ds_track_models")
        model_signals.post_delete.connect(registry_track_delete, weak=False, dispatch_uid="ds_track_models")

        return context

    def cleanup(self, context, node):

        model_signals.post_save.disconnect(dispatch_uid="ds_track_models")
        model_signals.post_delete.disconnect(dispatch_uid="ds_track_models")


class Datastream(monitor_processors.NodeProcessor):
    """
    A processor that stores all monitoring data into the datastream.
    """

    def process(self, context, node):
        """
        Called for every processed node.

        :param context: Current context
        :param node: Node that is being processed
        :return: A (possibly) modified context
        """

        processed_items = set()
        for items in context.datastream.values():
            if isinstance(items, dict):
                items = items.values()
            elif not isinstance(items, list):
                items = [items]

            # Only include models that have known stream descriptors registered in
            # the descriptor pool
            for item in items:
                if item in processed_items:
                    continue
                processed_items.add(item)

                try:
                    descriptor = pool.get_descriptor(item)
                    descriptor.insert_to_stream(datastream)
                    pool.clear_descriptor(item)
                except exceptions.StreamDescriptorNotRegistered:
                    continue

        return context


class Maintenance(monitor_processors.NetworkProcessor):
    """
    Datastream maintenance processor.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        self.logger.info("Backprocessing streams...")
        datastream.backprocess_streams()
        self.logger.info("Downsampling streams...")
        datastream.downsample_streams()

        return context, nodes
