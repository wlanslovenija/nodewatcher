
class HookHandler(object):
    """
    All handlers must subclass this class, otherwise they will not get
    called.
    """
    pass

class Hookable(object):
    """
    A simple class that enables registration of hook methods. When invoking
    such a method, all registered hooks will be called, including the base
    one. Hook methods can't have a return value because multiple methods might
    be called which would require a result combiner.

    Simple usage example::

        class Test(hookable.Hookable):
            @hookable.hook
            def filter(self):
                pass

            def test(self):
                self.queryset = Foo.objects.all()
                self.filter()
                return self.queryset[0]

        class Handler(hookable.HookHandler):
            def filter(self):
                self.queryset = self.queryset.filter(x = True)

        Test.register_hooks(Handler)

    """

    @classmethod
    def register_hooks(cls, other):
        """
        Registers additional hook handlers for this class. Hook handlers
        also become superclasses of the current class.

        :param other: Class containing hook handlers
        """

        cls.__bases__ += (other,)

def hook(f):
    """
    A decorator for hook methods.
    """

    def wrapper(self, *args, **kwargs):
        for base in self.__class__.__mro__:
            # HookHandler must be a direct base
            if HookHandler not in base.__bases__:
                continue

            if hasattr(base, f.__name__):
                handler = getattr(base, f.__name__)
                # Skip hook wrappers to avoid infinite recursion
                if not hasattr(handler, '_hook'):
                    handler(self, *args, **kwargs)

        f(self, *args, **kwargs)

    wrapper._hook = True
    return wrapper
