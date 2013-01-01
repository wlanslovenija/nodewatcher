from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

def load_modules(*types):
    """
    Loads the per-application specific modules that must always be loaded
    before registry operations can function normaly.

    :param types: Types of modules that should be loaded (type name
        determines the filename that is loaded)
    """

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        
        for type in types:
            # Attempt to import the submodule if it exists
            if module_has_submodule(mod, type):
                import_module(".%s" % type, app)
