from django import http
from django.core import urlresolvers
from django.views import generic

from guardian import mixins

from nodewatcher.core import models as core_models
from nodewatcher.core.frontend import views
from nodewatcher.core.generator import models as generator_models

from . import forms


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
    permission_required = 'generate_firmware'
    context_object_name = 'node'

    def get_success_url(self):
        return urlresolvers.reverse('GeneratorComponent:view_build', kwargs={'pk': self.build_result.pk})

    def get_cancel_url(self):
        # TODO: Where should we redirect here? What if display component is not enabled?
        return urlresolvers.reverse('DisplayComponent:node', kwargs={'pk': self.get_object().pk})


class ViewBuild(generic.DetailView):
    template_name = 'nodes/view_build.html'
    model = generator_models.BuildResult
