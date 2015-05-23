from django import forms
from django.apps import apps
from django.db import models

from nodewatcher.core.registry import registration

from . import models as td_models, signals


class TunneldiggerInterfaceConfigForm(forms.ModelForm):
    class Meta:
        model = td_models.TunneldiggerInterfaceConfig
        fields = '__all__'

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """

        if not apps.is_installed('nodewatcher.modules.administration.projects'):
            return

        from nodewatcher.modules.administration.projects import models as projects_models

        # Only display servers that are available.
        server = self.fields['server']
        qs = server.queryset
        query = models.Q(PerProjectTunneldiggerServer___project=None)

        try:
            # Only list the servers that are available for the selected project.
            project = cfg['core.project'][0].project
            if project:
                query |= models.Q(PerProjectTunneldiggerServer___project=project)
        except (projects_models.Project.DoesNotExist, KeyError, AttributeError):
            pass

        server.queryset = qs.filter(query)

        # Enable other modules to further filter the servers per some other attributes.
        signals.filter_servers.send(sender=self, server=server, item=item, cfg=cfg, request=request)

        # Cast back to non-polymorphic query.
        server.queryset = server.queryset.non_polymorphic().all()

registration.register_form_for_item(td_models.TunneldiggerInterfaceConfig, TunneldiggerInterfaceConfigForm)
