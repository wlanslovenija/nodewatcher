import pkgutil

from docutils import core, nodes

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


class DocVisitor(nodes.SparseNodeVisitor):
    def __init__(self, document, checker, pynode):
        nodes.SparseNodeVisitor.__init__(self, document)
        self.checker = checker
        self.pynode = pynode
        self.inside_list = False
        self.field_list = []

    def visit_list_item(self, node):
        self.inside_list = True

    def depart_list_item(self, node):
        self.inside_list = False

    def visit_field_list(self, node):
        self.field_list = []

    def depart_field_list(self, node):
        if not hasattr(self.pynode, 'argnames'):
            return
        argnames = self.pynode.argnames()
        if self.pynode.is_method() and len(argnames) > 0 and argnames[0] == 'self':
            argnames = argnames[1:]
        if self.pynode.is_bound() and len(argnames) > 0 and argnames[0] == 'cls':
            argnames = argnames[1:]
        varargs = False
        for arg in ('kwargs', 'args'):
            if len(argnames) > 0 and argnames[-1] == arg:
                varargs = True
                argnames = argnames[:-1]

        if len(argnames) > len(self.field_list):
            for arg in self.field_list[len(self.field_list):]:
                self.checker.add_message('W9008', args=arg, node=self.pynode, line=self.pynode.fromlineno)

        if not varargs and len(self.field_list) > len(argnames):
            for arg in self.field_list[len(argnames):]:
                self.checker.add_message('W9009', args=arg, node=self.pynode, line=self.pynode.fromlineno)

        for arg, field in zip(argnames, self.field_list):
            if arg != field:
                self.checker.add_message('W9010', args=(arg, field), node=self.pynode, line=self.pynode.fromlineno)

    def visit_field(self, node):
        self.inside_list = True

    def depart_field(self, node):
        self.inside_list = False

    def visit_field_name(self, node):
        field_name = node.astext()
        tokens = field_name.split(' ')

        if tokens[0] not in ('param', 'type', 'raise', 'return', 'rtype'):
            self.checker.add_message('W9006', args=tokens[0], node=self.pynode, line=self.pynode.fromlineno)
            return

        if tokens[0] != 'param':
            return

        if len(tokens) != 2:
            self.checker.add_message('W9007', args=field_name, node=self.pynode, line=self.pynode.fromlineno)
            return

        self.field_list.append(tokens[1])

    def visit_paragraph(self, node):
        if self.inside_list:
            return

        paragraph = node.astext().strip()
        if not paragraph:
            return

        if paragraph[-1] not in '.!?':
            self.checker.add_message('W9001', node=self.pynode, line=self.pynode.fromlineno)

class DocStringChecker(checkers.BaseChecker):
    __implements__ = interfaces.IASTNGChecker

    name = 'docstring'
    priority = -1
    msgs = {
        'W9001': (
            "Doc string does not end with '.' period",
            'docstring-missing-period',
            "Used when a doc string does not end with a period.",
        ),
        'W9002': (
            "Triple quotes",
            'docstring-triple-quotes',
            "Used when doc string does not use \"\"\".",
        ),
        'W9003': (
            "Invalid docstring start or end",
            'docstring-start-or-end',
            "Used when doc string does not start or end with \"\"\" on its own line.",
        ),
        'W9004': (
            "Missing blank line after doc string",
            'docstring-missing blank line',
            "Used when doc string is missing a blank line afterwards.",
        ),
        'W9005': (
            "Doxygen syntax detected: %s",
            'docstring-doxygen',
            "Used when doc string contains Doxygen syntax.",
        ),
        'W9006': (
            "Invalid reST field type: %s",
            'docstring-invalid-field-type',
            "Used when doc string contains invalid reSt field type.",
        ),
        'W9007': (
            "Invalid reST field content: %s",
            'docstring-invalid-field-content',
            "Used when doc string contains invalid reSt field content.",
        ),
        'W9008': (
            "Argument not documented: %s",
            'docstring-args-not-documented',
            "Used when function or method argument is not documented in the doc string.",
        ),
        'W9009': (
            "Unknown argument documented: %s",
            'docstring-args-unknown',
            "Used when function or method argument is documented in the doc string but it is unknown.",
        ),
        'W9010': (
            "Documented argument name mismatch: %s, %s",
            'docstring-args-mismatch',
            "Used when function or method argument is documented in the doc string but does not match the name.",
        ),
    }
    options = ()

    def visit_function(self, node):
        if node.doc:
            self._check_doc_string(node)

    def visit_module(self, node):
        if node.doc:
            self._check_doc_string(node)

    def visit_class(self, node):
        if node.doc:
            self._check_doc_string(node)

    def _check_doc_string(self, node):
        self.is_rest(node)
        self.is_doxygen(node)

    def is_doxygen(self, node):
        for doxy in ('@param', '@return'):
            if doxy in node.doc:
                self.add_message('W9005', args=doxy, node=node, line=node.fromlineno)

    def is_rest(self, node):
        document = core.publish_doctree(source=node.doc)
        document.walkabout(DocVisitor(document, self, node))


class NodewatcherChecker(checkers.BaseChecker):
    __implements__ = interfaces.IASTNGChecker

    name = 'custom'
    msgs = {
        'I9999': (
            "Dummy to modify AST",
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
        # For registration.create_point calls add target registration point to the model
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
    linter.register_checker(DocStringChecker(linter))
    linter.register_checker(NodewatcherChecker(linter))
