# -*- coding: utf-8 -*-

import inspect
from pysnow.exceptions import (QueryEmpty,
                               QueryExpressionError,
                               QueryMissingField,
                               QueryMultipleExpressions,
                               QueryTypeError)


class QueryBuilder(object):
    def __init__(self):
        """Query builder - used for building complex queries"""
        self._query = []
        self.current_field = None
        self.c_oper = None
        self.l_oper = None

    def AND(self):
        """And operator"""
        return self._add_logical_operator('^')

    def OR(self):
        """OR operator"""
        return self._add_logical_operator('^OR')

    def NQ(self):
        """NQ (new query) operator"""
        return self._add_logical_operator('^NQ')

    def field(self, field):
        """ Sets the field to operate on

        :param field: field (str) to operate on
        :return: self
        """
        self.current_field = field
        return self

    def starts_with(self, value):
        """Query records with the given field starting with the value specified"""
        return self._add_condition('STARTSWITH', value, types=[str])

    def ends_with(self, value):
        """Query records with the given field ending with the value specified"""
        return self._add_condition('ENDSWITH', value, types=[str])

    def contains(self, value):
        """Query records with the given field containing the value specified"""
        return self._add_condition('LIKE', value, types=[str])

    def not_contains(self, value):
        """Query records with the given field not containing the value specified"""
        return self._add_condition('NOTLIKE', value, types=[str])

    def is_empty(self):
        """Query records with the given field empty"""
        return self._add_condition('ISEMPTY', '', types=[str, int])

    def equals(self, data):
        """
        Query records with the given field equalling either:
        - the value passed (str)
        - any of the values passed (list)
        """

        if isinstance(data, str):
            return self._add_condition('=', data, types=[int, str])
        elif isinstance(data, list):
            return self._add_condition('IN', ",".join(map(str, data)), types=[str])

        raise QueryTypeError('Expected value of type `str` or `list`, not %s' % type(data))

    def not_equals(self, value):
        """
        Query records with the given field not equalling:
        - the value specified
        - any of the values specified (list)
        """

        if isinstance(value, str):
            return self._add_condition('!=', value, types=[int, str])
        elif isinstance(value, list):
            return self._add_condition('NOT IN', ",".join(value), types=[str])

        raise QueryTypeError('Expected value of type `str` or `list`, not %s' % type(value))

    def greater_than(self, value):
        """Query records with the given field greater than the value specified"""
        if hasattr(value, 'strftime'):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, str):
            raise QueryTypeError('Expected value of type `int` or instance of `datetime`, not %s' % type(value))

        return self._add_condition('>', value, types=[int, str])

    def less_than(self, value):
        """Query records with the given field less than the value specified"""
        if hasattr(value, 'strftime'):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, str):
            raise QueryTypeError('Expected value of type `int` or instance of `datetime`, not %s' % type(value))

        return self._add_condition('<', value, types=[int, str])

    def between(self, start, end):
        """Query records in a start and end range

        :param start: `int` or `datetime` object
        :param end: `int` or `datetime` object
        :raise:
            :QueryTypeError: if start or end arguments is of an invalid type
        :return: self
        """
        if hasattr(start, 'strftime') and hasattr(end, 'strftime'):
            dt_between = (
              'javascript:gs.dateGenerate("%(start)s")'
              "@"
              'javascript:gs.dateGenerate("%(end)s")'
            ) % {
              'start': start.strftime('%Y-%m-%d %H:%M:%S'),
              'end': end.strftime('%Y-%m-%d %H:%M:%S')
            }
        elif isinstance(start, int) and isinstance(end, int):
            dt_between = '%d@%d' % (start, end)
        else:
            raise QueryTypeError("Expected `start` and `end` of type `int` "
                                 "or instance of `datetime`, not %s and %s" % (type(start), type(end)))

        return self._add_condition('BETWEEN', dt_between, types=[str])

    def _add_condition(self, operator, value, types):
        """ Appends condition to self._query after performing validation

        :param operator: operator (str)
        :param value: value / operand
        :param types: allowed types
        :raise:
            :QueryMissingField: if a field hasn't been set
            :QueryMultipleExpressions: if a condition already has been set
            :QueryTypeError: if the value is of an unexpected type
        :return: self
        """
        if not self.current_field:
            raise QueryMissingField("Expressions requires a field()")
        elif not type(value) in types:
            caller = inspect.currentframe().f_back.f_code.co_name
            raise QueryTypeError("Invalid type passed to %s() , expected: %s" % (caller, types))
        elif self.c_oper:
            raise QueryMultipleExpressions("Expected logical operator after expression")

        self.c_oper = inspect.currentframe().f_back.f_code.co_name
        self._query.append("%(current_field)s%(operator)s%(value)s" % {
                               'current_field': self.current_field,
                               'operator': operator,
                               'value': value})
        return self

    def _add_logical_operator(self, operator):
        """ Adds a logical operator between conditions in query

        :param operator: logical operator (str)
        :raise:
            :QueryExpressionError: if a expression hasn't been set
        :return: self
        """
        if not self.c_oper:
            raise QueryExpressionError("Logical operators must be preceded by an expression")

        self.current_field = None
        self.c_oper = None

        self.l_oper = inspect.currentframe().f_back.f_code.co_name
        self._query.append(operator)
        return self

    def __str__(self):
        """ String representation of the query object
        :raise:
            :QueryEmpty: if there's no conditions defined
            :QueryMissingField: if field() hasn't been set
            :QueryExpressionError: if a expression hasn't been set
        :return: Query string
        """
        if len(self._query) == 0:
            raise QueryEmpty("At least one condition is required")
        elif self.current_field is None:
            raise QueryMissingField("Logical operator expects a field()")
        elif self.c_oper is None:
            raise QueryExpressionError("field() expects an expression")

        return str().join(self._query)


# For backwards compatibility
class Query(QueryBuilder):
    pass
