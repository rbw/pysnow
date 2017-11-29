
# -*- coding: utf-8 -*-

import six

from .query_builder import QueryBuilder

from .exceptions import InvalidUsage


class Query(object):
    """Takes query and request params to construct a param dictionary -
    compatible with :class:`requests.Request`

    :param query: Dictionary, string or :class:`QueryBuilder` object
    :param request_params: Dictionary of query parameters to pass along to :class:`requests.Request`
    """

    def __init__(self, query, request_params):
        self._query = query or {}
        self._request_params = request_params

        self.str_query = self._stringify()

    def _stringify(self):
        """Stringifies the query (dict or QueryBuilder) to a ServiceNow-compatible format

        :return: ServiceNow-compatible string-type query
        """

        query = self._query
        if isinstance(query, QueryBuilder):
            # Get string-representation of the passed :class:`pysnow.QueryBuilder` object
            return str(query)
        elif isinstance(query, dict):
            # Dict-type query
            return '^'.join(['%s=%s' % (k, v) for k, v in six.iteritems(query)])
        elif isinstance(query, str):
            # Regular string-type query
            return query
        else:
            raise InvalidUsage('Query must be instance of %s, %s or %s' % (QueryBuilder, str, dict))

    def sort(self, order_by):
        """Applies sorting to the query

        :param order_by: List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :return: self
        :rtype: :class:`pysnow.Query`
        """

        if not isinstance(order_by, list):
            raise InvalidUsage('order_by must be of type list()')

        for field in order_by:
            if field[0] == '-':
                self.str_query += '^ORDERBYDESC%s' % field[1:]
            else:
                self.str_query += '^ORDERBY%s' % field

        return self

    def set_generator_size(self, size):
        """Sets generator size aka limit

        :param size:  generator size (int)
        """

        self._request_params.update({
            'sysparm_limit': size,
        })

    def filter(self, fields=list(), limit=None, offset=None):
        """Applies fields, limit and offset filters to the query

        :param fields: List of fields to include in the response
        :param limit: Limits the number of records returned
        :param offset: Number of records to skip before returning records
        :return: self
        :rtype: :class:`pysnow.Query`
        """

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
        """Constructs query params compatible with :class:`requests.Request`

        :return: Dictionary containing query params
        """

        q = {'sysparm_query': self.str_query}
        q.update(self._request_params)
        return q
