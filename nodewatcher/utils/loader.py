from django.apps import apps
from django.utils import importlib, module_loading


def load_modules(*types):
    """
    Loads the per-application specific modules that must always be loaded
    before registry operations can function normally.

    :param types: Types of modules that should be loaded (type name
      determines the filename that is loaded)
    """

    # Note that we can't simply use module_loading.autodiscover_modules as it
    # doesn't work correctly when multiple module types are specified (it exits
    # on the first import failure). See: https://code.djangoproject.com/ticket/23670
    for app in apps.get_app_configs():
        for type in types:
            # Attempt to import the submodule if it exists
            if module_loading.module_has_submodule(app.module, type):
                importlib.import_module(".%s" % type, app.name)
