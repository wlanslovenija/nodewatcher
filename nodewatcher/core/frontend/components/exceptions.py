class FrontendComponentException(Exception):
    pass

class FrontendComponentAlreadyRegistered(FrontendComponentException):
    pass

class FrontendComponentNotRegistered(FrontendComponentException):
    pass

class FrontendComponentNoneRegistered(FrontendComponentException):
    pass

class FrontendComponentHasInvalidBase(FrontendComponentException):
    pass

class FrontendComponentHasInvalidName(FrontendComponentException):
    pass

class FrontendComponentDependencyNotRegistered(FrontendComponentException):
    pass

class FrontendComponentWithoutMain(FrontendComponentException):
    pass

class MenuEntryException(Exception):
    pass

class MenuEntryHasInvalidLabel(MenuEntryException):
    pass

class MenuException(Exception):
    pass

class MenuHasInvalidBase(FrontendComponentException):
    pass

class MenuHasInvalidName(MenuException):
    pass
