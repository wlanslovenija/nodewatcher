from nodewatcher.utils import toposort

__all__ = (
    'FormDefaults',
    'StopDefaults',
    'FormDefaultsModule',
    'ComplexFormDefaults',
)


class FormDefaults(object):
    """
    An abstract class for defining form defaults setters.
    """

    # Set to True to ensure that these defaults are applied even when the
    # user has disabled defaults for a specific device.
    always_apply = False

    def set_defaults(self, state, create):
        raise NotImplementedError


class StopDefaults(Exception):
    """
    An exception that can be used to stop complex defaults processing.
    """

    pass


class FormDefaultsModule(object):
    """
    An abstract class for complex defaults modules.

    Each module can have multiple parts (phases), which always execute in
    the following order:
    * Pre-configuration phase is executed first for all modules.
    * Configuration phase is executed second for all modules.
    * Post-configuration phase is executed last for all modules.

    Execution order inside each phase is only guaranteed based on
    declared requirements (requirements will always execute before the
    module in question) and is otherwise arbitrary.

    Each module can define dependencies using the ``requires`` attribute,
    which should be a list of required module instances.

    Additionally, each module can require the parent context to include
    specific variables, by declaring them in ``requires_context``.
    """

    requires = None
    requires_context = None

    def _pre_configure(self, context, state, create):
        return self.pre_configure(context, state, create)

    def pre_configure(self, context, state, create):
        """
        Run pre-configuration phase.

        :param context: Current defaults processing context
        :param state: Form state
        :param create: True if a new instance is being created
        """

        pass

    def _configure(self, context, state, create):
        return self.configure(context, state, create)

    def configure(self, context, state, create):
        """
        Run configuration phase.

        :param context: Current defaults processing context
        :param state: Form state
        :param create: True if a new instance is being created
        """

        pass

    def _post_configure(self, context, state, create):
        return self.post_configure(context, state, create)

    def post_configure(self, context, state, create):
        """
        Run post-configuration phase.

        :param context: Current defaults processing context
        :param state: Form state
        :param create: True if a new instance is being created
        """

        pass

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __hash__(self):
        return hash(self.__class__)


class ComplexFormDefaults(FormDefaults):
    """
    An abstract class for defining form defaults setters.

    The actual ``FormDefaultsModule`` instances that compute defaults should
    be passed as a list in the ``modules`` attribute.
    """

    modules = None

    def __init__(self, **kwargs):
        self.context = kwargs.copy()

    def set_defaults(self, state, create):
        context = self.context.copy()

        # Resolve module execution order based on declared dependencies.
        modules = {}
        queue = set(self.modules)
        while queue:
            module = queue.pop()
            if module in modules:
                continue

            modules[module] = {
                'module': module,
                'dependencies': module.requires or [],
            }

            if module.requires:
                queue.update(module.requires)

        try:
            modules = [m['module'] for ms in toposort.topological_sort(modules) for m in ms]
        except ValueError:
            raise ValueError("Circular dependencies exist between form defaults modules.")

        if not modules:
            raise NotImplementedError

        # Ensure any context requirements are satisfied before proceeding.
        for module in modules:
            if module.requires_context is None:
                continue

            for context_requirement in module.requires_context:
                if context_requirement not in context:
                    raise KeyError("Module '{}' requires parent context to contain '{}'.".format(
                        module.__class__.__name__,
                        context_requirement
                    ))

        try:
            # Run pre-configure hooks.
            for module in modules:
                module._pre_configure(context, state, create)

            # Run configure hooks.
            for module in modules:
                module._configure(context, state, create)

            # Run post-configure hooks.
            for module in modules:
                module._post_configure(context, state, create)
        except StopDefaults:
            pass
