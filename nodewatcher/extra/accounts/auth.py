import crypt
import md5crypt

from django.contrib import auth
from django.contrib.auth import backends as auth_backends, models as auth_models

try:
    # pylint: disable=import-error
    import aprmd5
    APR_ENABLED = True
except ImportError:
    APR_ENABLED = False


class AprBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticates against the database using Apache Portable Runtime MD5 hash function.
        """

        if not APR_ENABLED:
            return None

        UserModel = auth.get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(**{('%s__iexact' % UserModel.USERNAME_FIELD): username})
            if aprmd5.password_validate(password, user.password):
                # Successfully checked password, so we change it to the Django password format.
                user.set_password(password)
                user.save()
                return user
        except ValueError:
            pass
        except UserModel.DoesNotExist:
            pass

        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        UserModel().set_password(password)
        return None

    def get_user(self, user_id):
        """
        Translates the user ID into the User object.
        """

        UserModel = auth.get_user_model()
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class CryptBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticates against the database using crypt hash function.
        """

        UserModel = auth.get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(**{('%s__iexact' % UserModel.USERNAME_FIELD): username})
            if crypt.crypt(password, user.password) == user.password or md5crypt.md5crypt(password, user.password) == user.password:
                # Successfully checked password, so we change it to the Django password format.
                user.set_password(password)
                user.save()
                return user
        except ValueError:
            pass
        except UserModel.DoesNotExist:
            pass

        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        UserModel().set_password(password)
        return None

    def get_user(self, user_id):
        """
        Translates the user ID into the User object.
        """

        UserModel = auth.get_user_model()
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class ModelBackend(auth_backends.ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticates against the database using official implementation but
        catches exceptions and does it in case-insensitive manner.
        """

        UserModel = auth.get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel._default_manager.get(**{('%s__iexact' % UserModel.USERNAME_FIELD): username})
            if user.check_password(password):
                return user
        except ValueError:
            pass
        except UserModel.DoesNotExist:
            pass

        # Run the default password hasher once to reduce the timing
        # difference between an existing and a non-existing user (#20760).
        UserModel().set_password(password)
        return None
