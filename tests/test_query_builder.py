# -*- coding: utf-8 -*-
import unittest
import pysnow
from datetime import datetime as dt

from pysnow.exceptions import (QueryEmpty,
                               QueryExpressionError,
                               QueryMissingField,
                               QueryMultipleExpressions,
                               QueryTypeError)


class TestQueryBuilder(unittest.TestCase):
    def test_query_no_expression(self):
        q = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryEmpty, q.__str__)

    def test_query_no_query(self):
        q = pysnow.QueryBuilder()
        self.assertRaises(QueryEmpty, q.__str__)

    def test_query_unexpected_logical(self):
        q = pysnow.QueryBuilder()
        self.assertRaises(QueryExpressionError, q.AND)

    def test_query_expression_no_field(self):
        q = pysnow.QueryBuilder()
        self.assertRaises(QueryMissingField, q.equals, 'test')

    def test_query_no_field_expression(self):
        q = pysnow.QueryBuilder().field('test').equals('test').AND().field('test')
        self.assertRaises(QueryExpressionError, q.__str__)

    def test_query_field_multiple_expressions(self):
        q = pysnow.QueryBuilder().field('test').equals('test')
        self.assertRaises(QueryMultipleExpressions, q.between, 1, 2)

    def test_query_unfinished_logical(self):
        q = pysnow.QueryBuilder().field('test').equals('test').AND()
        self.assertRaises(QueryMissingField, q.__str__)

    def test_query_logical_and(self):
        # Make sure AND() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').AND().field('test2').equals('test')
        self.assertEqual(str(q), 'test=test^test2=test')

    def test_query_logical_or(self):
        # Make sure OR() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').OR().field('test2').equals('test')
        self.assertEqual(str(q), 'test=test^ORtest2=test')

    def test_query_logical_nq(self):
        # Make sure NQ() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').NQ().field('test2').equals('test')
        self.assertEqual(str(q), 'test=test^NQtest2=test')

    def test_query_order_descending(self):
        # :meth:`order_descending` should generate ORDERBYDESC<field>
        q = pysnow.QueryBuilder().field('foo').equals('bar').AND().field('foo2').order_descending()
        self.assertEqual(str(q), 'foo=bar^ORDERBYDESCfoo2')

    def test_query_order_ascending(self):
        # :meth:`order_descending` should generate ORDERBY<field>
        q = pysnow.QueryBuilder().field('foo').equals('bar').AND().field('foo2').order_ascending()
        self.assertEqual(str(q), 'foo=bar^ORDERBYfoo2')

    def test_query_cond_between(self):
        # Make sure between with str arguments fails
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.between, 'test', 'test')

        # Make sure between with int arguments works
        q2 = str(pysnow.QueryBuilder().field('test').between(1, 2))
        self.assertEqual(str(q2), 'testBETWEEN1@2')

        start = dt(1970, 1, 1)
        end = dt(1970, 1, 2)

        # Make sure between with dates works
        q2 = str(pysnow.QueryBuilder().field('test').between(start, end))
        self.assertEqual(str(q2), 'testBETWEENjavascript:gs.dateGenerate("1970-01-01 00:00:00")'
                                   '@javascript:gs.dateGenerate("1970-01-02 00:00:00")')

    def test_query_cond_starts_with(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.starts_with, 1)

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').starts_with('val')
        self.assertEqual(str(q2), 'testSTARTSWITHval')

    def test_query_cond_ends_with(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.ends_with, 1)

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').ends_with('val')
        self.assertEqual(str(q2), 'testENDSWITHval')

    def test_query_cond_contains(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.contains, 1)

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').contains('val')
        self.assertEqual(str(q2), 'testLIKEval')

    def test_query_cond_not_contains(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.not_contains, 1)

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').not_contains('val')
        self.assertEqual(str(q2), 'testNOTLIKEval')

    def test_query_cond_is_empty(self):
        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').is_empty()

        self.assertEqual(str(q), 'testISEMPTY')

    def test_query_cond_equals(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.equals, dt)

        # Make sure a valid operation works (str)
        q2 = pysnow.QueryBuilder().field('test').equals('test')
        self.assertEqual(str(q2), 'test=test')

        # Make sure a valid operation works (list)
        q3 = pysnow.QueryBuilder().field('test').equals(['foo', 'bar', 1])
        self.assertEqual(str(q3), 'testINfoo,bar,1')

    def test_query_cond_not_equals(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.not_equals, dt)

        # Make sure a valid operation works (str)
        q2 = pysnow.QueryBuilder().field('test').not_equals('test')
        self.assertEqual(str(q2), 'test!=test')

        # Make sure a valid operation works (list)
        q3 = pysnow.QueryBuilder().field('test').not_equals(['foo', 'bar'])
        self.assertEqual(str(q3), 'testNOT INfoo,bar')

    def test_query_cond_greater_than(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.greater_than, 'a')

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').greater_than(1)
        self.assertEqual(str(q2), 'test>1')

        q3 = pysnow.QueryBuilder().field('test').greater_than(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test>2016-02-01 00:00:00')

    def test_query_cond_less_than(self):
        # Make sure type checking works
        q1 = pysnow.QueryBuilder().field('test')
        self.assertRaises(QueryTypeError, q1.less_than, 'a')

        # Make sure a valid operation works
        q2 = pysnow.QueryBuilder().field('test').less_than(1)
        self.assertEqual(str(q2), 'test<1')

        q3 = pysnow.QueryBuilder().field('test').less_than(dt(2016, 2, 1))
        self.assertEqual(str(q3), 'test<2016-02-01 00:00:00')

    def test_complex_query(self):
        start = dt(2016, 2, 1)
        end = dt(2016, 2, 10)

        q = pysnow.QueryBuilder()\
            .field('f1').equals('val1')\
            .AND()\
            .field('f2').between(start, end)\
            .NQ()\
            .field('f3').equals('val3')

        self.assertEqual(str(q), 'f1=val1^f2BETWEENjavascript:gs.dateGenerate("2016-02-01 00:00:00")'
                                 '@javascript:gs.dateGenerate("2016-02-10 00:00:00")^NQf3=val3')

