import functools

from django import shortcuts
from django.conf import settings
from django.contrib import auth, messages
from django.core import exceptions
from django.utils import decorators
from django.utils.six.moves.urllib import parse
from django.utils.translation import ugettext_lazy as _


def user_test_required(test_func, message_func=None, message_level_func=lambda u: messages.INFO, redirect_url_func=lambda u: None, redirect_field_name=auth.REDIRECT_FIELD_NAME, decorator_id=None):
    """
    Decorator for views that checks that the user passes the given test, redirecting if necessary (by default to the profile page).
    The test should be a callable that takes the user object and returns True if the user passes. It can use optional message
    argument to tell the user the reason why she has be redirected, which should also be a callable that takes the user object as
    an argument.

    It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
    one used.
    """

    if decorator_id is None:
        decorator_id = id(user_test_required)

    def decorator(view_func):
        @functools.wraps(view_func, assigned=decorators.available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)

            path = request.build_absolute_uri()
            resolved_login_url = shortcuts.resolve_url(redirect_url_func(request.user) or settings.LOGIN_REDIRECT_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = parse.urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = parse.urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()

            if message_func:
                messages.add_message(request, message_level_func(request.user), message_func(request.user), fail_silently=True)

            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(path, resolved_login_url, redirect_field_name)

        _wrapped_view.decorators = []
        if hasattr(view_func, 'decorators'):
            _wrapped_view.decorators += view_func.decorators
        _wrapped_view.decorators.append(decorator_id)

        return _wrapped_view

    return decorator


def authenticated_required(function=None, message_func=lambda u: _("You have to be logged in while accessing the previous page. Please login to continue."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting if necessary (by default to the log-in page).

    It gives the user a message with a reason for redirect.

    It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
    one used.
    """

    actual_decorator = user_test_required(
        lambda u: u.is_authenticated(),
        message_func=message_func,
        message_level_func=message_level_func,
        redirect_url_func=redirect_url_func,
        redirect_field_name=redirect_field_name,
        decorator_id=id(authenticated_required),
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def anonymous_required(function=None, message_func=lambda u: _("You should not be logged in while accessing the previous page."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks whether the user is anonymous, redirecting if necessary (by default to the profile page).

    It gives the user a message with a reason for redirect.

    It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
    one used.
    """

    actual_decorator = user_test_required(
        lambda u: u.is_anonymous(),
        message_func=message_func,
        message_level_func=message_level_func,
        redirect_url_func=redirect_url_func,
        redirect_field_name=redirect_field_name,
        decorator_id=id(anonymous_required),
    )

    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(perm, message_func=lambda u: _("You do not have necessary permission to access the previous page."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME, raise_exception=False):
    """
    Decorator for views that checks whether the user has a particular permission enabled, redirecting if necessary (by default
    to the profile page).

    It gives the user a message with a reason for redirect.

    It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
    one used.
    """

    def check_perms(user):
        if not isinstance(perm, (list, tuple)):
            perms = (perm, )
        else:
            perms = perm
        # First check if the user has the permission (even anonymous users).
        if user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception.
        if raise_exception:
            raise exceptions.PermissionDenied
        # As the last resort, show the login form.
        return False

    return user_test_required(check_perms, message_func=message_func, message_level_func=message_level_func, redirect_url_func=redirect_url_func, redirect_field_name=redirect_field_name, decorator_id=id(permission_required))


def authenticated_permission_required(perm, message_func=lambda u: _("You do not have necessary permission to access the previous page.") if u.is_authenticated() else _("You have to be logged in while accessing the previous page. Please login to continue."), message_level_func=lambda u: messages.ERROR, redirect_url_func=lambda u: settings.LOGIN_REDIRECT_URL if u.is_authenticated() else settings.LOGIN_URL, redirect_field_name=auth.REDIRECT_FIELD_NAME, raise_exception=False):
    """
    Decorator for views that checks whether the user has authenticated and has a particular permission enabled, redirecting as
    necessary: if not authenticated to the log-in page, otherwise to the profile page.

    It also gives the user a proper message with a reason for redirect.

    It maintains `decorators` attribute on wrapped function with list of all ids of used decorators, where the first one is the first
    one used.
    """

    def check_perms(user):
        if not isinstance(perm, (list, tuple)):
            perms = (perm, )
        else:
            perms = perm
        # First check if the user has the permission (even anonymous users).
        if user.is_authenticated() and user.has_perms(perms):
            return True
        # In case the 403 handler should be called raise the exception.
        if raise_exception:
            raise exceptions.PermissionDenied
        # As the last resort, show the login form,
        return False

    return user_test_required(check_perms, message_func=message_func, message_level_func=message_level_func, redirect_url_func=redirect_url_func, redirect_field_name=redirect_field_name, decorator_id=id(authenticated_permission_required))
