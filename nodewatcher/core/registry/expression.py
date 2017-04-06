from grako import exceptions

from django.db.models import constants, query
from django.contrib.gis import measure

from . import expression_parser


class LookupExpression(object):
    """
    Describes a registry lookup expression.
    """

    registration_point = None
    registry_id = None
    constraints = None
    field = None

    def __init__(self, registration_point=None, registry_id=None, field=None, constraints=None):
        self.registration_point = registration_point
        self.registry_id = registry_id
        self.field = field
        self.constraints = constraints

    def apply_constraints(self, queryset):
        """
        Applies all constraints contained in the lookup expression.

        :param queryset: Queryset to apply the constraints to
        :return: Queryset with all constraints applied
        """

        for constraint in self.constraints:
            queryset = constraint.apply(queryset)

        return queryset

    @property
    def name(self):
        """
        Returns an identifier suitable for representing this lookup expression
        in an attribute.
        """

        return '%s%s%s' % (
            self.registration_point.replace('.', '_') if self.registration_point else '',
            self.registry_id.replace('.', '_') if self.registry_id else '',
            '_'.join(self.field or []),
        )

    @classmethod
    def from_ast(cls, ast):
        return LookupExpression(
            registration_point=ast.registration_point,
            registry_id='.'.join(ast.registry_id),
            field=ast.field,
            constraints=ast.constraints,
        )

    def __repr__(self):
        return '<LookupExpression registration_point=\'%s\' registry_id=\'%s\' constraints=\'%s\' field=\'%s\'>' % (
            self.registration_point,
            self.registry_id,
            self.constraints,
            '.'.join(self.field) if self.field else ''
        )


class Lookup(object):
    def __init__(self, operator, field, value):
        self.operator = operator
        self.field = constants.LOOKUP_SEP.join(field)
        self.value = value

    def apply(self, queryset):
        return queryset.filter(**{self.field: self.value})

    def __repr__(self):
        return '%s %s %s' % (self.field, self.operator, self.value)


class LookupExpressionSemantics(expression_parser.ExpressionSemantics):
    def constraint(self, ast):
        return Lookup(ast.operator, ast.field, ast.value)

    def INTEGER(self, ast):
        return int(ast)

    def FLOAT(self, ast):
        return float(ast)

    def STRING(self, ast):
        return ''.join(ast)

    def TUPLE(self, ast):
        return tuple(ast)

    def distance(self, ast):
        return measure.Distance(m=ast)

    def area(self, ast):
        return measure.Area(sq_m=ast)


class LookupExpressionParser(object):
    """
    A parser for registry lookup expressions.
    """

    def __init__(self):
        self._parser = expression_parser.ExpressionParser()
        self._semantics = LookupExpressionSemantics()

    def parse(self, expression):
        try:
            ast = self._parser.parse(expression, rule_name='lookup', semantics=self._semantics)
        except exceptions.FailedParse:
            raise ValueError('Invalid registry lookup expression: %s' % expression)

        return LookupExpression.from_ast(ast)


class FilterExpression(object):
    """
    Describes a registry filter expression based on a Q-expression.
    """

    filter_q = None
    ensure_distinct = False

    def __init__(self, filter_q, ensure_distinct=False):
        self.filter_q = filter_q
        self.ensure_distinct = ensure_distinct

    def apply(self, queryset):
        """
        Applies this filter expression to a queryset.

        :param queryset: Queryset to apply the filter expression to
        :return Queryset with filter expression applied
        """

        if hasattr(queryset, 'raw_filter'):
            # Use raw filter for registry querysets.
            queryset = queryset.raw_filter(self.filter_q)
        else:
            queryset = queryset.filter(self.filter_q)

        if self.ensure_distinct:
            queryset = queryset.distinct()
        return queryset

    def __repr__(self):
        return '<FilterExpression: %s>' % self.filter_q


class FilterExpressionSemantics(LookupExpressionSemantics):
    def __init__(self, root, field=None, disallow_sensitive=False):
        self.root = root
        self.field = field
        self.disallow_sensitive = disallow_sensitive

    def filter_expression_prec1(self, ast):
        lhs, rhs, op = ast['lhs'], ast['rhs'], ast['op']

        if op is None:
            return rhs
        if not isinstance(lhs, list):
            lhs = [lhs]
        if not isinstance(op, list):
            op = [op]

        expressions = lhs + [rhs]
        active = expressions[0]
        for expression, operator in zip(expressions[1:], op):
            q = active.filter_q
            ensure_distinct = active.ensure_distinct or expression.ensure_distinct

            if operator == ',':
                q = q & expression.filter_q
            elif operator == '|':
                q = q | expression.filter_q
            else:
                raise ValueError('Unsupported operator: %s' % op)

            active = FilterExpression(
                q,
                ensure_distinct=ensure_distinct
            )

        return active

    def filter_expression_prec2(self, ast):
        expression, op = ast['expression'], ast['op']

        if op is None:
            return expression
        elif op == '!':
            return FilterExpression(~expression.filter_q, ensure_distinct=expression.ensure_distinct)
        else:
            raise ValueError('Unsupported operator: %s' % op)

    def equality_lookup(self, ast):
        from . import lookup

        lookup_expression = LookupExpression.from_ast(ast['field'])
        try:
            selector, _, ensure_distinct = lookup.selector_for_lookup(
                self.root,
                lookup_expression,
                disallow_sensitive=self.disallow_sensitive
            )

            if self.field is not None:
                selector = self.field.name + constants.LOOKUP_SEP + selector
        except TypeError:
            # Disallowed field.
            return FilterExpression(query.Q())

        return FilterExpression(query.Q(**{selector: ast['value']}), ensure_distinct=ensure_distinct)


class FilterExpressionParser(object):
    """
    A parser for registry filter expressions.
    """

    def __init__(self, root, field=None, disallow_sensitive=False):
        self._parser = expression_parser.ExpressionParser()
        self._semantics = FilterExpressionSemantics(
            root,
            field=field,
            disallow_sensitive=disallow_sensitive
        )

    def parse(self, expression):
        try:
            return self._parser.parse(expression, rule_name='filter', semantics=self._semantics)
        except exceptions.FailedParse:
            raise ValueError('Invalid registry filter expression: %s' % expression)
