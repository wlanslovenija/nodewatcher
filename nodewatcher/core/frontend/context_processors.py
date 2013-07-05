from django.conf import settings
from django.contrib import auth
from django.contrib.sites import models as sites_models

# TODO: Move to middleware and set a value on request object
def web_client_node(request):
    """
    Adds web_client_node variable to current template context
    depending on whether the current client's IP address is from
    a node's allocated subnet.
    """

    return {
        # TODO: Implement
        'web_client_node': None
    }

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
