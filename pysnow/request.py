# -*- coding: utf-8 -*-

import logging
import json

from .response import Response
from .exceptions import InvalidUsage

logger = logging.getLogger('pysnow')


class SnowRequest(object):
    """Creates a new :class:`SnowRequest` object.

    :param parameters: :class:`params_builder.ParamsBuilder` object
    :param session: :class:`request.Session` object
    :param url_builder: :class:`url_builder.URLBuilder` object
    """

    def __init__(self, parameters=None, session=None, url_builder=None, chunk_size=None, resource=None):
        self._parameters = parameters
        self._url_builder = url_builder
        self._session = session
        self._chunk_size = chunk_size
        self._resource = resource

        self._url = url_builder.get_url()

    def _get_response(self, method, **kwargs):
        """Response wrapper - creates a :class:`requests.Response` object and passes along to :class:`pysnow.Response`
        for validation and parsing.

        :param args: args to pass along to _send()
        :param kwargs: kwargs to pass along to _send()
        :return:
            - :class:`pysnow.Response` object
        """

        params = self._parameters.as_dict()
        use_stream = kwargs.pop('stream', False)

        logger.debug('(REQUEST_SEND) Method: %s, Resource: %s' % (method, self._resource))

        response = self._session.request(method, self._url, stream=use_stream, params=params, **kwargs)
        response.raw.decode_content = True

        logger.debug('(RESPONSE_RECEIVE) Code: %d, Resource: %s' % (response.status_code, self._resource))

        return Response(response=response, resource=self._resource, chunk_size=self._chunk_size, stream=use_stream)

    def get(self, *args, **kwargs):
        """Fetches one or more records

        :return:
            - :class:`pysnow.Response` object
        """

        self._parameters.query = kwargs.pop('query', {}) if len(args) == 0 else args[0]
        self._parameters.limit = kwargs.pop('limit', 10000)
        self._parameters.offset = kwargs.pop('offset', 0)
        self._parameters.fields = kwargs.pop('fields', kwargs.pop('fields', []))

        return self._get_response('GET', stream=kwargs.pop('stream', False))

    def create(self, payload):
        """Creates a new record

        :param payload: Dictionary payload
        :return:
            - Dictionary of the inserted record
        """

        return self._get_response('POST', data=json.dumps(payload))

    def update(self, query, payload):
        """Updates a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :param payload: Dictionary payload
        :return:
            - Dictionary of the updated record
        """

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        record = self.get(query).one()

        self._url = self._url_builder.get_appended_custom("/{0}".format(record['sys_id']))
        return self._get_response('PUT', data=json.dumps(payload))

    def delete(self, query):
        """Deletes a record

        :param query: Dictionary, string or :class:`QueryBuilder` object
        :return:
            - Dictionary containing status of the delete operation
        """

        record = self.get(query=query).one()

        self._url = self._url_builder.get_appended_custom("/{0}".format(record['sys_id']))
        return self._get_response('DELETE').one()

    def custom(self, method, path_append=None, headers=None, **kwargs):
        """Creates a custom request

        :param method: HTTP method
        :param path_append: (optional) append path to resource.api_path
        :param headers: (optional) Dictionary of headers to add or override
        :param kwargs: kwargs to pass along to :class:`requests.Request`
        :return:
            - :class:`pysnow.Response` object
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
