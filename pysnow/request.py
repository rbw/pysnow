# -*- coding: utf-8 -*-

import json
import requests

from .response import Response
from .query import Query

from .exceptions import InvalidUsage


class PreparedRequest(object):
    """Creates a new :class:`PreparedRequest` object.

    :param request_params: Request parameters to pass along with the request
    :param session: :class:`request.Session` object
    :param generator_size: Generator size / internal page size
    :param generator_size: Sets the size of each yield, a higher value might increases performance some but
    will cause pysnow to consume more memory when serving big results.
    :param raise_on_empty: Whether or not to raise an exception on 404 (no matching records)
    :param resource_url: :class:`url.URL` object
    :param report: :class:`report.Report` object
    """

    def __init__(self,
                 request_params=None, session=None, generator_size=None,
                 raise_on_empty=True, resource_url=None, report=None):

        self._request_params = request_params
        self._session = session
        self._generator_size = generator_size
        self._report = report
        self._raise_on_empty = raise_on_empty
        self._resource_url = resource_url

    def _send(self, method, url, **kwargs):
        """Prepares and sends a new :class:`requests.Request` object, uses prepare() as it makes wrapping simpler.
        Also, sets request params in report, if reporting is enabled.

        :param method: Request method
        :param url: Request URL
        :param kwargs: kwargs to pass along to Request
        :return: :class:`requests.Response` object
        """

        params = kwargs.pop('params', self._request_params)

        request = requests.Request(method, url, auth=self._session.auth, params=params, **kwargs)

        if self._report:
            self._report.request_params = params

        prepared = request.prepare()
        response = self._session.send(prepared)

        return response

    def _get_response(self, method, url, **kwargs):
        """Response wrapper - creates a :class:`requests.Response` object and passes along to :class:`pysnow.Response`
        for validation and parsing.

        :param args: args to pass along to _send()
        :param kwargs: kwargs to pass along to _send()
        :return: :class:`pysnow.Response` object
        """

        return Response(self._send(method, url, **kwargs), request_callback=self._send,
                        raise_on_empty=self._raise_on_empty, report=self._report)

    def _get_request_params(self, query=None, fields=list(), limit=None, order_by=list(), offset=None):
        """Constructs request params dictionary to pass along with a :class:`requests.PreparedRequest` object

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param limit: Limits the number of records returned
        :param fields: List of fields to include in the response
        :param order_by: List of columns used in sorting. Example:
        ['category', '-created_on'] would sort the category field in ascending order, with a secondary sort by
        created_on in descending order.
        :param offset: Number of records to skip before returning records
        :return: :class:`pysnow.Query` dictionary-like object
        """

        query_params = Query(query, self._request_params)

        # Generator responses creates its "iterable chunks" using `sysparm_limit` and relies on the
        # use of link headers, which set_limit() disables, effectively disabling the use of generators.
        if not limit:
            query_params.set_generator_size(self._generator_size)
        else:
            query_params.set_limit(limit)

        if fields:
            query_params.set_fields(fields)

        if offset:
            query_params.set_offset(offset)

        if order_by:
            query_params.set_sorting(order_by)

        return query_params.as_dict()

    def get(self, **kwargs):
        """Fetches one or more records, exposes a public API of :class:`pysnow.Response`

        :param kwargs: kwargs to pass along to :class:`requests.Request`
        :return: :class:`pysnow.Response` object
        """

        request_params = self._get_request_params(**kwargs)
        url = self._resource_url.get_url()
        return self._get_response('GET', url, params=request_params)

    def custom(self, method, path_append=None, headers=None, **kwargs):
        """Creates a custom request

        :param method: HTTP method
        :param path_append: (optional) append path to resource.api_path
        :param headers: (optional) Dictionary of headers to add or override
        :param kwargs: kwargs to pass along to :class:`requests.Request`
        :return: :class:`pysnow.Response` object
        """

        if headers:
            self._session.headers.update(headers)

        if path_append is not None:
            try:
                url = self._resource_url.get_appended_custom(path_append)
            except InvalidUsage:
                raise InvalidUsage("Argument 'path_append' must be a string in the following format: "
                                   "/path-to-append[/.../...]")
        else:
            url = self._resource_url.get_url()

        return self._get_response(method, url, **kwargs)

    def insert(self, payload):
        """Creates a new record

        :param payload: Dictionary payload
        :return: Dictionary containing the inserted record
        """

        url = self._resource_url.get_url()
        return self._get_response('POST', url, data=json.dumps(payload)).one()

    def update(self, query, payload):
        """Updates a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param payload: Dictionary payload
        :return: Dictionary containing the updated record
        """

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        record = self.get(query=query).one()

        url = self._resource_url.get_appended_custom("/{}".format(record['sys_id']))
        return self._get_response('PUT', url, data=json.dumps(payload)).one()

    def delete(self, query):
        """Deletes a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :return: Dictionary containing the result
        """
        record = self.get(query=query).one()

        url = self._resource_url.get_appended_custom("/{}".format(record['sys_id']))
        return self._get_response('DELETE', url).one()
