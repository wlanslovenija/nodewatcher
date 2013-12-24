from django.conf import settings
from django.utils import importlib, module_loading


def load_modules(*types):
    """
    Loads the per-application specific modules that must always be loaded
    before registry operations can function normally.

    :param types: Types of modules that should be loaded (type name
                  determines the filename that is loaded)
    """

    for app in settings.INSTALLED_APPS:
        mod = importlib.import_module(app)

        for type in types:
            # Attempt to import the submodule if it exists
            if module_loading.module_has_submodule(mod, type):
                importlib.import_module(".%s" % type, app)
