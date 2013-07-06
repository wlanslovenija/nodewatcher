from django.conf import settings
from django.contrib import auth
from django.contrib.sites import models as sites_models

def global_vars(request):
    """
    Adds some global variables to the context.
    """

    return {
        'NETWORK': {
            'NAME': settings.NETWORK_NAME,
            'HOME': settings.NETWORK_HOME,
            'CONTACT': getattr(settings, 'NETWORK_CONTACT', None),
            'CONTACT_PAGE': getattr(settings, 'NETWORK_CONTACT_PAGE', None),
            'DESCRIPTION': getattr(settings, 'NETWORK_DESCRIPTION', None),
            'FAVICON_URL': getattr(settings, 'NETWORK_FAVICON_URL', None),
            'LOGO_URL': getattr(settings, 'NETWORK_LOGO_URL', None),
        },
        'REDIRECT_FIELD_NAME': auth.REDIRECT_FIELD_NAME,

        'site': sites_models.get_current_site(request),
        'request_get_next': request.REQUEST.get(auth.REDIRECT_FIELD_NAME, ''),
    }
