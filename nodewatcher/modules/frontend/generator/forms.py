from django import forms
from django.utils.translation import ugettext as _

from nodewatcher.core.generator.cgm import base as cgm_base, exceptions


class GenerateFirmwareForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.node = kwargs['node']
        del kwargs['node']
        super(GenerateFirmwareForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(GenerateFirmwareForm, self).clean()

        # Validate that node build will work.
        try:
            if not cgm_base.generate_firmware(self.node, only_validate=True):
                raise forms.ValidationError(_("No build platform is configured for this node!"), code='no_platform')
        except cgm_base.ValidationError, e:
            raise forms.ValidationError(e.args[0])
        except exceptions.NoBuildChannelsConfigured:
            raise forms.ValidationError(_("No build channels have been configured!"), code='no_build_channels')
        except exceptions.NoBuildersConfigured:
            raise forms.ValidationError(_("No builders have been configured!"), code='no_builders')
        except exceptions.NoSuitableBuildersFound:
            raise forms.ValidationError(_("No suitable builder could be found!"), code='no_builder')
        except exceptions.BuilderInconsistent:
            raise forms.ValidationError(_("Builder configuration is inconsistent with current state!"), code='inconsistent_builder')
        except exceptions.NoDeviceConfigured:
            raise forms.ValidationError(_("No device has been configured!"), code='no_device')

        return cleaned_data

    def generate(self, request):
        """
        Queues a firmware generation request for the specified node.

        :param request: HTTP request
        :return: An instance of BuildResult
        """

        return cgm_base.generate_firmware(self.node, user=request.user)
