class FrontendComponentException(Exception):
    pass


class InvalidFrontendComponent(FrontendComponentException):
    pass


class FrontendComponentAlreadyRegistered(FrontendComponentException):
    pass


class FrontendComponentNotRegistered(FrontendComponentException):
    pass


class FrontendComponentNoneRegistered(FrontendComponentException):
    pass


class FrontendComponentDependencyNotRegistered(FrontendComponentException):
    pass


class FrontendComponentWithoutMain(FrontendComponentException):
    pass


class MenuEntryException(Exception):
    pass


class InvalidMenuEntry(MenuEntryException):
    pass


class MenuException(Exception):
    pass


class InvalidMenu(MenuException):
    pass


class MenuAlreadyRegistered(MenuException):
    pass


class MenuNotRegistered(MenuException):
    pass
