import uuid

from cryptography import x509
from cryptography.hazmat import backends

from nodewatcher.core import models as core_models
from nodewatcher.core.monitor import processors as monitor_processors

from . import models

# Ensure default cryptography backend is loaded.
backends.default_backend()


class DiscoverUnknownNodes(monitor_processors.NetworkProcessor):
    """
    A processor that discovers unknown nodes when they push data.
    """

    def process(self, context, nodes):
        """
        Performs network-wide processing and selects the nodes that will be processed
        in any following processors. Context is passed between network processors.

        :param context: Current context
        :param nodes: A set of nodes that are to be processed
        :return: A (possibly) modified context and a (possibly) modified set of nodes
        """

        if not context.push.source:
            return context, nodes

        try:
            core_models.Node.objects.get(uuid=context.push.source)
        except core_models.Node.DoesNotExist:
            # If there is currently no such node, add an unknown node record.
            try:
                if context.identity.certificate:
                    backend = backends.default_backend()

                    try:
                        raw = x509.load_pem_x509_certificate(context.identity.certificate, backend)
                        certificate = {
                            'raw': context.identity.certificate,
                            'subject': {},
                        }

                        attribute_map = {
                            x509.NameOID.COMMON_NAME: 'common_name',
                            x509.NameOID.COUNTRY_NAME: 'country',
                            x509.NameOID.LOCALITY_NAME: 'locality',
                            x509.NameOID.ORGANIZATION_NAME: 'organization',
                            x509.NameOID.ORGANIZATIONAL_UNIT_NAME: 'organizational_unit',
                        }

                        for attribute in raw.subject:
                            if attribute.oid in attribute_map:
                                certificate['subject'][attribute_map[attribute.oid]] = attribute.value
                    except ValueError:
                        certificate = None
                else:
                    certificate = None

                models.UnknownNode.objects.update_or_create(
                    uuid=str(uuid.UUID(context.push.source)),
                    defaults={
                        'ip_address': context.identity.ip_address or None,
                        'certificate': certificate,
                    },
                )
            except ValueError:
                # Ignore invalid UUIDs.
                pass

        return context, nodes
