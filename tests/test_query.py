# -*- coding: utf-8 -*-
import unittest
import pysnow
from datetime import datetime as dt


class TestIncident(unittest.TestCase):
    def test_query_no_expression(self):
        try:
            q = str(pysnow.QueryBuilder().field('test'))
            self.assertFalse(q)
        except pysnow.QueryEmpty:
            pass

    def test_query_no_query(self):
        try:
            q = str(pysnow.QueryBuilder())
            self.assertFalse(q)
        except pysnow.QueryEmpty:
            pass

    def test_query_no_field_expression(self):
        try:
            q = str(pysnow.QueryBuilder().field('test').equals('test').AND().field('beh'))
            self.assertFalse(q)
        except pysnow.QueryExpressionError:
            pass

    def test_query_field_multiple_expressions(self):
        try:
            q = str(pysnow.QueryBuilder().field('test').equals('test').between(1, 2))
            self.assertFalse(q)
        except pysnow.QueryMultipleExpressions:
            pass

    def test_query_unfinished_logical(self):
        try:
            q = str(pysnow.QueryBuilder().field('test').equals('test').AND())
            self.assertFalse(q)
        except pysnow.QueryMissingField:
            pass

    def test_query_logical_and(self):
        # Make sure AND() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').AND().field('test2').equals('test')

        self.assertEquals(str(q), 'test=test^test2=test')

    def test_query_logical_or(self):
        # Make sure OR() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').OR().field('test2').equals('test')

        self.assertEquals(str(q), 'test=test^ORtest2=test')

    def test_query_logical_nq(self):
        # Make sure NQ() operator between expressions works
        q = pysnow.QueryBuilder().field('test').equals('test').NQ().field('test2').equals('test')

        self.assertEquals(str(q), 'test=test^NQtest2=test')

    def test_query_cond_between(self):
        # Make sure between with str arguments fails
        try:
            q = pysnow.QueryBuilder().field('test').between('test', 'test')
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure between with int arguments works
        q1 = str(pysnow.QueryBuilder().field('test').between(1, 2))
        self.assertEquals(str(q1), 'testBETWEEN1@2')

        start = dt(1970, 1, 1)
        end = dt(1970, 1, 2)

        # Make sure between with dates works
        q2 = str(pysnow.QueryBuilder().field('test').between(start, end))
        self.assertEquals(str(q2), 'testBETWEENjavascript:gs.dateGenerate("1970-01-01 00:00:00")'
                                   '@javascript:gs.dateGenerate("1970-01-02 00:00:00")')

    def test_query_cond_starts_with(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').starts_with(1)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').starts_with('val')

        self.assertEquals(str(q), 'testSTARTSWITHval')

    def test_query_cond_ends_with(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').ends_with(1)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').ends_with('val')

        self.assertEquals(str(q), 'testENDSWITHval')

    def test_query_cond_contains(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').contains(1)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').contains('val')

        self.assertEquals(str(q), 'testLIKEval')

    def test_query_cond_not_contains(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').not_contains(1)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').not_contains('val')

        self.assertEquals(str(q), 'testNOTLIKEval')

    def test_query_cond_is_empty(self):
        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').is_empty()

        self.assertEquals(str(q), 'testISEMPTY')

    def test_query_cond_equals(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').equals(dt)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').equals('test')

        self.assertEquals(str(q), 'test=test')

    def test_query_cond_not_equals(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').not_equals(dt)
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').not_equals('test')

        self.assertEquals(str(q), 'test!=test')

    def test_query_cond_greater_than(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').greater_than('a')
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').greater_than(1)
        self.assertEquals(str(q), 'test>1')

        q = pysnow.QueryBuilder().field('test').greater_than(dt(2016, 2, 1))
        self.assertEquals(str(q), 'test>2016-02-01 00:00:00')

    def test_query_cond_less_than(self):
        # Make sure type checking works
        try:
            q = pysnow.QueryBuilder().field('test').less_than('a')
            self.assertFalse(q)
        except pysnow.QueryTypeError:
            pass

        # Make sure a valid operation works
        q = pysnow.QueryBuilder().field('test').less_than(1)
        self.assertEquals(str(q), 'test<1')

        q = pysnow.QueryBuilder().field('test').less_than(dt(2016, 2, 1))
        self.assertEquals(str(q), 'test<2016-02-01 00:00:00')

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

