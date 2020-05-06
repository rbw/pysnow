import inspect
import six
import pytz
from datetime import datetime

from .enums import (
    Boolean,
    Equality,
    DateTimeOn,
    Order,
)
from .exceptions import QueryTypeError


class Term(object):
    @staticmethod
    def wrap_constant(value, types, list_type=False):
        if list_type:
            if isinstance(value, (list, tuple)):
                if all(type(x) in types for x in value):
                    return ListValueWrapper(value, types)
                else:
                    caller = inspect.currentframe().f_back.f_code.co_name
                    raise QueryTypeError(
                        "Expected value to be a list of type %s, not %s"
                        % (types, type(value))
                    )
            else:
                caller = inspect.currentframe().f_back.f_code.co_name
                raise QueryTypeError(
                    "Invalid type passed to %s() , expected list or tuple" % (caller)
                )
        elif isinstance(value, ValueWrapper) and (
            value.type_ in types or (value.type_ == list and list_type)
        ):
            return value
        # allow other types than datetime, as long as they have strftime
        elif hasattr(value, "strftime") and datetime in types:
            return DateTimeValueWrapper(value)
        elif not type(value) in types:
            caller = inspect.currentframe().f_back.f_code.co_name
            raise QueryTypeError(
                "Invalid type passed to %s() , expected: %s" % (caller, types)
            )
        elif isinstance(value, int):
            return IntValueWrapper(value)
        elif isinstance(value, str):
            return StringValueWrapper(value)
        else:
            return value

    def eq(self, other):
        return self == other

    def gt(self, other):
        return self > other

    def gte(self, other):
        return self >= other

    def lt(self, other):
        return self < other

    def lte(self, other):
        return self <= other

    def ne(self, other):
        return self != other

    def is_empty(self):
        return IsEmptyCriterion(self)

    def is_not_empty(self):
        return NotEmptyCriterion(self)

    def is_empty_string(self):
        return IsEmptyStringCriterion(self)

    def between(self, lower, upper):
        return BetweenCriterion(
            self,
            self.wrap_constant(lower, types=[int, datetime]),
            self.wrap_constant(upper, types=[int, datetime]),
        )

    def starts_with(self, other):
        return BasicCriterion(
            "STARTSWITH", self, self.wrap_constant(other, types=[str])
        )

    def ends_with(self, other):
        return BasicCriterion("ENDSWITH", self, self.wrap_constant(other, types=[str]))

    def contains(self, other):
        return self.like(other)

    def not_contains(self, other):
        return self.not_like(other)

    def like(self, other):
        return BasicCriterion("LIKE", self, self.wrap_constant(other, types=[str]))

    def not_like(self, other):
        return BasicCriterion("NOT LIKE", self, self.wrap_constant(other, types=[str]))

    def is_in(self, other):
        return BasicCriterion(
            "IN", self, self.wrap_constant(other, types=[int, str], list_type=True)
        )

    def not_in(self, other):
        return BasicCriterion(
            "NOT IN", self, self.wrap_constant(other, types=[int, str], list_type=True)
        )

    def is_anything(self, other):
        return IsAnythingCriterion(self)

    def is_same(self, other):
        return BasicCriterion("SAMEAS", self, self.wrap_constant(other, types=[Field]))

    def is_different(self, other):
        return BasicCriterion("NSAMEAS", self, self.wrap_constant(other, types=[Field]))

    def __eq__(self, other):
        return BasicCriterion(
            Equality.eq, self, self.wrap_constant(other, types=[int, str])
        )

    def __ne__(self, other):
        return BasicCriterion(
            Equality.ne, self, self.wrap_constant(other, types=[int, str])
        )

    def __gt__(self, other):
        return BasicCriterion(
            Equality.gt, self, self.wrap_constant(other, types=[int, datetime])
        )

    def __ge__(self, other):
        return BasicCriterion(
            Equality.gte, self, self.wrap_constant(other, types=[int, datetime])
        )

    def __lt__(self, other):
        return BasicCriterion(
            Equality.lt, self, self.wrap_constant(other, types=[int, datetime])
        )

    def __le__(self, other):
        return BasicCriterion(
            Equality.lte, self, self.wrap_constant(other, types=[int, datetime])
        )

    # DateTime only
    def on(self, other):
        return DateTimeOnCriterion(
            self, self.wrap_constant(other, types=[datetime, DateTimeOn])
        )

    def not_on(self, other):
        return DateTimeNotOnCriterion(
            self, self.wrap_constant(other, types=[datetime, DateTimeOn])
        )

    # End DateTime only

    def order(self, direction):
        return OrderCriterion(self, direction)

    def __str__(self):
        return self.get_query()

    def get_query(self, **kwargs):
        raise NotImplementedError()


