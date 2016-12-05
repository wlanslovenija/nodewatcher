from django import http
from django.conf import settings
from django.views import generic
from django.views.decorators import csrf
from django.utils import decorators, timezone

from nodewatcher.core.monitor import tasks as monitor_tasks
from nodewatcher.utils import datastructures

from . import signals


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

        context = {
            'push': {
                'source': uuid,
                'data': request.body,
                'timestamp': timezone.now(),
            },
            'identity': {
                'ip_address': remote_ip,
            }
        }

        # Emit signal to augment the context.
        contexts = signals.extract_context.send(sender=self.__class__, headers=request.META, uuid=uuid)
        for _, extracted_context in contexts:
            if not extracted_context:
                continue

            datastructures.merge_dict(context, extracted_context)

        # Schedule a new push task.
        monitor_tasks.run_pipeline.delay(
            run_id=settings.MONITOR_HTTP_PUSH_RUN,
            base_context=context,
        )

        return http.JsonResponse({'status': 'ok'})
