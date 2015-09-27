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

    def form_valid(self, **kwargs):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, **kwargs):
        kwargs['object'] = self.object
        return self.render_to_response(self.get_context_data(**kwargs))


class RegistryCreateFormMixin(RegistryFormMixin):
    def get_node_uuid(self, **kwargs):
        """
        May return an UUID for the newly created node. The default implementation
        will return None and cause the UUID to be generated automatically.
        """

        return None

    def get_initial_flags(self, flags, **kwargs):
        """
        This method may provide initial form generation flags.

        :param flags: Existing form generation flags
        """

        return flags

    def initial_configuration(self, request, form_state, **kwargs):
        """
        This method may provide additional initial node configuration.
        """

        pass

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        self.object = None

        sid = transaction.savepoint()
        try:
            self.object = core_models.Node()
            self.object.save()

            form_state = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                flags=self.get_initial_flags(
                    registry_forms.FORM_INITIAL |
                    registry_forms.FORM_ONLY_DEFAULTS |
                    registry_forms.FORM_ROOT_CREATE
                ),
            )

            # Run the initial configuration hook.
            self.initial_configuration(request, form_state, **kwargs)

            has_errors, self.dynamic_forms = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                save=True,
                form_state=form_state,
                flags=registry_forms.FORM_OUTPUT,
            )

            self.dynamic_forms.root = None
        finally:
            try:
                transaction.savepoint_rollback(sid)
            except transaction.TransactionManagementError:
                # Rollback will fail if some query caused a database error and the whole
                # transaction is aborted anyway.
                pass

        return self.render_to_response(self.get_context_data(**kwargs))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = None

        sid = transaction.savepoint()
        try:
            self.object = core_models.Node(uuid=self.get_node_uuid(**kwargs))
            self.object.save()

            form_state = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                data=request.POST,
                flags=registry_forms.FORM_ONLY_DEFAULTS | registry_forms.FORM_ROOT_CREATE,
            )

            has_errors, self.dynamic_forms = registry_forms.prepare_root_forms(
                'node.config',
                request,
                self.object,
                data=request.POST,
                save=True,
                form_state=form_state,
                flags=registry_forms.FORM_OUTPUT | registry_forms.FORM_CLEAR_STATE,
            )

            if not has_errors:
                shortcuts.assign_perm('change_node', request.user, self.object)
                shortcuts.assign_perm('delete_node', request.user, self.object)
                shortcuts.assign_perm('reset_node', request.user, self.object)
                signals.post_create_node.send(sender=self, request=request, node=self.object)
                response = self.form_valid(**kwargs)
                transaction.savepoint_commit(sid)
                return response
            else:
                transaction.savepoint_rollback(sid)
                self.dynamic_forms.root = None
                return self.form_invalid(**kwargs)
        except:
            try:
                transaction.savepoint_rollback(sid)
            except transaction.TransactionManagementError:
                # Rollback will fail if some query caused a database error and the whole
                # transaction is aborted anyway.
                pass

            raise


class NewNode(mixins.PermissionRequiredMixin,
              views.CancelableFormMixin,
              RegistryCreateFormMixin,
              generic.TemplateView):
    template_name = 'nodes/new.html'
    permission_required = 'core.add_node'

    def form_valid(self, **kwargs):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

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

        kwargs['object'] = self.object
        return self.render_to_response(self.get_context_data(**kwargs))

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
            flags=registry_forms.FORM_OUTPUT | registry_forms.FORM_CLEAR_STATE,
        )

        if not has_errors:
            return self.form_valid(**kwargs)
        else:
            return self.form_invalid(**kwargs)


class EditNode(mixins.PermissionRequiredMixin,
               views.NodeNameMixin,
               views.CancelableFormMixin,
               RegistryEditFormMixin,
               generic.DetailView):
    template_name = 'nodes/edit.html'
    model = core_models.Node
    permission_required = 'core.change_node'
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
    permission_required = 'core.reset_node'
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
    permission_required = 'core.delete_node'
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
