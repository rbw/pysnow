
# -*- coding: utf-8 -*-

import six

from .query_builder import QueryBuilder

from .exceptions import InvalidUsage


class Sysparms(object):
    """Sysparm query builder"""

    _foreign_params = {}

    _sysparms = {
        'sysparm_query': '',
        'sysparm_limit': None,
        'sysparm_offset': None,
        'sysparm_suppress_pagination_header': False,
        'sysparm_fields': []
    }

    @staticmethod
    def stringify_query(query):
        """Stringifies the query (dict or QueryBuilder) into a ServiceNow-compatible format

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
            raise InvalidUsage('Query must be of type string, dict or a QueryBuilder object')

    @property
    def foreign_params(self):
        return self._foreign_params

    def add_foreign(self, params):
        if isinstance(params, dict) is False:
            raise TypeError("Foreign parameters must be of type `dict`")

        self._foreign_params.update(params)

    @property
    def query(self):
        return self._sysparms['sysparm_query']

    @query.setter
    def query(self, query):
        self._sysparms['sysparm_query'] = self.stringify_query(query)

    @property
    def offset(self):
        """Sets `sysparm_offset`, usually used to accomplish pagination

        :param offset: Number of records to skip before fetching records
        :raise:
            :InvalidUsage: if offset is of an unexpected type
        """

        return self._sysparms['sysparm_offset']

    @offset.setter
    def offset(self, offset):
        if not isinstance(offset, int) or isinstance(offset, bool):
            raise InvalidUsage('Offset must be an integer')

        self._sysparms['sysparm_offset'] = offset

    @property
    def fields(self):
        return self._sysparms['sysparm_fields']

    @fields.setter
    def fields(self, fields):
        """Converts a list of fields to a comma-separated string

        :param fields: List of fields to include in the response
        :raise:
            :InvalidUsage: if fields is of an unexpected type
        """

        if not isinstance(fields, list):
            raise InvalidUsage('fields must be of type `list`')

        self._sysparms['sysparm_fields'] = ",".join(fields)

    @property
    def paginate(self):
        return not self._sysparms['sysparm_suppress_pagination_header']

    @paginate.setter
    def paginate(self, pagination_wanted=True):
        self._sysparms['sysparm_suppress_pagination_header'] = not pagination_wanted

    @property
    def limit(self):
        return self._sysparms['sysparm_limit']

    @limit.setter
    def limit(self, number_records):
        """Sets page_size aka limit

        :param size: Generator size (int)
        :param disable_pagination: Whether or not to use pagination (Link headers)
        """

        if not isinstance(number_records, int) or isinstance(number_records, bool):
            raise InvalidUsage("limit size must be of type integer")

        self._sysparms['sysparm_limit'] = number_records

    def as_dict(self):
        """Constructs query params compatible with :class:`requests.Request`

        :return: Dictionary containing query parameters
        """

        sysparms = self._sysparms
        sysparms.update(self._foreign_params)

        return sysparms
