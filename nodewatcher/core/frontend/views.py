from django import http
from django.core import exceptions
from django.utils import encoding
from django.utils.translation import ugettext_lazy as _


class NodeNameMixin(object):
    def get_context_data(self, **kwargs):
        context = super(NodeNameMixin, self).get_context_data(**kwargs)
        context['node_name'] = getattr(self.object.config.core.general(), 'name', None) or _("unknown")
        return context


class CancelableFormMixin(object):
    def post(self, request, *args, **kwargs):
        if request.POST.get('cancel', None):
            return http.HttpResponseRedirect(self.get_cancel_url())
        else:
            return super(CancelableFormMixin, self).post(request, *args, **kwargs)

    def get_cancel_url(self):
        if self.cancel_url:
            # Forcing possible reverse_lazy evaluation
            url = encoding.force_text(self.success_url)
        else:
            raise exceptions.ImproperlyConfigured("No URL to redirect to. Provide a cancel_url.")
        return url