class Criterion(Term):
    def AND(self, other):
        return self & other

    def OR(self, other):
        return self | other

    def NQ(self, other):
        return self ^ other

    def __and__(self, other):
        return BasicCriterion(Boolean.and_, self, other)

    def __or__(self, other):
        return BasicCriterion(Boolean.or_, self, other)

    def __xor__(self, other):
        """
            While not really an XOR operation, this allows us to use Python's bitwise operators
        """
        return BasicCriterion(Boolean.nq_, self, other)

    @staticmethod
    def any(terms=()):
        crit = EmptyCriterion()

        for term in terms:
            crit |= term

        return crit

    @staticmethod
    def all(terms=()):
        crit = EmptyCriterion()

        for term in terms:
            crit &= term

        return crit

    def get_query(self, **kwargs):
        raise NotImplementedError()


class EmptyCriterion(object):
    def __and__(self, other):
        return other

    def __or__(self, other):
        return other

    def __xor__(self, other):
        return other


class BasicCriterion(Criterion):
    def __init__(self, comparator, left, right):
        """
        A wrapper for a basic criterion such as equality or inequality.
        This wraps three parts, a left and right term and a comparator which
        defines the type of comparison.


        :param comparator:
            Type: Comparator
            This defines the type of comparison, such as {quote}={quote} or
            {quote}>{quote}.
        :param left:
            The term on the left side of the expression.
        :param right:
            The term on the right side of the expression.
        """
        super(BasicCriterion, self).__init__()
        self.comparator = comparator
        self.left = left
        self.right = right

    def get_query(self, **kwargs):
        return "{left}{comparator}{right}".format(
            comparator=getattr(self.comparator, "value", self.comparator),
            left=self.left.get_query(**kwargs),
            right=self.right.get_query(**kwargs),
        )


class IsEmptyCriterion(Criterion):
    def __init__(self, term):
        super(IsEmptyCriterion, self).__init__()
        self.term = term

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        return "{}ISEMPTY".format(term)


class NotEmptyCriterion(Criterion):
    def __init__(self, term):
        super(NotEmptyCriterion, self).__init__()
        self.term = term

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        return "{}ISNOTEMPTY".format(term)


class IsAnythingCriterion(Criterion):
    def __init__(self, term):
        super(IsAnythingCriterion, self).__init__()
        self.term = term

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        return "{}ANYTHING".format(term)


class IsEmptyStringCriterion(Criterion):
    def __init__(self, term):
        super(IsEmptyStringCriterion, self).__init__()
        self.term = term

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        return "{}EMPTYSTRING".format(term)


class BetweenCriterion(Criterion):
    def __init__(self, term, start, end):
        super(BetweenCriterion, self).__init__()
        self.term = term
        self.start = start
        self.end = end

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        start = self.start.get_query(**kwargs)
        end = self.end.get_query(**kwargs)

        if isinstance(self.start, DateTimeValueWrapper) and isinstance(
            self.end, DateTimeValueWrapper
        ):
            dt_between = "%s@%s" % (start, end)
        elif isinstance(self.start, IntValueWrapper) and isinstance(
            self.end, IntValueWrapper
        ):
            dt_between = "%d@%d" % (start, end)
        else:
            raise QueryTypeError(
                "Expected both `start` and `end` of type `int` "
                "or instance of `datetime`, not %s and %s" % (type(start), type(end))
            )

        return "{}BETWEEN{}".format(term, dt_between)


class DateTimeOnCriterion(Criterion):
    def __init__(self, term, criteria):
        super(DateTimeOnCriterion, self).__init__()
        self.term = term
        self.criteria = criteria

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        if isinstance(self.criteria, DateTimeOn):
            return "{term}ON{criteria}".format(term=term, criteria=self.criteria.value)
        else:
            return "{term}ONcustom@{start}@{end}".format(
                term=term,
                start=self.criteria.get_query(date_only=True, extra_param="start"),
                end=self.criteria.get_query(date_only=True, extra_param="end"),
            )


