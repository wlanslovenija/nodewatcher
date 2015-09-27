from django import http, shortcuts
from django.core import urlresolvers, exceptions
from django.views import generic

from guardian import mixins

from nodewatcher.core.frontend import views
from nodewatcher.core.registry import forms as registry_forms
from nodewatcher.modules.frontend.editor import views as editor_views
from nodewatcher.modules.identity.base import models as identity_models
from nodewatcher.modules.identity.public_key import models as public_key_models

from . import models


class SuperuserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied

        return super(SuperuserRequiredMixin, self).dispatch(request, *args, **kwargs)


class ListUnknownNodes(generic.TemplateView):
    template_name = 'unknown_nodes/list.html'


class RegisterUnknownNode(mixins.PermissionRequiredMixin,
                          SuperuserRequiredMixin,
                          views.CancelableFormMixin,
                          editor_views.RegistryCreateFormMixin,
                          generic.TemplateView):
    template_name = 'unknown_nodes/register.html'
    permission_required = 'core.add_node'

    def get_context_data(self, **kwargs):
        context = super(RegisterUnknownNode, self).get_context_data(**kwargs)
        context['unknown_node_uuid'] = kwargs['uuid']
        return context

    def get_node_uuid(self, **kwargs):
        return kwargs['uuid']

    def get_initial_flags(self, flags, **kwargs):
        # Ensure defaults are disabled initially.
        return (flags | registry_forms.FORM_SET_DEFAULTS) & ~registry_forms.FORM_DEFAULTS_ENABLED

    def initial_configuration(self, request, form_state, **kwargs):
        # Get the unknown node instance.
        unknown_node = shortcuts.get_object_or_404(models.UnknownNode, uuid=kwargs['uuid'])
        self.unknown_node = unknown_node

        # Configure trusted certificate if available.
        if unknown_node.certificate.get('raw', None):
            identity_config = form_state.append_item(
                identity_models.IdentityConfig,
                trust_policy='first',
                store_unknown=True,
            )

            form_state.append_item(
                public_key_models.PublicKeyIdentityConfig,
                parent=identity_config,
                trusted=True,
                automatically_added=True,
                created=unknown_node.first_seen,
                last_seen=unknown_node.last_seen,
                public_key=unknown_node.certificate['raw'],
            )

    def form_valid(self, **kwargs):
        # Remove the unknown node.
        unknown_node = shortcuts.get_object_or_404(models.UnknownNode, uuid=kwargs['uuid'])
        unknown_node.delete()

        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_cancel_url(self):
        return urlresolvers.reverse('UnknownNodesComponent:list')

    def get_success_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})
