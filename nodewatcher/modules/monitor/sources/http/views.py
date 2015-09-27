from django import http
from django.conf import settings
from django.views import generic
from django.views.decorators import csrf
from django.utils import decorators

from nodewatcher.core.monitor import tasks as monitor_tasks


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
                    # We assume that the HTTP server is configured so that it populates
                    # the X-SSL-Certificate header with the PEM-encoded certificate.
                    'certificate': request.META.get('HTTP_X_SSL_CERTIFICATE', None),
                }
            }
        )

        return http.JsonResponse({'status': 'ok'})
