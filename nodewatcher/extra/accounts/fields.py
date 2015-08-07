from django.conf import settings
from django.db.models import fields
from django.utils import translation
from django.utils.translation import ugettext_lazy as _


languages_choices = map(lambda (code, name): (code, _(name)), settings.LANGUAGES) # We have to translate names


def get_initial_language(request=None):
    """
    Returns language code based on a request or settings.
    """

    if request:
        return translation.get_language_from_request(request)
    return settings.LANGUAGE_CODE


class LanguageField(fields.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 5)
        kwargs.setdefault('choices', languages_choices)
        kwargs.setdefault('default', get_initial_language)

        super(LanguageField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"
