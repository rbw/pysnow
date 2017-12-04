# -*- coding: utf-8 -*-

from .request import SnowRequest
from .url_builder import URLBuilder

class Resource(object):
    """Creates a new :class:`Resource` object

    Resources provides a natural way of interfacing with ServiceNow APIs.

    :param base_path: Base path
    :param api_path: API path
    :param \*\*kwargs: Arguments to pass along to :class:`Request`
    """

    _report = None

    def __init__(self, base_url=None, base_path=None, api_path=None, **kwargs):
        self._base_url = base_url
        self._base_path = base_path
        self._api_path = api_path
        self._url_builder = URLBuilder(base_url, base_path, api_path)

        self.sysparms = kwargs.pop('sysparms')
        self.kwargs = kwargs

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    @property
    def path(self):
        """Returns full API path"""
        return "%s" % self._base_path + self._api_path

    @property
    def _request(self):
        return SnowRequest(url_builder=self._url_builder, sysparms=self.sysparms, **self.kwargs)

    def get(self, query, limit=None, offset=None, fields=list()):
        """Queries the API resource

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param limit: (optional) Limits the number of records returned
        :param fields: (optional) List of fields to include in the response
        created_on in descending order.
        :param offset: (optional) Number of records to skip before returning records
        :return: :class:`Response` object
        """

        return self._request.get(query, limit, offset, fields)

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
