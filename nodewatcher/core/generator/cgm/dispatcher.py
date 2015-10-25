from django import dispatch

from . import base


class Signal(dispatch.Signal):
    """
    A convenience signal class, tailored for CGM hooks.
    """

    def __init__(self, **kwargs):
        """
        Class constructor.
        """

        # Always include an argument containing the current platform configuration.
        providing_args = kwargs.setdefault('providing_args', [])
        providing_args.append('cfg')

        super(Signal, self).__init__(**kwargs)

    def _validate_send(self, sender, **named):
        if 'cfg' not in named:
            raise KeyError("CGM signals must contain a 'cfg' argument.")

        cfg = named['cfg']
        if not isinstance(cfg, base.PlatformConfiguration):
            raise TypeError("The 'cfg' argument must contain a platform configuration instance.")

    def send(self, sender, **named):
        self._validate_send(sender, **named)
        return super(Signal, self).send(sender, **named)

    def send_robust(self, sender, **named):
        self._validate_send(sender, **named)
        return super(Signal, self).send_robust(sender, **named)

    def connect(self, receiver, platform=None, **kwargs):
        # Wrap the receiver so that it will not be called when the platform doesn't match.
        def wrapper(sender, **kwargs):
            cfg = kwargs['cfg']
            if platform is not None and cfg.platform.name != platform:
                return

            return receiver(sender, **kwargs)

        kwargs['weak'] = False
        super(Signal, self).connect(wrapper, **kwargs)
