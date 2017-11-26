# -*- coding: utf-8 -*-

import json
import itertools
from functools import wraps
import requests

from .response import Response
from .query import Query

from pysnow.exceptions import (MultipleResults,
                               NoResults,
                               InvalidUsage,
                               ReportUnavailable)


class Request(object):
    _report = None

    def __init__(self, url, *args, **kwargs):
        """Takes arguments used to perform a HTTP request

        :param method: HTTP request method
        """

        self._request_params = kwargs.pop('request_params')
        self._session = kwargs.pop('session')
        self._generator_size = kwargs.pop('generator_size')
        self._enable_reporting = kwargs.pop('enable_reporting', False)
        self._raise_on_empty = kwargs.pop('raise_on_empty')
        self._resource = kwargs.pop('resource')
        self._url = url

        if self._enable_reporting:
            self._report = Report(self._resource)

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

    def one(self, *args, **kwargs):
        kwargs['limit'] = 1
        return next(itertools.chain.from_iterable(self._get_inner(*args, **kwargs)), {})

    def insert(self, payload):
        response = self._send('POST', data=json.dumps(payload))
        return Response(response, raise_on_empty=self._raise_on_empty)

    def update(self, *args, **kwargs):
        payload = kwargs.pop('payload')

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        try:
            result = self.one(*args, **kwargs)
            if 'sys_id' not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults('Update of multiple records is not supported')
        except NoResults as e:
            e.args = ('Cannot update a non-existing record',)
            raise

        response = self._session.put(self._get_url(sys_id=result['sys_id']), data=json.dumps(payload))
        return Response(response, raise_on_empty=self._raise_on_empty).get()

    def delete(self):
        try:
            result = self.get_one()
            if 'sys_id' not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults("Deletion of multiple records is not supported")
        except NoResults as e:
            e.args = ('Cannot delete a non-existing record',)
            raise

        response = self._session.delete(self._get_url(sys_id=result['sys_id']))
        return Response(response, raise_on_empty=self._raise_on_empty).get()


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

