import pkgutil

from logilab import astng
from logilab.astng import builder

from pylint import checkers, interfaces

from DjangoLint import AstCheckers
from DjangoLint.AstCheckers import utils


class DynamicClass(astng.Class):
    def has_dynamic_getattr(self, context=None):
        return True


def is_model(node, **kwargs):
    return utils.is_model(node, **kwargs) or utils.nodeisinstance(node, ('polymorphic.polymorphic_model.PolymorphicModel',), **kwargs)


def is_field(node, **kwargs):
    return utils.nodeisinstance(node, ('django.db.models.fields.Field',), **kwargs)


class NodewatcherChecker(checkers.BaseChecker):
    __implements__ = interfaces.IASTNGChecker

    name = 'custom'
    msgs = {
        'I9999': (
            "Dummy to modify AST.",
            'dummy',
            "Used just to be able to modify AST.",
        ),
    }
    options = ()
    priority = -1 # so that our checker is executed before others

    def __init__(self, linter=None):
        super(NodewatcherChecker, self).__init__(linter)

        query_filename = pkgutil.get_loader('django').filename + '/db/models/query.py'
        query = builder.ASTNGBuilder(astng.MANAGER).file_build(query_filename)
        queryset = query.locals['QuerySet'][0]
        queryset.locals['regpoint'] = [DynamicClass('RegpointAttribute', None)]
        self._queryset = [astng.Instance(queryset)]

        options_filename = pkgutil.get_loader('django').filename + '/db/models/options.py'
        options = builder.ASTNGBuilder(astng.MANAGER).file_build(options_filename)
        self._options = [astng.Instance(options.locals['Options'][0])]

        models = builder.ASTNGBuilder(astng.MANAGER).file_build('nodewatcher/core/registry/models.py')
        self._registry_item_base = models.locals['RegistryItemBase']

    def visit_getattr(self, node):
        try:
            inferred = list(node.expr.infer())[0].frame()
        except astng.InferenceError:
            return
        except AttributeError:
            return
        except IndexError:
            return

        # Whenever somebody wants to access a *RegistryItem class, we create a dummy class for it
        # *RegistryItem classes are dynamically created so we cannot really check them statically
        if node.attrname.endswith('RegistryItem'):
            inferred.locals[node.attrname] = self._registry_item_base

        # Capabilities are generates in the metaclass dynamically
        class_name = '%s.%s' % (inferred.root().name, inferred.name)
        if class_name == 'nodewatcher.core.generator.cgm.protocols.IEEE80211N':
            inferred.locals[node.attrname] = [astng.Instance(DynamicClass('CapabilityAttribute', None))] # TODO: Can we do something better?

        # We do the same for accessing Field attributes, which are just descriptors for dynamic values
        if is_field(inferred):
            inferred.locals[node.attrname] = [DynamicClass('FieldAttribute', None)] # TODO: Can we do something better?

        # For some reason not all classes pass the visit_class visitor below, so we add Django ORM dynamic attributes
        if node.attrname == 'DoesNotExist' and is_model(inferred):
            try:
                inferred.getattr('DoesNotExist')
            except astng.NotFoundError:
                inferred.locals['DoesNotExist'] = [astng.Class('DoesNotExist', None)] # TODO: Should be probably django.core.exceptions.ObjectDoesNotExist
        if node.attrname == 'objects' and is_model(inferred):
            try:
                inferred.getattr('objects')
            except astng.NotFoundError:
                inferred.locals['objects'] = self._queryset
        if node.attrname == '_meta' and is_model(inferred):
            try:
                inferred.getattr('_meta')
            except astng.NotFoundError:
                inferred.locals['_meta'] = self._options

    def visit_class(self, node):
        if is_model(node):
            # We add Django ORM dynamic attributes
            node.locals['DoesNotExist'] = [astng.Class('DoesNotExist', None)] # TODO: Should be probably django.core.exceptions.ObjectDoesNotExist
            node.locals['objects'] = self._queryset
            node.locals['_meta'] = self._options

            # Pool model is self-referencing
            class_name = '%s.%s' % (node.root().name, node.name)
            if class_name == 'nodewatcher.core.allocation.models.PoolBase':
                node.locals['children'] = self._queryset

    def visit_callfunc(self, node):
        if isinstance(node.func, astng.Getattr) and getattr(node.func, 'attrname', None) == 'create_point':
            try:
                inferred = list(node.func.expr.infer())[0].frame()
            except astng.InferenceError:
                return
            except AttributeError:
                return
            except IndexError:
                return

            if not inferred.name == 'nodewatcher.core.registry.registration':
                return

            # So it is a call to registration.create_point

            # TODO: Hardcoded, should also check node.starargs and node.kwargs
            model, namespace = node.args

            model = list(model.infer())[0]
            model.locals[namespace.value] = [astng.Instance(DynamicClass('RegistrationPointAttribute', None))] # TODO: Can we do something better?


def register(linter):
    AstCheckers.register(linter)
    linter.register_checker(NodewatcherChecker(linter))
