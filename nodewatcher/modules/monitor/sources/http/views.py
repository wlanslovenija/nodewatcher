import ujson

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

        # TODO: Support client certificate validation.

        # Schedule a new push task.
        monitor_tasks.run_pipeline.delay(
            run_id=settings.MONITOR_HTTP_PUSH_RUN,
            base_context={
                'push': {
                    'source': uuid,
                    'data': request.body,
                }
            }
        )

        return http.JsonResponse({'status': 'ok'})
