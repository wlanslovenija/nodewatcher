from django.conf import urls
from django.contrib.auth import views as auth_views
from django.core import urlresolvers
from django.utils import functional as functional_utils
from django.views.generic import simple as generic_simple

from registration import views as registration_views

from . import decorators, forms

# We pass redirect targets as a lazy unicode string as we are backreferencing.
# We wrap views with custom decorators to force anonymous and authenticated access to them (it is strange to
# try to register a new account while still logged in with another account). We redirect the user away and tell
# the user what has happened with messages.
# Some views use those decorators already so they are not used here. `logout_redirect` does not require
# authenticated access on purpose.
# We use custom login and logout views which give messages to the user explaining what has happened with login
# and logout. We do not assume the user understands what is happening behind the scenes.
urlpatterns = urls.patterns('',
    urls.url(r'^activate/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
        'template': 'registration/activation_complete.html',
    }, name='registration_activation_complete'),
    urls.url(r'^activate/(?P<activation_key>\w+)/$', decorators.anonymous_required(function=registration_views.activate), {
        'backend': 'nodewatcher.extra.account.regbackend.ProfileBackend',
    }, name='registration_activate'),
    urls.url(r'^register/$', decorators.anonymous_required(function=registration_views.register), {
        'backend': 'nodewatcher.extra.account.regbackend.ProfileBackend',
    }, name='registration_register'),
    urls.url(r'^register/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
        'template': 'registration/registration_complete.html',
    }, name='registration_complete'),
    urls.url(r'^register/closed/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
        'template': 'registration/registration_closed.html',
    }, name='registration_disallowed'),
    urls.url(r'^email/change/complete/$', decorators.anonymous_required(function=generic_simple.direct_to_template), {
        'template': 'registration/email_change_complete.html',
    }, name='email_change_complete'),
    urls.url(r'^login/$', 'nodewatcher.extra.account.views.login', name='auth_login'),
    urls.url(r'^logout/$', 'nodewatcher.extra.account.views.logout_redirect', name='auth_logout'),
    urls.url(r'^password/change/$', decorators.authenticated_required(function=auth_views.password_change), {
        'post_change_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_change_done'),
        'password_change_form': forms.PasswordChangeForm,
    }, name='auth_password_change'),
    urls.url(r'^password/change/complete/$', decorators.authenticated_required(function=auth_views.password_change_done), name='auth_password_change_done'),
    urls.url(r'^password/reset/$', decorators.anonymous_required(function=auth_views.password_reset), {
        'email_template_name': 'registration/password_reset_email.txt',
        'password_reset_form': forms.PasswordResetForm,
        'post_reset_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_reset_done'),
    }, name='auth_password_reset'),
    urls.url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', decorators.anonymous_required(function=auth_views.password_reset_confirm), {
        'set_password_form': forms.SetPasswordForm,
        'post_reset_redirect': functional_utils.lazy(urlresolvers.reverse, unicode)('auth_password_reset_complete'),
    }, name='auth_password_reset_confirm'),
    urls.url(r'^password/reset/complete/$', decorators.anonymous_required(function=auth_views.password_reset_complete), name='auth_password_reset_complete'),
    urls.url(r'^password/reset/done/$', decorators.anonymous_required(function=auth_views.password_reset_done), name='auth_password_reset_done'),
    urls.url(r'^$', 'nodewatcher.extra.account.views.account', name='user_account'),
)