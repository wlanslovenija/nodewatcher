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


class NewNode(mixins.PermissionRequiredMixin, RegistryFormMixin, generic.DetailView):
    template_name = 'nodes/new.html'
    permission_required = 'add_node'

    def get_context_data(self, **kwargs):
        context = super(NewNode, self).get_context_data(**kwargs)
        context['registry_forms'] = self.dynamic_forms
        return context

    def get(self, request, *args, **kwargs):
        self.object = None

        self.dynamic_forms, self.eval_state = registry_forms.prepare_forms_for_regpoint_root(
            'node.config',
            request,
            None,
            also_rules=True,
        )

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        self.object = None

        sid = transaction.savepoint()
        try:
            self.object = core_models.Node()
            self.object.save()

            actions, partial_config = registry_forms.prepare_forms_for_regpoint_root(
                'node.config',
                request,
                self.object,
                data=request.POST,
                only_rules=True,
            )

            has_errors, self.dynamic_forms = registry_forms.prepare_forms_for_regpoint_root(
                'node.config',
                request,
                self.object,
                data=request.POST,
                save=True,
                actions=actions,
                current_config=partial_config,
            )

            if not has_errors:
                shortcuts.assign_perm('change_node', request.user, self.object)
                shortcuts.assign_perm('delete_node', request.user, self.object)
                shortcuts.assign_perm('reset_node', request.user, self.object)
                transaction.savepoint_commit(sid)
                return self.form_valid()
            else:
                transaction.savepoint_rollback(sid)
                self.dynamic_forms.root = None
                return self.form_invalid()
        except:
            transaction.savepoint_rollback(sid)
            raise

    def form_valid(self):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})


class EditNode(mixins.PermissionRequiredMixin, RegistryFormMixin, generic.DetailView):
    template_name = 'nodes/edit.html'
    model = core_models.Node
    permission_required = 'change_node'
    context_object_name = 'node'

    def get_context_data(self, **kwargs):
        context = super(EditNode, self).get_context_data(**kwargs)
        context['registry_forms'] = self.dynamic_forms
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.dynamic_forms, self.eval_state = registry_forms.prepare_forms_for_regpoint_root(
            'node.config',
            request,
            self.object,
            also_rules=True,
        )

        return self.render_to_response(self.get_context_data(object=self.object))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        actions, partial_config = registry_forms.prepare_forms_for_regpoint_root(
            'node.config',
            request,
            self.object,
            data=request.POST,
            only_rules=True,
        )

        has_errors, self.dynamic_forms = registry_forms.prepare_forms_for_regpoint_root(
            'node.config',
            request,
            self.object,
            data=request.POST,
            save=True,
            actions=actions,
            current_config=partial_config,
        )

        if not has_errors:
            return self.form_valid()
        else:
            return self.form_invalid()

    def get_success_url(self):
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})


class ResetNode(mixins.PermissionRequiredMixin, views.NodeNameMixin, generic.DetailView):
    template_name = 'nodes/reset.html'
    model = core_models.Node
    permission_required = 'reset_node'
    context_object_name = 'node'

    def reset(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        signals.reset_node.send(sender=self, request=request, node=self.object)
        return http.HttpResponseRedirect(success_url)

    def post(self, request, *args, **kwargs):
        if request.POST.get('reset', None):
            return self.reset(request, *args, **kwargs)
        else:
            self.object = self.get_object()
            return http.HttpResponseRedirect(self.get_cancel_url())

    def get_success_url(self):
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})

    def get_cancel_url(self):
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})


class RemoveNode(mixins.PermissionRequiredMixin, views.NodeNameMixin, generic.DeleteView):
    template_name = 'nodes/remove.html'
    model = core_models.Node
    permission_required = 'delete_node'
    context_object_name = 'node'

    def delete(self, request, *args, **kwargs):
        response = super(RemoveNode, self).delete(request, *args, **kwargs)
        signals.remove_node.send(sender=self, request=request, node=self.object)
        return response

    def post(self, request, *args, **kwargs):
        if request.POST.get('remove', None):
            return self.delete(request, *args, **kwargs)
        else:
            self.object = self.get_object()
            return http.HttpResponseRedirect(self.get_cancel_url())

    def get_success_url(self):
        # TODO: Where should we redirect here? What if list component is not enabled?
        return urlresolvers.reverse('ListComponent:list')

    def get_cancel_url(self):
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.object.pk})
