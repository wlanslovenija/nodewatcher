import base64

from django import http
from django.conf import settings
from django.views import generic
from django.views.decorators import csrf
from django.utils import decorators

from cryptography import x509
from cryptography.hazmat import backends
from cryptography.hazmat.primitives import serialization

from nodewatcher.core.monitor import tasks as monitor_tasks

# Ensure default cryptography backend is loaded.
backends.default_backend()


class HttpPushEndpoint(generic.View):
    @decorators.method_decorator(csrf.csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(HttpPushEndpoint, self).dispatch(*args, **kwargs)

    def post(self, request, uuid):
        """
        Handles HTTP push requests from nodewatcher-agent.
        """

        # Determine the remote IP address.
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            remote_ip = x_forwarded_for.split(',')[0]
        else:
            remote_ip = request.META.get('REMOTE_ADDR')

        # Determine client certificate. We assume that the HTTP server is configured so
        # that it populates the X-SSL-Certificate header with the PEM-encoded certificate.
        raw_certificate = request.META.get('HTTP_X_SSL_CERTIFICATE', None)
        if raw_certificate:
            # Decode X509 certificate.
            backend = backends.default_backend()
            try:
                raw_certificate = x509.load_pem_x509_certificate(raw_certificate, backend)
            except ValueError:
                if '-----BEGIN CERTIFICATE-----' not in raw_certificate:
                    # Assume it is just the Base64-encoded part without header/footer.
                    try:
                        raw_certificate = base64.b64decode(raw_certificate)
                        raw_certificate = x509.load_der_x509_certificate(raw_certificate, backend)
                    except (ValueError, TypeError):
                        raw_certificate = None
                else:
                    raw_certificate = None

        if raw_certificate:
            try:
                certificate = {
                    'public_key': raw_certificate.public_key().public_bytes(
                        serialization.Encoding.PEM, serialization.PublicFormat.PKCS1
                    ),
                    'subject': {},
                }

                attribute_map = {
                    x509.NameOID.COMMON_NAME: 'common_name',
                    x509.NameOID.COUNTRY_NAME: 'country',
                    x509.NameOID.LOCALITY_NAME: 'locality',
                    x509.NameOID.ORGANIZATION_NAME: 'organization',
                    x509.NameOID.ORGANIZATIONAL_UNIT_NAME: 'organizational_unit',
                }

                for attribute in raw_certificate.subject:
                    if attribute.oid in attribute_map:
                        certificate['subject'][attribute_map[attribute.oid]] = attribute.value
            except ValueError:
                certificate = None
        else:
            certificate = None

        # Schedule a new push task.
        monitor_tasks.run_pipeline.delay(
            run_id=settings.MONITOR_HTTP_PUSH_RUN,
            base_context={
                'push': {
                    'source': uuid,
                    'data': request.body,
                },
                'identity': {
                    'ip_address': remote_ip,
                    'certificate': certificate,
                }
            }
        )

        return http.JsonResponse({'status': 'ok'})
