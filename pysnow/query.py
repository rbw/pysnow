
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

    def __init__(self, query, request_params=None):
        self.str_query = self.stringify(query)
        self._request_params = request_params or {}

    @staticmethod
    def stringify(query):
        """Stringifies the query (dict or QueryBuilder) to a ServiceNow-compatible format

        :return: ServiceNow-compatible string-type query
        """

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

    def set_sorting(self, order_by):
        """Applies sorting to the query

        :param order_by: List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :return: self
        :rtype: :class:`pysnow.Query`
        """

        if not isinstance(order_by, list):
            raise InvalidUsage('Sort fields must be of type list()')

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

        if not isinstance(size, int) or isinstance(size, bool):
            raise InvalidUsage("Generator size must be an integer")

        self._request_params.update({
            'sysparm_limit': size,
        })

    def set_offset(self, offset):
        """Sets `sysparm_offset`, usually used to accomplish pagination

        :param offset: Number of records to skip before fetching records
        :raise:
            :InvalidUsage: if offset is of an unexpected type
        """

        if not isinstance(offset, int) or isinstance(offset, bool):
            raise InvalidUsage('Offset must be an integer')

        self._request_params.update({'sysparm_offset': offset})

    def set_limit(self, limit):
        """Sets `sysparm_limit` to the limit provided and `sysparm_suppress_pagination_header` to True, which disables
        the use of link headers and as an side-effect, the use of generators in :class:`pysnow.Response`.

        :param limit: Maximum number of records to return in the response
        :raise:
            :InvalidUsage: if limit is of an unexpected type
        """

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise InvalidUsage('Limit must be an integer')

        self._request_params.update({
            'sysparm_limit': limit,
            'sysparm_suppress_pagination_header': True
        })

    def set_fields(self, fields):
        """Converts a list of fields to a comma-separated string

        :param fields: List of fields to include in the response
        :raise:
            :InvalidUsage: if fields is of an unexpected type
        """

        if not isinstance(fields, list):
            raise InvalidUsage('fields must be of type list()')

        if len(fields) > 0:
            self._request_params.update({'sysparm_fields': ",".join(fields)})

    def as_dict(self):
        """Constructs query params compatible with :class:`requests.Request`

        :return: Dictionary containing query params
        """

        q = {'sysparm_query': self.str_query}
        q.update(self._request_params)
        return q
