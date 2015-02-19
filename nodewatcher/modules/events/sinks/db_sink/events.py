from django.db import transaction

from nodewatcher.core.events import base, pool, declarative

from . import models


class DatabaseEventSink(base.EventSink):
    """
    An event sink that stores events into the database.
    """

    def deliver(self, event):
        """
        Persists the received event into the database.
        """

        if not isinstance(event, declarative.NodeEventRecord):
            return
        elif isinstance(event, declarative.NodeWarningRecord):
            return

        with transaction.atomic():
            mdl = models.SerializedNodeEvent()
            mdl.timestamp = event.timestamp
            mdl.severity = event.severity
            mdl.source_name = event.source_name
            mdl.source_type = event.source_type

            # Remove fields that are already in the database
            record = event.record.copy()
            del record['timestamp']
            del record['severity']
            del record['source_name']
            del record['source_type']
            del record['related_nodes']
            del record['related_users']
            mdl.record = record

            mdl.save()
            # Add related nodes
            mdl.related_nodes.add(*event.related_nodes)
            # Add related users
            if event.related_users is not None:
                mdl.related_users.add(*event.related_users)

pool.register_sink(DatabaseEventSink)


class DatabaseWarningSink(base.EventSink):
    """
    An event sink that stores warnings into the database.
    """

    def deliver(self, event):
        """
        Persists the received warning into the database.
        """

        if not isinstance(event, declarative.NodeWarningRecord):
            return

        with transaction.atomic():
            if event.is_absent():
                # This is actually a complementary event, signalling the absence of a warning.
                models.SerializedNodeWarning.objects.filter(pk=event.get_primary_key()).delete()
            else:
                mdl, created = models.SerializedNodeWarning.objects.get_or_create(
                    pk=event.get_primary_key(),
                    defaults={
                        'severity': event.severity,
                        'source_name': event.source_name,
                        'source_type': event.source_type,
                    }
                )

                if created:
                    # Add related nodes.
                    mdl.related_nodes.add(*event.related_nodes)

                # Remove fields that are already in the database.
                record = event.record.copy()
                del record['timestamp']
                del record['severity']
                del record['source_name']
                del record['source_type']
                del record['related_nodes']
                del record['related_users']
                mdl.record = record

                mdl.save()

pool.register_sink(DatabaseWarningSink)
