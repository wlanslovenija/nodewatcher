from django.db import transaction

from nodewatcher.core.events import base, pool, events

from . import models


class DatabaseSink(base.EventSink):
    """
    An event sink that stores events into the database.
    """

    def deliver(self, event):
        """
        Persists the received event into the database.
        """

        if not isinstance(event, events.NodeEventRecord):
            return

        sid = transaction.savepoint()
        try:
            mdl = models.SerializedNodeEvent()
            mdl.timestamp = event.timestamp
            mdl.severity = event.severity
            mdl.title = event.title
            mdl.source_name = event.source_name
            mdl.source_type = event.source_type
            mdl.description = event.description

            # Remove fields that are already in the database
            record = event.record.copy()
            del record['timestamp']
            del record['severity']
            del record['title']
            del record['source_name']
            del record['source_type']
            del record['description']
            del record['related_nodes']
            mdl.record = record

            mdl.save()
            # Add related nodes
            mdl.related_nodes.add(*event.related_nodes)
            transaction.savepoint_commit(sid)
        except:
            transaction.savepoint_rollback(sid)
            raise

pool.register(DatabaseSink)