class DateTimeNotOnCriterion(Criterion):
    def __init__(self, term, criteria):
        super(DateTimeNotOnCriterion, self).__init__()
        self.term = term
        self.criteria = criteria

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        if isinstance(self.criteria, DateTimeOn):
            return "{term}NOTON{criteria}".format(
                term=term, criteria=self.criteria.value
            )
        else:
            return "{term}NOTONcustom@{start}@{end}".format(
                term=term,
                start=self.criteria.get_query(date_only=True, extra_param="start"),
                end=self.criteria.get_query(date_only=True, extra_param="end"),
            )


class OrderCriterion(Criterion):
    def __init__(self, term, direction):
        super(OrderCriterion, self).__init__()
        self.term = term
        self.direction = direction

    def get_query(self, **kwargs):
        term = self.term.get_query(**kwargs)
        if self.direction == Order.asc or (
            isinstance(self.direction, six.string_types)
            and self.direction.lower() == "asc"
        ):
            return "ORDERBY{term}".format(term=term)
        elif self.direction == Order.desc or (
            isinstance(self.direction, six.string_types)
            and self.direction.lower() == "desc"
        ):
            return "ORDERBYDESC{term}".format(term=term)
        else:
            raise QueryTypeError(
                "Expected 'asc', 'desc', or an instance of Order, not %s"
                % (type(self.direction))
            )


class ValueWrapper(Term):
    def __init__(self, type_):
        self.type_ = type_


class IntValueWrapper(ValueWrapper):
    def __init__(self, value):
        super(IntValueWrapper, self).__init__(int)
        self.value = value

    def get_query(self, **kwargs):
        if isinstance(self.value, int):
            return self.value
        else:
            raise QueryTypeError(
                "Expected value to be an instance of `int`, not %s" % type(self.value)
            )


class StringValueWrapper(ValueWrapper):
    def __init__(self, value):
        super(StringValueWrapper, self).__init__(str)
        self.value = value

    def get_query(self, **kwargs):
        if isinstance(self.value, six.string_types):
            return self.value
        else:
            raise QueryTypeError(
                "Expected value to be an instance of `str`, not %s" % type(self.value)
            )


class DateTimeValueWrapper(ValueWrapper):
    def __init__(self, value):
        super(DateTimeValueWrapper, self).__init__(datetime)
        self.value = value

    def get_query(self, date_only=False, extra_param=None, **kwargs):
        if hasattr(self.value, "strftime"):
            datetime_ = datetime_as_utc(self.value)
            if date_only:
                value = datetime_.strftime("%Y-%m-%d")
            else:
                value = datetime_.strftime("%Y-%m-%d %H:%M:%S")

            if extra_param:
                value += '", "{}'.format(extra_param)

            return 'javascript:gs.dateGenerate("{}")'.format(value)
        else:
            raise QueryTypeError(
                "Expected value to be an instance of `datetime`, not %s"
                % type(self.value)
            )


class ListValueWrapper(ValueWrapper):
    def __init__(self, value, types):
        super(ListValueWrapper, self).__init__(list)
        self.value = value
        self.types = types

    def get_query(self, **kwargs):
        if isinstance(self.value, (list, tuple)) and all(
            type(x) in self.types for x in self.value
        ):
            return ",".join(map(str, self.value))
        else:
            raise QueryTypeError(
                "Expected value to be a list of type %s, not %s"
                % (self.types, type(self.value))
            )


class Field(Criterion):
    def __init__(self, name):
        super(Field, self).__init__()
        self.name = name

    def get_query(self, **kwargs):
        return self.name


class Table(object):
    """
        Allows the following:

        ```
        incident = Table(incident)
        criterion = incident.company.eq('3dasd3')
        ```
    """

    # Could be used to automate resource creation?
    def __init__(self, name):
        self.table_name = name

    def field(self, name):
        return Field(name)

    def __getattr__(self, name):
        return self.field(name)

    def __getitem__(self, name):
        return self.field(name)


def datetime_as_utc(date_obj):
    if date_obj.tzinfo is not None and date_obj.tzinfo.utcoffset(date_obj) is not None:
        return date_obj.astimezone(pytz.UTC)
    return date_obj
