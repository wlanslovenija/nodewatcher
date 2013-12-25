import django
from django.conf import settings
from django.contrib import auth
from django.contrib.sites import models as sites_models


def global_vars(request):
    """
    Adds some global variables to the context.
    """

    vars = {
        'NETWORK': getattr(settings, 'NETWORK', {}),
        'REDIRECT_FIELD_NAME': auth.REDIRECT_FIELD_NAME,

        'site': sites_models.get_current_site(request),
        'request_get_next': request.REQUEST.get(auth.REDIRECT_FIELD_NAME, ''),
    }

    if django.VERSION < (1, 5):
        # In Django versions before 1.5, you could not use True, False or None
        # values directly in the template
        vars.update({
            'True': True,
            'False': False,
            'None': None,
        })

    return vars
