class RegistryFormProcessor(object):
    """
    A registry form processor can be used to hook into the form validation
    process. The class gets instantiated before forms are generated and
    preprocessing is executed. Then, after forms successfully validate,
    postprocessing is called with updated configuration based on user
    form input.

    Processors can be set up per registration point and are called in the
    order specified. Raising a RegistryValidationError in post-processing
    will rollback any changes performed.
    """
    def preprocess(self, root):
        """
        Called before user forms are generated.

        :param root: registration point root instance
        """
        pass

    def postprocess(self, root):
        """
        Called after user forms are generated and processed. New values
        have already been saved into `instance` registry. Raising a
        RegistryValidationError will rollback any changes performed and
        will stop any further processing.

        :param root: registration point root instance
        """
        pass
