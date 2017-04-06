from django import http
from django.core import urlresolvers
from django.views import generic

from rest_framework import viewsets, filters

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import views
from nodewatcher.core.generator import models as generator_models
from nodewatcher.core.registry import api as registry_api
from nodewatcher.extra.accounts import mixins

from . import forms, serializers, permissions


class GenerateFirmwareMixin(object):
    def get_form(self, data=None):
        return forms.GenerateFirmwareForm(data=data, node=self.get_object())

    def get_context_data(self, **kwargs):
        context = super(GenerateFirmwareMixin, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.get_form()
        return context

    def generate_firmware(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.form = self.get_form(request.POST)
        if self.form.is_valid():
            self.build_result = self.form.generate(request)
            return self.form_valid()
        else:
            return self.form_invalid()

    def form_valid(self):
        return http.HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        return self.render_to_response(self.get_context_data(form=self.form))

    def post(self, request, *args, **kwargs):
        return self.generate_firmware(request, *args, **kwargs)


class GenerateFirmware(mixins.PermissionRequiredMixin,
                       views.NodeNameMixin,
                       views.CancelableFormMixin,
                       GenerateFirmwareMixin,
                       generic.DetailView):
    template_name = 'nodes/generate_firmware.html'
    model = core_models.Node
    permission_required = 'core.generate_firmware'
    context_object_name = 'node'

    def get_success_url(self):
        return urlresolvers.reverse('GeneratorComponent:view_build', kwargs={'pk': self.build_result.pk})

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.get_object().pk})


class ViewBuild(mixins.PermissionRequiredMixin,
                generic.DetailView):
    template_name = 'generator/view_build.html'
    model = generator_models.BuildResult
    permission_required = 'core.generate_firmware'
    context_object_name = 'build'

    def get_permission_object(self):
        return self.get_object().node


class ListBuilds(mixins.AuthenticatedRequiredMixin,
                 generic.TemplateView):
    template_name = 'generator/list_builds.html'


class BuildResultViewSet(registry_api.RegistryRootViewSetMixin,
                         viewsets.ReadOnlyModelViewSet):
    """
    Endpoint for build results.
    """

    queryset = generator_models.BuildResult.objects.all()
    serializer_class = serializers.BuildResultSerializer
    permission_classes = (permissions.BuildResultPermission,)
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ['uuid', 'status', 'created']
    registry_root_fields = ['node']

    def get_queryset(self):
        """
        Filter build results for the currently authenticated user.
        """

        qs = super(BuildResultViewSet, self).get_queryset()
        user = self.request.user
        if not user.is_authenticated():
            return qs.none()

        qs = qs.filter(
            user=user
        ).prefetch_related(
            'build_channel',
            'builder',
            'builder__version',
        ).order_by('uuid')
        return qs
