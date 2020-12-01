# -*- coding: utf-8 -*-

import inspect
import six
import pytz

from .exceptions import (
    QueryEmpty,
    QueryExpressionError,
    QueryMissingField,
    QueryMultipleExpressions,
    QueryTypeError,
)


class QueryBuilder(object):
    """Query builder - for constructing advanced ServiceNow queries"""

    def __init__(self):
        self._query = []
        self.current_field = None
        self.c_oper = None
        self.l_oper = None

    def field(self, field):
        """Sets the field to operate on

        :param field: field (str) to operate on
        """

        self.current_field = field
        return self

    def order_descending(self):
        """Sets ordering of field descending"""

        self._query.append("ORDERBYDESC{0}".format(self.current_field))
        self.c_oper = inspect.currentframe().f_back.f_code.co_name
        return self

    def order_ascending(self):
        """Sets ordering of field ascending"""

        self._query.append("ORDERBY{0}".format(self.current_field))
        self.c_oper = inspect.currentframe().f_back.f_code.co_name
        return self

    def starts_with(self, starts_with):
        """Adds new `STARTSWITH` condition

        :param starts_with: Match field starting with the provided value
        """

        return self._add_condition("STARTSWITH", starts_with, types=[str])

    def ends_with(self, ends_with):
        """Adds new `ENDSWITH` condition

        :param ends_with: Match field ending with the provided value
        """

        return self._add_condition("ENDSWITH", ends_with, types=[str])

    def contains(self, contains):
        """Adds new `LIKE` condition

        :param contains: Match field containing the provided value
        """

        return self._add_condition("LIKE", contains, types=[str])

    def not_contains(self, not_contains):
        """Adds new `NOT LIKE` condition

        :param not_contains: Match field not containing the provided value
        """

        return self._add_condition("NOT LIKE", not_contains, types=[str])

    def is_empty(self):
        """Adds new `ISEMPTY` condition"""

        return self._add_condition("ISEMPTY", "", types=[str, int])

    def is_not_empty(self):
        """Adds new `ISNOTEMPTY` condition"""

        return self._add_condition("ISNOTEMPTY", "", types=[str, int])

    def equals(self, data):
        """Adds new `IN` or `=` condition depending on if a list or string was provided

        :param data: string or list of values
        :raise:
            - QueryTypeError: if `data` is of an unexpected type
        """

        if isinstance(data, six.string_types):
            return self._add_condition("=", data, types=[int, str])
        elif isinstance(data, list):
            return self._add_condition("IN", ",".join(map(str, data)), types=[str])

        raise QueryTypeError(
            "Expected value of type `str` or `list`, not %s" % type(data)
        )

    def not_equals(self, data):
        """Adds new `NOT IN` or `!=` condition depending on if a list or string was provided

        :param data: string or list of values
        :raise:
            - QueryTypeError: if `data` is of an unexpected type
        """

        if isinstance(data, six.string_types):
            return self._add_condition("!=", data, types=[int, str])
        elif isinstance(data, list):
            return self._add_condition("NOT IN", ",".join(data), types=[str])

        raise QueryTypeError(
            "Expected value of type `str` or `list`, not %s" % type(data)
        )

    def greater_than(self, greater_than):
        """Adds new `>` condition

        :param greater_than: str or datetime compatible object (naive UTC datetime or tz-aware datetime)
        :raise:
            - QueryTypeError: if `greater_than` is of an unexpected type
        """

        if hasattr(greater_than, "strftime"):
            greater_than = datetime_as_utc(greater_than).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(greater_than, six.string_types):
            raise QueryTypeError(
                "Expected value of type `int` or instance of `datetime`, not %s"
                % type(greater_than)
            )

        return self._add_condition(">", greater_than, types=[int, str])

    def greater_than_or_equal(self, greater_than):
        """Adds new `>=` condition

        :param greater_than: str or datetime compatible object (naive UTC datetime or tz-aware datetime)
        :raise:
            - QueryTypeError: if `greater_than` is of an unexpected type
        """

        if hasattr(greater_than, "strftime"):
            greater_than = datetime_as_utc(greater_than).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(greater_than, six.string_types):
            raise QueryTypeError(
                "Expected value of type `int` or instance of `datetime`, not %s"
                % type(greater_than)
            )

        return self._add_condition(">=", greater_than, types=[int, str])

    def less_than(self, less_than):
        """Adds new `<` condition

        :param less_than: str or datetime compatible object (naive UTC datetime or tz-aware datetime)
        :raise:
            - QueryTypeError: if `less_than` is of an unexpected type
        """

        if hasattr(less_than, "strftime"):
            less_than = datetime_as_utc(less_than).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(less_than, six.string_types):
            raise QueryTypeError(
                "Expected value of type `int` or instance of `datetime`, not %s"
                % type(less_than)
            )

        return self._add_condition("<", less_than, types=[int, str])

    def less_than_or_equal(self, less_than):
        """Adds new `<=` condition

        :param less_than: str or datetime compatible object (naive UTC datetime or tz-aware datetime)
        :raise:
            - QueryTypeError: if `less_than` is of an unexpected type
        """

        if hasattr(less_than, "strftime"):
            less_than = datetime_as_utc(less_than).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(less_than, six.string_types):
            raise QueryTypeError(
                "Expected value of type `int` or instance of `datetime`, not %s"
                % type(less_than)
            )

        return self._add_condition("<=", less_than, types=[int, str])

    def between(self, start, end):
        """Adds new `BETWEEN` condition

        :param start: int or datetime  compatible object (in SNOW user's timezone)
        :param end: int or datetime compatible object (in SNOW user's timezone)
        :raise:
            - QueryTypeError: if start or end arguments is of an invalid type
        """

        if hasattr(start, "strftime") and hasattr(end, "strftime"):
            dt_between = (
                'javascript:gs.dateGenerate("%(start)s")'
                "@"
                'javascript:gs.dateGenerate("%(end)s")'
            ) % {
                "start": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end": end.strftime("%Y-%m-%d %H:%M:%S"),
            }
        elif isinstance(start, int) and isinstance(end, int):
            dt_between = "%d@%d" % (start, end)
        else:
            raise QueryTypeError(
                "Expected `start` and `end` of type `int` "
                "or instance of `datetime`, not %s and %s" % (type(start), type(end))
            )

        return self._add_condition("BETWEEN", dt_between, types=[str])

    def AND(self):
        """Adds an and-operator"""
        return self._add_logical_operator("^")

    def OR(self):
        """Adds an or-operator"""
        return self._add_logical_operator("^OR")

    def NQ(self):
        """Adds a NQ-operator (new query)"""
        return self._add_logical_operator("^NQ")

    def _add_condition(self, operator, operand, types):
        """Appends condition to self._query after performing validation

        :param operator: operator (str)
        :param operand: operand
        :param types: allowed types
        :raise:
            - QueryMissingField: if a field hasn't been set
            - QueryMultipleExpressions: if a condition already has been set
            - QueryTypeError: if the value is of an unexpected type
        """

        if not self.current_field:
            raise QueryMissingField("Conditions requires a field()")

        elif not type(operand) in types:
            caller = inspect.currentframe().f_back.f_code.co_name
            raise QueryTypeError(
                "Invalid type passed to %s() , expected: %s" % (caller, types)
            )

        elif self.c_oper:
            raise QueryMultipleExpressions("Expected logical operator after expression")

        self.c_oper = inspect.currentframe().f_back.f_code.co_name

        self._query.append(
            "%(current_field)s%(operator)s%(operand)s"
            % {
                "current_field": self.current_field,
                "operator": operator,
                "operand": operand,
            }
        )

        return self

    def _add_logical_operator(self, operator):
        """Adds a logical operator in query

        :param operator: logical operator (str)
        :raise:
            - QueryExpressionError: if a expression hasn't been set
        """

        if not self.c_oper:
            raise QueryExpressionError(
                "Logical operators must be preceded by an expression"
            )

        self.current_field = None
        self.c_oper = None

        self.l_oper = inspect.currentframe().f_back.f_code.co_name
        self._query.append(operator)
        return self

    def __str__(self):
        """String representation of the query object

        :raise:
            - QueryEmpty: if there's no conditions defined
            - QueryMissingField: if field() hasn't been set
            - QueryExpressionError: if a expression hasn't been set

        :return:
            - String-type query
        """

        if len(self._query) == 0:
            raise QueryEmpty("At least one condition is required")
        elif self.current_field is None:
            raise QueryMissingField("Logical operator expects a field()")
        elif self.c_oper is None:
            raise QueryExpressionError("field() expects an expression")

        return str().join(self._query)


def datetime_as_utc(date_obj):
    if date_obj.tzinfo is not None and date_obj.tzinfo.utcoffset(date_obj) is not None:
        return date_obj.astimezone(pytz.UTC)
    return date_obj
