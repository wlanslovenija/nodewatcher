import django
from django.conf import settings
from django.contrib import auth
from django.contrib.sites import shortcuts


def global_vars(request):
    """
    Adds some global variables to the context.
    """

    vars = {
        'NETWORK': getattr(settings, 'NETWORK', {}),
        'REDIRECT_FIELD_NAME': auth.REDIRECT_FIELD_NAME,

        'site': shortcuts.get_current_site(request),
        'request_get_next': request.GET.get(auth.REDIRECT_FIELD_NAME, ''),
    }

    return vars
