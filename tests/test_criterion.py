# -*- coding: utf-8 -*-
import unittest
import pytz
import pysnow
from datetime import datetime as dt

from pysnow.criterion import (
    Field,
)
from pysnow.enums import(
    DateTimeOn,
)
from pysnow.exceptions import (
    QueryEmpty,
    QueryExpressionError,
    QueryMissingField,
    QueryMultipleExpressions,
    QueryTypeError,
)


class TestQueryBuilder(unittest.TestCase):

    def test_query_logical_and(self):
        # Make sure AND() operator between expressions works
        q = (
            Field("test").eq("test")
            .AND(
                Field("test2").eq("test")
            )
        )
        self.assertEqual(str(q), "test=test^test2=test")

    def test_query_logical_bitwise_and(self):
        # Make sure AND() operator between expressions works
        q = (
            (Field("test") == "test")
            &
            (Field("test2") == "test")
        )
        self.assertEqual(str(q), "test=test^test2=test")

    def test_query_logical_or(self):
        # Make sure AND() operator between expressions works
        q = (
            Field("test").eq("test")
            .OR(
                Field("test2").eq("test")
            )
        )
        self.assertEqual(str(q), "test=test^ORtest2=test")

    def test_query_logical_bitwise_or(self):
        # Make sure AND() operator between expressions works
        q = (
            (Field("test") == "test")
            |
            (Field("test2") == "test")
        )
        self.assertEqual(str(q), "test=test^ORtest2=test")

    def test_query_logical_nq(self):
        # Make sure AND() operator between expressions works
        q = (
            Field("test").eq("test")
            .NQ(
                Field("test2").eq("test")
            )
        )
        self.assertEqual(str(q), "test=test^NQtest2=test")

    def test_query_logical_bitwise_nq(self):
        # Make sure AND() operator between expressions works
        q = (
            Field("test").eq("test")
            ^
            Field("test2").eq("test")
        )
        self.assertEqual(str(q), "test=test^NQtest2=test")

    def test_query_cond_between(self):
        # Make sure between with str arguments fails
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.between, "start", "end")

        # Make sure between with int arguments works
        q2 = Field("test").between(1, 2)
        self.assertEqual(str(q2), "testBETWEEN1@2")

        # Make sure between with dates works
        start = dt(1970, 1, 1)
        end = dt(1970, 1, 2)

        q2 = Field("test").between(start, end)
        self.assertEqual(
            str(q2),
            'testBETWEENjavascript:gs.dateGenerate("1970-01-01 00:00:00")'
            '@javascript:gs.dateGenerate("1970-01-02 00:00:00")',
        )

    def test_query_cond_starts_with(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.starts_with, 1)

        # Make sure a valid operation works
        q2 = Field("test").starts_with("val")
        self.assertEqual(str(q2), "testSTARTSWITHval")

    def test_query_cond_ends_with(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.ends_with, 1)

        # Make sure a valid operation works
        q2 = Field("test").ends_with("val")
        self.assertEqual(str(q2), "testENDSWITHval")

    def test_query_cond_contains(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.contains, 1)

        # Make sure a valid operation works
        q2 = Field("test").contains("val")
        self.assertEqual(str(q2), "testLIKEval")

    def test_query_cond_not_contains(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.not_contains, 1)

        # Make sure a valid operation works
        q2 = Field("test").not_contains("val")
        self.assertEqual(str(q2), "testNOT LIKEval")

    def test_query_cond_is_empty(self):
        # Make sure a valid operation works
        q = Field("test").is_empty()

        self.assertEqual(str(q), "testISEMPTY")

    def test_query_cond_is_not_empty(self):
        # Make sure a valid operation works
        q = Field("test").is_not_empty()

        self.assertEqual(str(q), "testISNOTEMPTY")

    def test_query_cond_is_in(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.is_in, [dt])
        self.assertRaises(QueryTypeError, q1.is_in, "single")

        # Make sure a valid operation works (string list)
        q3 = Field("test").is_in(["foo", "bar"])
        self.assertEqual(str(q3), "testINfoo,bar")

        # Make sure a valid operation works (int list)
        q3 = Field("test").is_in([1, 2])
        self.assertEqual(str(q3), "testIN1,2")

    def test_query_cond_not_in(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.not_in, [dt])
        self.assertRaises(QueryTypeError, q1.not_in, "single")

        # Make sure a valid operation works (string list)
        q3 = Field("test").not_in(["foo", "bar"])
        self.assertEqual(str(q3), "testNOT INfoo,bar")

        # Make sure a valid operation works (int list)
        q3 = Field("test").not_in([1, 2])
        self.assertEqual(str(q3), "testNOT IN1,2")

    def test_query_cond_equals(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.eq, dt)

        # Make sure a valid operation works (str)
        q2 = Field("test").eq("test")
        self.assertEqual(str(q2), "test=test")

    def test_query_cond_not_equals(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.ne, dt)

        # Make sure a valid operation works (str)
        q2 = Field("test").ne("test")
        self.assertEqual(str(q2), "test!=test")

    def test_query_cond_greater_than(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.gt, "a")

        # Make sure a valid operation works
        q2 = Field("test").gt(1)
        self.assertEqual(str(q2), "test>1")

        # Make sure naive dates are assumed as UTC
        q3 = Field("test").gt(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test>javascript:gs.dateGenerate("2016-02-01 00:00:00")')

        # Make sure tz-aware dates are converted to UTC (UTC+1)
        q4 = (
            Field("test")
            .gt(dt(2016, 2, 1, 3, tzinfo=pytz.FixedOffset(60)))
        )
        self.assertEqual(str(q4), 'test>javascript:gs.dateGenerate("2016-02-01 02:00:00")')

    def test_query_cond_less_than(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.lt, "a")

        # Make sure a valid operation works
        q2 = Field("test").lt(1)
        self.assertEqual(str(q2), "test<1")

        # Make sure naive dates are assumed as UTC
        q3 = Field("test").lt(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test<javascript:gs.dateGenerate("2016-02-01 00:00:00")')

        # Make sure tz-aware dates are converted to UTC (UTC+1)
        q3 = (
            Field("test")
            .lt(dt(2016, 2, 1, 3, tzinfo=pytz.FixedOffset(60)))
        )
        self.assertEqual(str(q3), 'test<javascript:gs.dateGenerate("2016-02-01 02:00:00")')

    def test_query_cond_greater_than_or_equal(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.gte, "a")

        # Make sure a valid operation works
        q2 = Field("test").gte(1)
        self.assertEqual(str(q2), "test>=1")

        # Make sure naive dates are assumed as UTC
        q3 = Field("test").gte(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test>=javascript:gs.dateGenerate("2016-02-01 00:00:00")')

        # Make sure tz-aware dates are converted to UTC (UTC+1)
        q4 = (
            Field("test")
            .gte(dt(2016, 2, 1, 3, tzinfo=pytz.FixedOffset(60)))
        )
        self.assertEqual(str(q4), 'test>=javascript:gs.dateGenerate("2016-02-01 02:00:00")')

    def test_query_cond_less_than_or_equal(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.lte, "a")

        # Make sure a valid operation works
        q2 = Field("test").lte(1)
        self.assertEqual(str(q2), "test<=1")

        # Make sure naive dates are assumed as UTC
        q3 = Field("test").lte(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test<=javascript:gs.dateGenerate("2016-02-01 00:00:00")')

        # Make sure tz-aware dates are converted to UTC (UTC+1)
        q3 = (
            Field("test")
            .lte(dt(2016, 2, 1, 3, tzinfo=pytz.FixedOffset(60)))
        )
        self.assertEqual(str(q3), 'test<=javascript:gs.dateGenerate("2016-02-01 02:00:00")')

    def test_query_cond_on(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.on, "a")
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.on, 1)

        # Make sure naive dates are assumed as UTC
        q2 = Field("test").on(dt(2016, 2, 1))
        self.assertEqual(str(q2), 'testONcustom@javascript:gs.dateGenerate("2016-02-01", "start")@javascript:gs.dateGenerate("2016-02-01", "end")')

        q3 = Field("test").on(DateTimeOn.today)
        self.assertEqual(str(q3), 'testONToday@javascript:gs.beginningOfToday()@javascript:gs.endOfToday()')

    def test_query_cond_not_on(self):
        # Make sure type checking works
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.not_on, "a")
        q1 = Field("test")
        self.assertRaises(QueryTypeError, q1.not_on, 1)

        # Make sure naive dates are assumed as UTC
        q2 = Field("test").not_on(dt(2016, 2, 1))
        self.assertEqual(str(q2), 'testNOTONcustom@javascript:gs.dateGenerate("2016-02-01", "start")@javascript:gs.dateGenerate("2016-02-01", "end")')

        q3 = Field("test").not_on(DateTimeOn.today)
        self.assertEqual(str(q3), 'testNOTONToday@javascript:gs.beginningOfToday()@javascript:gs.endOfToday()')

    def test_complex_query(self):
        start = dt(2016, 2, 1)
        end = dt(2016, 2, 10)

        q = (
            Field("f1").eq("val1")
            .AND(
                Field("f2").between(start, end)
            )
            .NQ(
                Field("f3").eq("val3")
            )
        )

        self.assertEqual(
            str(q),
            'f1=val1^f2BETWEENjavascript:gs.dateGenerate("2016-02-01 00:00:00")'
            '@javascript:gs.dateGenerate("2016-02-10 00:00:00")^NQf3=val3',
        )

    def test_complex_query_bitwise(self):
        start = dt(2016, 2, 1)
        end = dt(2016, 2, 10)

        q = (
            Field("f1").eq("val1")
            &
            Field("f2").between(start, end)
            ^
            Field("f3").eq("val3")
        )

        self.assertEqual(
            str(q),
            'f1=val1^f2BETWEENjavascript:gs.dateGenerate("2016-02-01 00:00:00")'
            '@javascript:gs.dateGenerate("2016-02-10 00:00:00")^NQf3=val3',
        )
