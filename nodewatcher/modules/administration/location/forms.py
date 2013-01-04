from django import forms
from django.core import exceptions as django_exceptions

from nodewatcher.core.registry import registration, widgets as registry_widgets

from . import models

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
        except (django_exceptions.ObjectDoesNotExist, AttributeError, KeyError, IndexError):
            # Projects are not supported or not specified - in this case we fallback
            # to default coordinates specified in general configuration for the widget
            pass

registration.register_form_for_item(models.LocationConfig, LocationConfigForm)
