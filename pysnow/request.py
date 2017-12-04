# -*- coding: utf-8 -*-

import json
import requests

from .response import Response
from .exceptions import InvalidUsage


class SnowRequest(object):
    """Creates a new :class:`SnowRequest` object.

    :param sysparms: :class:`sysparms.Sysparms` object
    :param session: :class:`request.Session` object
    :param raise_on_empty: Whether or not to raise an exception on 404 (no matching records)
    :param url_builder: :class:`url_builder.URLBuilder` object
    """

    def __init__(self, sysparms=None, session=None, raise_on_empty=True, url_builder=None):
        self._sysparms = sysparms
        self._session = session
        self._raise_on_empty = raise_on_empty
        self._url_builder = url_builder
        self._url = url_builder.get_url()

    def _get_response(self, method, **kwargs):
        """Response wrapper - creates a :class:`requests.Response` object and passes along to :class:`pysnow.Response`
        for validation and parsing.

        :param args: args to pass along to _send()
        :param kwargs: kwargs to pass along to _send()
        :return: :class:`pysnow.Response` object
        """

        prepared = requests.Request(method, self._url, auth=self._session.auth, **kwargs).prepare()

        response = self._session.send(prepared, stream=True)
        response.raw.decode_content = True

        return Response(response, raise_on_empty=self._raise_on_empty)

    def get(self, query, limit=None, offset=None, fields=list()):
        """Fetches one or more records, exposes a public API of :class:`pysnow.Response`

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param limit: Limits the number of records returned
        :param fields: List of fields to include in the response
        created_on in descending order.
        :param offset: Number of records to skip before returning records
        :return: :class:`pysnow.Response` object
        """

        self._sysparms.query = query

        if limit is not None:
            self._sysparms.limit = limit

        if offset is not None:
            self._sysparms.offset = offset

        if len(fields) > 0:
            self._sysparms.fields = fields

        return self._get_response('GET', params=self._sysparms.as_dict())

    def insert(self, payload):
        """Creates a new record

        :param payload: Dictionary payload
        :return: Dictionary containing the inserted record
        """

        self._url = self._url_builder.get_url()
        return self._get_response('POST', data=json.dumps(payload)).one()

    def update(self, query, payload):
        """Updates a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param payload: Dictionary payload
        :return: Dictionary containing the updated record
        """

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        record = self.get(query).one()

        self._url = self._url_builder.get_appended_custom("/{}".format(record['sys_id']))
        return self._get_response('PUT', data=json.dumps(payload)).one()

    def delete(self, query):
        """Deletes a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :return: Dictionary containing the result
        """
        record = self.get(query=query).one()

        self._url = self._url_builder.get_appended_custom("/{}".format(record['sys_id']))
        return self._get_response('DELETE').one()

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
                self._url = self._url_builder.get_appended_custom(path_append)
            except InvalidUsage:
                raise InvalidUsage("Argument 'path_append' must be a string in the following format: "
                                   "/path-to-append[/.../...]")

        return self._get_response(method, **kwargs)