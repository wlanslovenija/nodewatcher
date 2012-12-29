from django import forms

from . import models
from .allocation.ip import forms as ip_forms
from .registry import registration, widgets as registry_widgets

# TODO: Project model should be moved to core
from nodewatcher.legacy.nodes import models as nodes_models

class LocationConfigForm(forms.ModelForm):
    """
    Location configuration form.
    """

    class Meta:
        model = models.LocationConfig
        widgets = {
            'geolocation' : registry_widgets.LocationWidget(
                map_width = 400,
                map_height = 300
            )
        }

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modifies the form.
        """

        # Update the location widget's coordinates accoording to project
        try:
            project = cfg['core.project'][0].project

            self.fields['geolocation'].widget.default_location = [
                project.geo_lat,
                project.geo_long,
                project.geo_zoom
            ]
        except (nodes_models.Project.DoesNotExist, AttributeError, KeyError, IndexError):
            pass

registration.register_form_for_item(models.LocationConfig, LocationConfigForm)

class BasicAddressingConfigForm(forms.ModelForm, ip_forms.IpAddressAllocatorFormMixin):
    """
    General configuration form.
    """

    class Meta:
        model = models.BasicAddressingConfig

registration.register_form_for_item(models.BasicAddressingConfig, BasicAddressingConfigForm)
