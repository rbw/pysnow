# -*- coding: utf-8 -*-
import unittest

from pysnow.query import Query
from pysnow.query_builder import QueryBuilder
from pysnow.exceptions import InvalidUsage


class TestQuery(unittest.TestCase):
    def test_stringify_dict(self):
        """:meth:`_stringify` should be able to convert a dict to a string of the expected value"""

        query = {'dict_foo': 'dict_bar'}
        expected_string = 'dict_foo=dict_bar'

        self.assertEquals(Query.stringify(query), expected_string)

    def test_stringify_query_builder(self):
        """:meth:`_stringify` should be able to convert a query builder object to a string of the expected value"""

        query = QueryBuilder().field('qb_foo').equals('qb_bar')
        expected_string = "qb_foo=qb_bar"

        self.assertEquals(Query.stringify(query), expected_string)

    def test_stringify_string(self):
        """:meth:`_stringify` should leave string-type queries as is"""

        query = "str_foo=str_bar"

        self.assertEquals(Query.stringify(query), query)

    def test_stringify_invalid_type(self):
        """:meth:`_stringify` should raise an InvalidUsage exception if the query is of invalid type"""

        self.assertRaises(InvalidUsage, Query.stringify, False)
        self.assertRaises(InvalidUsage, Query.stringify, True)
        self.assertRaises(InvalidUsage, Query.stringify, ('foo', 'bar'))
        self.assertRaises(InvalidUsage, Query.stringify, 1)

    def test_apply_valid_sorting(self):
        """:meth:`sort` should apply sorting to the query passed to the constructor"""

        order_by = ['-foo', 'bar']
        expected_sort_str = 'foo=bar^ORDERBYDESCfoo^ORDERBYbar'

        q = Query('foo=bar').set_sorting(order_by)

        self.assertEquals(q.str_query, expected_sort_str)

    def test_apply_invalid_sorting(self):
        """:meth:`sort` should raise an InvalidUsage exception if the order_by argument is of an invalid type"""

        q = Query('foo=bar')

        self.assertRaises(InvalidUsage, q.set_sorting, 'foo')
        self.assertRaises(InvalidUsage, q.set_sorting, 1)
        self.assertRaises(InvalidUsage, q.set_sorting, False)
        self.assertRaises(InvalidUsage, q.set_sorting, ('asd', 'dsa'))

    def test_apply_valid_generator_size(self):
        """:meth:`set_generator_size` should set `sysparm_limit` in :prop:`_request_params`"""

        size = 10
        expected_dict = {'sysparm_limit': size}
        q = Query('foo=bar')
        q.set_generator_size(size)

        self.assertEquals(q._request_params, expected_dict)

    def test_apply_valid_limit(self):
        """:meth:`set_limit` should set `sysparm_limit` and `sysparm_suppress_pagination_header`
        in :prop:`_request_params`"""

        limit = 20
        expected_dict = {'sysparm_limit': limit, 'sysparm_suppress_pagination_header': True}
        q = Query('foo=bar')
        q.set_limit(limit)

        self.assertEquals(q._request_params, expected_dict)

    def test_apply_valid_offset(self):
        """:meth:`set_offset` should set `sysparm_offset` in :prop:`_request_params`"""

        offset = 30
        expected_dict = {'sysparm_offset': offset}
        q = Query('foo=bar')
        q.set_offset(offset)

        self.assertEquals(q._request_params, expected_dict)

    def test_apply_valid_fields(self):
        """:meth:`set_fields` should set `sysparm_fields` in :prop:`_request_params` to a comma-separated string"""

        fields = ['field1', 'field2']
        expected_dict = {'sysparm_fields': ','.join(fields)}
        q = Query('foo=bar')
        q.set_fields(fields)

        self.assertEquals(q._request_params, expected_dict)

    def test_apply_invalid_generator_size(self):
        """:meth:`set_generator_size` should raise an InvalidUsage exception if the size is of an invalid type"""

        q = Query('foo=bar')

        self.assertRaises(InvalidUsage, q.set_generator_size, 'foo')
        self.assertRaises(InvalidUsage, q.set_generator_size, {'foo': 'bar'})
        self.assertRaises(InvalidUsage, q.set_generator_size, False)
        self.assertRaises(InvalidUsage, q.set_generator_size, ('asd', 'dsa'))

    def test_apply_invalid_fields(self):
        """:meth:`set_fields` should raise an InvalidUsage exception if fields is of an invalid type"""

        q = Query('foo=bar')

        self.assertRaises(InvalidUsage, q.set_fields, 'foo')
        self.assertRaises(InvalidUsage, q.set_fields, 0)
        self.assertRaises(InvalidUsage, q.set_fields, False)
        self.assertRaises(InvalidUsage, q.set_fields, ('asd', 'dsa'))

    def test_apply_invalid_offset(self):
        """:meth:`set_offset` should raise an InvalidUsage exception if offset is of an invalid type"""

        q = Query('foo=bar')

        self.assertRaises(InvalidUsage, q.set_offset, 'foo')
        self.assertRaises(InvalidUsage, q.set_offset, {'foo': 'bar'})
        self.assertRaises(InvalidUsage, q.set_offset, False)
        self.assertRaises(InvalidUsage, q.set_offset, ('asd', 'dsa'))

    def test_apply_invalid_limit(self):
        """:meth:`set_limit` should raise an InvalidUsage exception if limit is of an invalid type"""

        q = Query('foo=bar')

        self.assertRaises(InvalidUsage, q.set_limit, 'foo')
        self.assertRaises(InvalidUsage, q.set_limit, {'foo': 'bar'})
        self.assertRaises(InvalidUsage, q.set_limit, False)
        self.assertRaises(InvalidUsage, q.set_limit, ('asd', 'dsa'))

    def test_params_as_dict(self):
        """:meth:`as_dict` should return a :class:`requests.Request` compatible param dictionary"""

        query = {'foo': 'bar'}
        fields = ['field1', 'field2']
        offset = 10
        limit = 20

        expected_dict = {
            'sysparm_limit': limit,
            'sysparm_suppress_pagination_header': True,
            'sysparm_offset': offset,
            'sysparm_query': 'foo=bar',
            'sysparm_fields': ','.join(fields)
        }

        q = Query(query)
        q.set_fields(fields)
        q.set_offset(offset)
        q.set_limit(limit)

        self.assertEquals(q.as_dict(), expected_dict)


