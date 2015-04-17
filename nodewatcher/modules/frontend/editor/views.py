from django import http
from django.core import exceptions, urlresolvers
from django.db import transaction
from django.views import generic

from guardian import mixins, shortcuts

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import views
from nodewatcher.core.registry import forms as registry_forms

from . import signals


class RegistryFormMixin(object):
    success_url = None
    cancel_url = None

    def get_context_data(self, **kwargs):
        context = super(RegistryFormMixin, self).get_context_data(**kwargs)
        context['registry_forms'] = self.dynamic_forms
        return context

    def get_success_url(self):
        if self.success_url:
            url = self.success_url
        else:
            raise exceptions.ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        return self.render_to_response(self.get_context_data(object=self.object))


class RegistryCreateFormMixin(RegistryFormMixin):
    def get(self, request, *args, **kwargs):
        self.object = None

        self.dynamic_forms = registry_forms.prepare_root_forms(
            'node.config',
            request,
            None,
            flags=registry_forms.FORM_INITIAL | registry_forms.FORM_OUTPUT | registry_forms.FORM_DEFAULTS,
        )

        return self.render_to_response(self.get_context_data())

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = None

        sid = transaction.savepoint()
        try:
            self.object = core_models.Node()
            self.object.save()

            form_state = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                data=request.POST,
                flags=registry_forms.FORM_ONLY_DEFAULTS,
            )

            has_errors, self.dynamic_forms = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                data=request.POST,
                save=True,
                form_state=form_state,
                flags=registry_forms.FORM_OUTPUT,
            )

            if not has_errors:
                shortcuts.assign_perm('change_node', request.user, self.object)
                shortcuts.assign_perm('delete_node', request.user, self.object)
                shortcuts.assign_perm('reset_node', request.user, self.object)
                signals.post_create_node.send(sender=self, request=request, node=self.object)
                transaction.savepoint_commit(sid)
                return self.form_valid()
            else:
                transaction.savepoint_rollback(sid)
                self.dynamic_forms.root = None
                return self.form_invalid()
        except:
            transaction.savepoint_rollback(sid)
            raise


class NewNode(mixins.PermissionRequiredMixin,
              views.CancelableFormMixin,
              RegistryCreateFormMixin,
              generic.TemplateView):
    template_name = 'nodes/new.html'
    permission_required = 'add_node'

    def form_valid(self):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        return self.render_to_response(self.get_context_data())

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if mynodes component is not enabled?
        return urlresolvers.reverse('MyNodesComponent:mynodes')

    def get_success_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})


class RegistryEditFormMixin(RegistryFormMixin):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.dynamic_forms = registry_forms.prepare_root_forms(
            'node.config',
            request,
            self.object,
            flags=registry_forms.FORM_INITIAL | registry_forms.FORM_OUTPUT | registry_forms.FORM_DEFAULTS,
        )

        return self.render_to_response(self.get_context_data(object=self.object))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_state = registry_forms.prepare_root_forms(
            'node.config',
            request,
            self.object,
            data=request.POST,
            flags=registry_forms.FORM_ONLY_DEFAULTS,
        )

        has_errors, self.dynamic_forms = registry_forms.prepare_root_forms(
            'node.config',
            request,
            self.object,
            data=request.POST,
            save=True,
            form_state=form_state,
            flags=registry_forms.FORM_OUTPUT,
        )

        if not has_errors:
            return self.form_valid()
        else:
            return self.form_invalid()


class EditNode(mixins.PermissionRequiredMixin,
               views.NodeNameMixin,
               views.CancelableFormMixin,
               RegistryEditFormMixin,
               generic.DetailView):
    template_name = 'nodes/edit.html'
    model = core_models.Node
    permission_required = 'change_node'
    context_object_name = 'node'

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.get_object().pk})

    def get_success_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})


class ResetNodeMixin(object):
    def reset(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        signals.pre_reset_node.send(sender=self, request=request, node=self.object)
        signals.reset_node.send(sender=self, request=request, node=self.object)
        signals.post_reset_node.send(sender=self, request=request, node=self.object)
        return http.HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        return self.reset(request, *args, **kwargs)


class ResetNode(mixins.PermissionRequiredMixin,
                views.NodeNameMixin,
                views.CancelableFormMixin,
                ResetNodeMixin,
                generic.DetailView):
    template_name = 'nodes/reset.html'
    model = core_models.Node
    permission_required = 'reset_node'
    context_object_name = 'node'

    def get_success_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.get_object().pk})


class RemoveNode(mixins.PermissionRequiredMixin,
                 views.NodeNameMixin,
                 views.CancelableFormMixin,
                 generic.DeleteView):
    template_name = 'nodes/remove.html'
    model = core_models.Node
    permission_required = 'delete_node'
    context_object_name = 'node'

    def delete(self, request, *args, **kwargs):
        # Need to use get_object instead of object here, because self.object is only
        # fetched by the super delete method
        signals.pre_remove_node.send(sender=self, request=request, node=self.get_object())
        response = super(RemoveNode, self).delete(request, *args, **kwargs)
        signals.post_remove_node.send(sender=self, request=request, node=self.object)
        return response

    def get_success_url(self):
        # TODO: Where should we redirect here? What if list component is not enabled?
        return urlresolvers.reverse('ListComponent:list')

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.get_object().pk})
