from django import http
from django.core import exceptions, urlresolvers
from django.db import transaction
from django.views import generic

from guardian import mixins, shortcuts

from nodewatcher.core import models as core_models
from nodewatcher.core.registry import forms as registry_forms


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


class NewNode(mixins.LoginRequiredMixin, RegistryFormMixin, generic.DetailView):
    template_name = 'nodes/new.html'

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
                shortcuts.assign_perm('remove_node', request.user, self.object)
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
