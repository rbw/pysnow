# -*- coding: utf-8 -*-
import unittest

from pysnow.sysparms import Sysparms
from pysnow.query_builder import QueryBuilder
from pysnow.exceptions import InvalidUsage


class TestQuery(unittest.TestCase):
    def test_stringify_dict(self):
        """:meth:`_stringify` should be able to convert a dict to a string of the expected value"""

        query = {'dict_foo': 'dict_bar'}
        expected_string = 'dict_foo=dict_bar'

        self.assertEquals(Sysparms.stringify_query(query), expected_string)

    def test_stringify_query_builder(self):
        """:meth:`_stringify` should be able to convert a query builder object to a string of the expected value"""

        query = QueryBuilder().field('qb_foo').equals('qb_bar')
        expected_string = "qb_foo=qb_bar"

        self.assertEquals(Sysparms.stringify_query(query), expected_string)

    def test_stringify_string(self):
        """:meth:`_stringify` should leave string-type queries as is"""

        query = "str_foo=str_bar"

        self.assertEquals(Sysparms.stringify_query(query), query)

    def test_stringify_invalid_type(self):
        """:meth:`_stringify` should raise an InvalidUsage exception if the query is of invalid type"""

        self.assertRaises(InvalidUsage, Sysparms.stringify_query, False)
        self.assertRaises(InvalidUsage, Sysparms.stringify_query, True)
        self.assertRaises(InvalidUsage, Sysparms.stringify_query, ('foo', 'bar'))
        self.assertRaises(InvalidUsage, Sysparms.stringify_query, 1)

    def test_apply_valid_limit(self):
        """:meth:`set_limit` should set `sysparm_limit` and `sysparm_suppress_pagination_header`
        in :prop:`_request_params`"""

        limit = 20
        sp = Sysparms()
        sp.limit = limit

        self.assertEquals(sp._sysparms['sysparm_limit'], limit)

    def test_apply_valid_offset(self):
        """:meth:`set_offset` should set `sysparm_offset` in :prop:`_request_params`"""

        offset = 30
        sp = Sysparms()
        sp.offset = offset

        self.assertEquals(sp._sysparms['sysparm_offset'], offset)

    def test_apply_valid_fields(self):
        """:meth:`set_fields` should set `sysparm_fields` in :prop:`_request_params` to a comma-separated string"""

        fields = ['field1', 'field2']
        sp = Sysparms()
        sp.fields = fields

        self.assertEquals(sp._sysparms['sysparm_fields'], ','.join(fields))

    def test_apply_invalid_fields(self):
        """:meth:`set_fields` should raise an InvalidUsage exception if fields is of an invalid type"""

        sp = Sysparms()

        self.assertRaises(InvalidUsage, setattr, sp, 'fields', 'foo')
        self.assertRaises(InvalidUsage, setattr, sp, 'fields', 0)
        self.assertRaises(InvalidUsage, setattr, sp, 'fields', False)
        self.assertRaises(InvalidUsage, setattr, sp, 'fields', ('asd', 'dsa'))

    def test_apply_invalid_offset(self):
        """:meth:`set_offset` should raise an InvalidUsage exception if offset is of an invalid type"""

        sp = Sysparms()

        self.assertRaises(InvalidUsage, setattr, sp, 'offset', 'foo')
        self.assertRaises(InvalidUsage, setattr, sp, 'offset', {'foo': 'bar'})
        self.assertRaises(InvalidUsage, setattr, sp, 'offset', False)
        self.assertRaises(InvalidUsage, setattr, sp, 'offset', ('asd', 'dsa'))

    def test_apply_invalid_limit(self):
        """:meth:`set_limit` should raise an InvalidUsage exception if limit is of an invalid type"""

        sp = Sysparms()

        self.assertRaises(InvalidUsage, setattr, sp, 'limit', 'foo')
        self.assertRaises(InvalidUsage, setattr, sp, 'limit', {'foo': 'bar'})
        self.assertRaises(InvalidUsage, setattr, sp, 'limit', False)
        self.assertRaises(InvalidUsage, setattr, sp, 'limit', ('asd', 'dsa'))


