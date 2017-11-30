# -*- coding: utf-8 -*-

from .request import PreparedRequest


class Resource(object):
    """Creates a new :class:`Resource` object

    Resources provides a natural way of interfacing with ServiceNow APIs.

    :param base_path: Base path
    :param api_path: API path
    :param \*\*kwargs: Arguments to pass along to :class:`Request`
    """

    def __init__(self, **kwargs):
        self._base_path = kwargs.get('base_path')
        self._api_path = kwargs.get('api_path')
        self._generator_size = kwargs.get('generator_size')

        self._request = PreparedRequest(resource=self, **kwargs)

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    @property
    def path(self):
        """Returns full API path"""
        return "%s" % self._base_path + self._api_path

    def get(self, query=None, limit=None, fields=list(), order_by=list(), offset=None):
        """Queries the API resource

        :param query: (optional) Dictionary, string or :class:`QueryBuilder` object
        :param limit: (optional) Limits the number of records returned
        :param fields: (optional) List of fields to include in the response
        :param order_by: (optional) List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :param offset: (optional) Number of records to skip before returning records
        :return: :class:`Response` object
        """

        return self._request.get(query=query, fields=fields, order_by=order_by, offset=offset, limit=limit)

    def insert(self, payload):
        """Creates a new record in the API resource

        :param payload: Dictionary containing key-value fields of the new record
        :return: Dictionary of the inserted record
        """

        return self._request.insert(payload)

    def update(self, query, payload):
        """Updates a record in the API resource

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param payload: Dictionary containing key-value fields of the record to be updated
        :return: Dictionary of the updated record
        """

        return self._request.update(query, payload)

    def delete(self, query):
        """Deletes matching record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :return: Dictionary containing information about deletion result
        """

        return self._request.delete(query)

    def custom(self, method, path_append=None, headers=None, **kwargs):
        """Creates a custom request

        :param method: HTTP method to use
        :param path_append: (optional) relative to :prop:`api_path`
        :param headers: (optional) Dictionary of headers to add or override
        :param kwargs: kwargs to pass along to :class:`requests.Request`
        :return: :class:`Response` object
        """

        return self._request.custom(method, path_append=path_append, headers=headers, **kwargs)
