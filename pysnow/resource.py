# -*- coding: utf-8 -*-

from .request import Request


class Resource(object):
    """Creates a new :class:`Resource <Resource>`

    Resources enables a natural way of interfacing with ServiceNow APIs.

    :param base_path: Base path (string)
    :param api_path: API path (string)
    :param \*\*kwargs: Arguments to pass along to :class:`Request`
    """

    def __init__(self, **kwargs):
        self._base_path = kwargs.get('base_path')
        self._api_path = kwargs.get('api_path')

        self._request = Request(resource=self, **kwargs)

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    @property
    def path(self):
        """Returns full API path"""
        return "%s" % self._base_path + self._api_path

    @property
    def report(self):
        """Returns a report for the last operation

        :return: :class:`Report <Report>` object
        """
        return self._request.get_report()

    def get_multiple(self, query=None, limit=None, fields=list(), order_by=list(), offset=None):
        """Queries the API resource

        :param query: (optional) Dictionary, string or :class:`QueryBuilder <QueryBuilder>`
        :param limit: (optional) Limits the number of records returned
        :param fields: (optional) List of fields to include in the response
        :param order_by: (optional) List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :param offset: (optional) Number of records to skip before returning records
        :return: :class:`Response <Response>` object
        """
        return self._request.all(query=query, fields=fields, order_by=order_by, offset=offset, limit=limit)

    def get_first(self, query=None, fields=list(), order_by=list(), offset=None):
        """Queries the API resource with a limit set to 1. Gets next item from the iterator, effectively
        fetching the first item in the result set.

        :param query: (optional) Dictionary, string or :class:`QueryBuilder <QueryBuilder>`
        :param fields: (optional) List of fields to include in the response
        :param order_by: (optional) List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :param offset: (optional) Number of records to skip before returning records
        :return: :class:`Response <Response>` object
        """
        return next(self._request.all(query=query, fields=fields, order_by=order_by, offset=offset, limit=1), {})

    def insert(self, payload):
        """Creates a new record in the API resource

        :param payload: Dictionary containing key-value fields of the new record
        :return: :class:`Response <Response>` object
        """
        return self._request.insert(payload)

    def update(self, query, payload):
        """Updates a record in the API resource

        :param query: Dictionary, string or :class:`QueryBuilder <QueryBuilder>`
        :param payload: Dictionary containing key-value fields of the record to be updated
        :return: :class:`Response <Response>` object
        """
        return self._request.update(query, payload)

    def delete(self, query):
        """Deletes the queried record

        :param query: Dictionary, string or :class:`QueryBuilder <QueryBuilder>`
        :return: :class:`Response <Response>` object
        """
        return self._request.delete(query)
