from django import shortcuts, template
from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import models as auth_models, views as auth_views
from django.contrib.sites import shortcuts as sites_shortcuts
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from registration import models as registration_models
from registration.backends.model_activation import views as registration_views

from . import decorators, forms, utils


class RegistrationView(registration_views.RegistrationView):
    def get_form_class(self):
        """
        Returns the default form class used for user registration.

        It returns `nodewatcher.extra.accounts.forms.AccountRegistrationForm` form
        which contains fields for both user and user profile objects.
        """

        return utils.initial_accepts_request(self.request, forms.AccountRegistrationForm)

    def get_success_url(self, user):
        return ('AccountsComponent:registration_complete', (), {})


class ActivationView(registration_views.ActivationView):
    def get_success_url(self, user):
        return ('AccountsComponent:registration_activation_complete', (), {})


def user(request, username):
    """
    This view displays a public page for a given user.
    """

    user = shortcuts.get_object_or_404(auth_models.User, username=username)

    return shortcuts.render_to_response("users/user.html", {
        'profileuser': user,
    }, context_instance=template.RequestContext(request))


def get_user_copy(user):
    if isinstance(user, auth_models.AnonymousUser):
        return auth_models.AnonymousUser()

    for backend in auth.get_backends():
        user_copy = backend.get_user(user.pk)
        if user_copy is not None:
            return user_copy

    assert False


@decorators.authenticated_required
def account(request):
    """
    View which displays `nodewatcher.extra.accounts.forms.AccountChangeForm` form for users to change their account.

    If the user changes their e-mail address her account is inactivated and they gets an activation e-mail.
    """

    assert request.user.is_authenticated()

    if request.method == 'POST':
        stored_user = get_user_copy(request.user)

        form = forms.AccountChangeForm(request.POST, instance=[request.user, request.user.profile])

        if form.is_valid():
            objs = form.save()
            messages.success(request, _("Your account has been successfully updated."), fail_silently=True)

            old_email = stored_user.email
            new_email = request.user.email

            if old_email == new_email:
                # The last element is user profile object.
                return shortcuts.redirect(objs[-1])
            else:
                site = sites_shortcuts.get_current_site(request)

                request.user.is_active = False
                request.user.save()

                # Creates a new activation key.
                registration_models.RegistrationProfile.objects.filter(user=request.user).delete()
                registration_profile = registration_models.RegistrationProfile.objects.create_profile(request.user)
                registration_profile.send_activation_email(site, email_change=True)

                url = urlresolvers.reverse('AccountsComponent:email_change_complete')

                return logout_redirect(request, next_page=url)
        else:
            # Restore user request object as it is changed by form.is_valid.
            request.user = stored_user
            if hasattr(request.user, '_profile_cache'):
                # Invalidates profile cache.
                delattr(request.user, '_profile_cache')
    else:
        form = forms.AccountChangeForm(instance=[request.user, request.user.profile])

    return shortcuts.render_to_response("users/account.html", {
        'form': form,
    }, context_instance=template.RequestContext(request))


def logout_redirect(request, *args, **kwargs):
    """
    Logs out the user and redirects them to the log-in page or elsewhere, as specified.

    A wrapper around `django.contrib.auth.views.logout` view which prefers redirect to
    the `LOGIN_URL` instead of rendering the template.
    """

    kwargs.setdefault('redirect_field_name', auth.REDIRECT_FIELD_NAME)
    # We prefer redirect but explicit None for next_page makes it behave as the official logout view.
    redirect_field_name = kwargs.get('redirect_field_name')
    kwargs.setdefault('next_page', request.POST.get(redirect_field_name) or request.GET.get(redirect_field_name) or settings.LOGIN_URL)

    return auth_views.logout(request, *args, **kwargs)


@decorators.anonymous_required
def login(request, *args, **kwargs):
    """
    Displays the login form and handles the login action.

    A wrapper around `django.contrib.auth.views.login` view which uses our authentication form.
    """

    assert request.user.is_anonymous()

    kwargs.setdefault('authentication_form', forms.AuthenticationForm)
    return auth_views.login(request, *args, **kwargs)
