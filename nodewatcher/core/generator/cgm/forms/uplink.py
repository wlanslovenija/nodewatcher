

class UplinkableFormMixin(object):
    """
    A mixin for address allocator forms.
    """

    def modify_to_context(self, item, cfg, request):
        """
        Dynamically modify the form.
        """

        # Hide default route announce if the interface is not an uplink.
        if not item.uplink:
            del self.fields['routing_default_announces']
