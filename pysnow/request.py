# -*- coding: utf-8 -*-

import json
import itertools
import requests

from .response import Response
from .query import Query

from pysnow.exceptions import (MultipleResults,
                               NoResults,
                               InvalidUsage,
                               ReportUnavailable)


class Request(object):
    """Creates a new :class:`Request <Request>` object.

    :param request_params: Request parameters

    """

    def __init__(self,
                 request_params=None, session=None, generator_size=None,
                 enable_reporting=False, raise_on_empty=True, resource=None,
                 base_url=None, base_path=None, api_path=None):

        self._request_params = request_params
        self._session = session
        self._generator_size = generator_size
        self._enable_reporting = enable_reporting
        self._raise_on_empty = raise_on_empty
        self._resource = resource

        self._base_url = base_url
        self._base_path = base_path
        self._api_path = api_path

        self._url = self._get_url()

        if self._enable_reporting:
            self._report = Report(self._resource)
        else:
            self._report = None

    def _get_url(self, api_path_override=None, sys_id=None):
        api_path = api_path_override or self._api_path
        url_str = self._base_url + self._base_path + api_path

        if sys_id:
            return "%s/%s" % (url_str, sys_id)

        return url_str

    def _send(self, *args, **kwargs):
        url = kwargs.pop('url', self._url)

        request = requests.Request(*args, **kwargs, url=url, auth=self._session.auth)
        prepared = request.prepare()
        response = self._session.send(prepared)

        if self._enable_reporting:
            self._report.add_response(response)

        return response

    def _get_inner(self, *args, **kwargs):
        request_params = self._get_request_params(*args, **kwargs)

        if self._enable_reporting:
            self._report.enable(request_params=request_params)

        r = self._send('GET', params=request_params)
        yield Response(r, raise_on_empty=self._raise_on_empty).result

        while 'next' in r.links:
            r = self._send('GET', url=r.links['next']['url'])
            yield Response(r, raise_on_empty=self._raise_on_empty).result

    def _get_request_params(self, query=None, fields=list(), limit=None, order_by=list(), offset=None):
        query_params = Query(query, self._request_params)

        if not limit:
            query_params.set_generator_size(self._generator_size)

        query_params.filter(fields=fields,
                            limit=limit,
                            offset=offset)

        query_params.sort(order_by=order_by)

        return query_params.as_dict()

    def get_report(self):
        if not self._enable_reporting:
            raise ReportUnavailable("Set `enable_reporting` to True to enable.")

        return self._report

    def all(self, *args, **kwargs):
        return itertools.chain.from_iterable(self._get_inner(*args, **kwargs))

    def insert(self, payload):
        return Response(self._send('POST', data=json.dumps(payload)),
                        raise_on_empty=self._raise_on_empty)

    def update(self, *args, **kwargs):
        payload = kwargs.pop('payload')

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        result = list(self.all(*args, **kwargs))
        if len(result) < 1:
            raise NoResults('Cannot update non-existing record')
        elif len(result) > 1:
            raise MultipleResults('Updating multiple records is not supported')

        url = self._get_url(sys_id=result[0]['sys_id'])
        return Response(self._send('PUT', url=url, data=json.dumps(payload)),
                        raise_on_empty=self._raise_on_empty)

    def delete(self, *args, **kwargs):
        result = list(self.all(*args, **kwargs))
        if len(result) < 1:
            raise NoResults('Cannot delete non-existing record')
        elif len(result) > 1:
            raise MultipleResults('Deleting multiple records is not supported')

        url = self._get_url(sys_id=result[0]['sys_id'])
        return Response(self._send('DELETE', url=url),
                        raise_on_empty=self._raise_on_empty)


class Report(object):
    records = 0
    responses = []
    request_params = {}

    def __init__(self, resource):
        self.resource = resource

    def enable(self, request_params):
        self.records = 0
        self.responses = []
        self.request_params = request_params

    def add_response(self, response):
        self.responses.append(response)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __repr__(self):
        return "%s %s" % (self.__class__, self.__dict__)
