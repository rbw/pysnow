# -*- coding: utf-8 -*-

import itertools
import json
import os
import ntpath
import six
import pysnow

from requests.exceptions import HTTPError

from pysnow.exceptions import (ResponseError,
                               MultipleResults,
                               NoResults,
                               InvalidUsage,
                               UnexpectedResponseFormat,
                               MissingResult)


from functools import wraps


def generator_response(func):
    @wraps(func)
    def f(*args, **kwargs):
        self = args[0]
        r = func(*args, **kwargs)

        yield RequestResponse(r, raise_on_empty=self._raise_on_empty).result
        while 'next' in r.links:
            r = self._send(r.links['next']['url'])
            yield RequestResponse(r, raise_on_empty=self._raise_on_empty).result

    return f


class ResponseLogger(object):
    records = 0
    responses = []
    request_params = None

    def enable(self, request_params):
        self.records = 0
        self.responses = []
        self.request_params = request_params

    def add_response(self, response):
        if 'X-Total-Count' in response.headers:
            self.records = int(response.headers['X-Total-Count'])

        self.responses.append({
            'url': response.url,
            'status_code': response.status_code
        })

    def get(self):
        return self.__dict__


class Request(object):
    def __init__(self, **kwargs):
        """Takes arguments used to perform a HTTP request

        :param method: HTTP request method
        """

        self._api_path = kwargs.pop('api_path')
        self._base_url = kwargs.pop('base_url')
        self._request_params = kwargs.pop('request_params')
        self._raise_on_empty = kwargs.pop('raise_on_empty')
        self._session = kwargs.pop('session')
        self._enable_logger = kwargs.pop('enable_response_logger')
        self._base_path = kwargs.pop('base_path', 'api/now')
        self._generator_size = kwargs.pop('generator_size')
        self._query = kwargs.pop('query', {})

        self._url = self._get_url()

        if self._enable_logger:
            self._logger = ResponseLogger()

    def get_response_log(self):
        return self._logger.get()

    def _send(self, *args, **kwargs):
        response = self._session.get(*args, **kwargs)

        if self._logger:
            self._logger.add_response(response)

        return response

    @generator_response
    def _get_inner(self, *args, **kwargs):
        """Yields all records for the query and follows links if present on the response after validating

        :return: List of records with content
        """

        request_params = self._get_request_params(*args, **kwargs)

        if self._enable_logger:
            self._logger.enable(request_params=request_params)

        response = self._send(self._url, params=self._get_request_params(*args, **kwargs))

        return response

    def _get_request_params(self, fields=list(), limit=None, order_by=list(), offset=None):
        query_params = RequestQuery(self._query, self._request_params)
        query_params.filter(fields=fields,
                            limit=limit,
                            offset=offset)
        query_params.set_generator_size(self._generator_size)
        query_params.sort(order_by=order_by)

        return query_params.as_dict()

    def get_multiple(self, *args, **kwargs):
        """Wrapper method that takes whatever was returned by the _all_inner() generators and chains it in one result

        The response can be sorted by passing a list of fields to order_by.

        Example:
        get_multiple(order_by=['category', '-created_on']) would sort the category field in ascending order,
        with a secondary sort by created_on in descending order.

        :param fields: List of fields to return in the result
        :param limit: Limits the number of records returned
        :param order_by: Sort response based on certain fields
        :param offset: A number of records to skip before returning records (for pagination)
        :return: Iterable chain object
        """

        return itertools.chain.from_iterable(self._get_inner(*args, **kwargs))

    def get_first(self, fields=list()):
        """Convenience method that returns the next item from the iterator

        :param fields: List of fields to return in the result
        :return: dict result
        """

        return next(itertools.chain.from_iterable(self._get_inner(fields)))

    def insert(self, payload):
        """Inserts a new record with the payload passed as an argument

        :param payload: The record to create (dict)
        :return: Created record
        """
        response = self._session.post(self._url, data=json.dumps(payload))
        return RequestResponse(response, raise_on_empty=self._raise_on_empty).get()

    def delete(self):
        """Deletes the queried record and returns response content after response validation

        :raise:
            :NoResults: if query returned no results
            :NotImplementedError: if query returned more than one result (currently not supported)
        :return: Delete response content (Generally always {'Success': True})
        """
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
        return RequestResponse(response, raise_on_empty=self._raise_on_empty).get()

    def update(self, query, payload, multi=False, upsert=False):
        """Updates the queried record with `payload` and returns the updated record after validating the response

        :param payload: Payload to update the record with
        :raise:
            :NoResults: if query returned no results
            :MultipleResults: if query returned more than one result (currently not supported)
        :return: The updated record
        """

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        try:
            result = self.get_one(query)
            if 'sys_id' not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults('Update of multiple records is not supported')
        except NoResults as e:
            e.args = ('Cannot update a non-existing record',)
            raise

        response = self._session.put(self._get_url(sys_id=result['sys_id']), data=json.dumps(payload))
        return RequestResponse(response, raise_on_empty=self._raise_on_empty).get()

    def _get_url(self, api_path_override=None, sys_id=None):
        """Takes table and sys_id (if present), and returns a URL

        :param api_path_override: Resource name
        :param sys_id: Record sys_id
        :return: url string
        """

        url_str = '%(base_url)s/%(base_path)s/%(api_path)s' % (
            {
                'base_url': self._base_url,
                'base_path': self._base_path,
                'api_path': api_path_override or self._api_path
            }
        )

        if sys_id:
            return "%s/%s" % (url_str, sys_id)

        return url_str


