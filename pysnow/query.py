# -*- coding: utf-8 -*-

import six

from .query_builder import QueryBuilder

from pysnow.exceptions import InvalidUsage


class Query(object):
    def __init__(self, query, request_params):
        self._query = query or {}
        self._query_parsed = self._parse()
        self._request_params = request_params

    def _parse(self):
        query = self._query
        if isinstance(query, QueryBuilder):
            return str(query)
        elif isinstance(query, dict):
            return '^'.join(['%s=%s' % (k, v) for k, v in six.iteritems(query)])
        elif isinstance(query, str):
            return query
        else:
            raise InvalidUsage('Query must be instance of %s, %s or %s' % (QueryBuilder, str, dict))

    def sort(self, order_by):
        if not isinstance(order_by, list):
            raise InvalidUsage('order_by must be of type list()')

        for field in order_by:
            if field[0] == '-':
                self._query_parsed += '^ORDERBYDESC%s' % field[1:]
            else:
                self._query_parsed += '^ORDERBY%s' % field

        return self

    def set_generator_size(self, size):
        self._request_params.update({
            'sysparm_limit': size,
        })

    def filter(self, fields=list(), limit=None, offset=None):
        if not isinstance(fields, list):
            raise InvalidUsage('fields must be of type list()')

        if limit:
            self._request_params.update({
                'sysparm_limit': limit,
                'sysparm_suppress_pagination_header': True
            })

        if offset:
            self._request_params.update({'sysparm_offset': offset})

        if len(fields) > 0:
            self._request_params.update({'sysparm_fields': ",".join(fields)})

        return self

    def as_dict(self):
        q = {'sysparm_query': self._query_parsed}
        q.update(self._request_params)
        return q
