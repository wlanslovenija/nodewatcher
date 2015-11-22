from django import dispatch
from django.contrib import auth, messages
from django.utils.translation import ugettext_lazy as _


@dispatch.receiver(auth.user_logged_in, dispatch_uid='user_login_message')
def user_login_message(sender, request, user, **kwargs):
    """
    Gives a success login message to the user.
    """

    messages.success(request, _("You have been successfully logged in."), fail_silently=True)


@dispatch.receiver(auth.user_logged_in, dispatch_uid='set_language')
def set_language(sender, request, user, **kwargs):
    """
    Sets Django language preference based on user profile.
    """

    request.session['django_language'] = user.profile.language


@dispatch.receiver(auth.user_logged_out, dispatch_uid='user_logout_message')
def user_logout_message(sender, request, user, **kwargs):
    """
    Gives a success logout message to the user.
    """

    messages.success(request, _("You have been successfully logged out."), fail_silently=True)