class RequestResponse(object):
    def __init__(self, response, raise_on_empty):
        self.method = response.request.method
        self.status_code = response.status_code
        self._raise_on_empty = raise_on_empty

        self.response = response
        self._content = self._parse_response(response)

    def _parse_response(self, response):
        try:
            response = response.json()
        except ValueError:
            raise UnexpectedResponseFormat('Expected JSON in response, got something else. '
                                           'Have you enabled the REST API in ServiceNow?')

        return self._validate_response(response)

    def _validate_response(self, response):
        if 'error' in response:
            raise ResponseError(response['error'])
        elif 'result' not in response:
            raise MissingResult('The expected `result` key was missing in the response from ServiceNow. '
                                'Cannot continue')

        try:
            self.response.raise_for_status()
        except HTTPError:
            # Versions prior to Helsinki returns 404 on empty result sets
            if self.status_code == 404:
                if self._raise_on_empty is True:
                    raise NoResults('Query yielded no results')
                else:
                    return {}
            raise

        # Helsinki and later returns status 200 instead of 404 on empty result sets
        if len(response['result']) < 1:
            if self._raise_on_empty is True:
                raise NoResults('Query yielded no results')

            return {'result': [{}]}

        return response

    @property
    def result(self):
        return self._content['result']


class RequestQuery(object):
    def __init__(self, query, request_params):
        self._query = query or {}
        self._query_parsed = self._parse()
        self._request_params = request_params

    def _parse(self):
        query = self._query
        if isinstance(query, pysnow.QueryBuilder):
            return str(query)
        elif isinstance(query, dict):
            return '^'.join(['%s=%s' % (k, v) for k, v in six.iteritems(query)])
        elif isinstance(query, str):
            return query
        else:
            raise InvalidUsage('Query must be instance of %s, %s or %s' % (pysnow.QueryBuilder, str, dict))

    def sort(self, order_by):
        if not isinstance(order_by, list):
            raise InvalidUsage('order_by must be of type list()')

        for field in order_by:
            if field[0] == '-':
                self._query_parsed += '^ORDERBYDESC%s' % field[1:]
            else:
                self._query_parsed += '^ORDERBY%s' % field

        return self

    def set_generator_size(self, size):
        self._request_params.update({
            'sysparm_limit': size,
        })

    def filter(self, fields=list(), limit=None, offset=None):
        if not isinstance(fields, list):
            raise InvalidUsage('fields must be of type list()')

        if limit:
            self._request_params.update({
                'sysparm_limit': limit,
                'sysparm_suppress_pagination_header': True
            })

        if offset:
            self._request_params.update({'sysparm_offset': offset})

        if len(fields) > 0:
            self._request_params.update({'sysparm_fields': ",".join(fields)})

        return self

    def as_dict(self):
        q = {'sysparm_query': self._query_parsed}
        q.update(self._request_params)
        return q
