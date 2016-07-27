# -*- coding: utf-8 -*-

"""
Python client for the ServiceNow REST API
"""

import requests
import json
import itertools
from requests.auth import HTTPBasicAuth

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.1.0"


class UnexpectedResponse(Exception):
    pass


class InvalidUsage(Exception):
    pass


class MultipleResults(Exception):
    pass


class MultipleResultsDelete(Exception):
    pass


class NoResults(Exception):
    pass


class Client(object):
    def __init__(self, instance, user, password, **kwargs):
        # Connection properties
        self.instance = instance
        self.fqdn = "%s.service-now.com" % instance
        self._user = user
        self._password = password
        self.base = "api/now"

        self.raise_on_empty = kwargs.pop('raise_on_empty', True)
        self.default_payload = kwargs.pop('default_payload', {})

        # Sets default payload for all requests, i.e. sysparm_limit, sysparm_offset etc
        if not isinstance(self.default_payload, dict):
            raise InvalidUsage("Payload must be of type dict")

        self.session = self._create_session()

    def _create_session(self):
        """
        Creates and returns a new session object with the credentials passed to the constructor
        :return: session object
        """
        s = requests.Session()
        s.auth = HTTPBasicAuth(self._user, self._password)
        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})
        return s

    def _request(self, method, table, **kwargs):
        kwargs.update(self.__dict__)
        return Request(method, table, **kwargs)

    def get(self, table, **kwargs):
        return self._request('GET', table, **kwargs)

    def insert(self, table, payload, **kwargs):
        r = self._request('POST', table, **kwargs)
        return r.insert(payload)

    def delete(self, table, **kwargs):
        r = self._request('DELETE', table, **kwargs)
        return r.delete()

    def delete_multiple(self, table, **kwargs):
        r = self._request('DELETE', table, **kwargs)
        return r.delete_multiple()


class Request(object):
    def __init__(self, method, table, **kwargs):
        self.method = method
        self.table = table
        self.url_link = None

        # Get `Client` properties
        self.default_payload = kwargs.pop('default_payload')
        self.raise_on_empty = kwargs.pop('raise_on_empty')
        self.session = kwargs.pop('session')
        self.base = kwargs.pop('base')
        self.fqdn = kwargs.pop('fqdn')

        if method in ('GET', 'DELETE'):
            self.query = kwargs.pop('query')
            self.fields = kwargs.pop('fields', None)
            self.query_formatted = self._get_formatted_query()

    def _all_inner(self):
        response = self.session.get(self._get_url(self.table), params=self.query_formatted)
        yield self._get_content(response)
        while 'next' in response.links:
            self.url_link = response.links['next']['url']
            response = self.session.get(self.url_link)
            yield self._get_content(response)

    def all(self):
        return itertools.chain.from_iterable(self._all_inner())

    def one(self):
        response = self.session.get(self._get_url(self.table), params=self.query_formatted)
        content = self._get_content(response)
        l = len(content)
        if l == 1:
            return content[0]
        elif l == 0:
            raise NoResults('No results for one()')
        else:
            raise MultipleResults('Multiple results for one()')

    def insert(self, payload):
        response = self.session.post(self._get_url(self.table), data=json.dumps(payload))
        return self._get_content(response)

    def delete(self):
        try:
            sys_id = self.one()['sys_id']
        except MultipleResults:
            raise MultipleResultsDelete("Matched multiple records when attempting to delete. "
                                        "Use delete_multiple() if you know what you're doing.")
        response = self.session.delete(self._get_url(self.table, sys_id))
        return self._get_content(response)

    def delete_multiple(self):
        raise NotImplementedError

    def update(self, payload):
        sys_id = self.one()['sys_id']
        response = self.session.put(self._get_url(self.table, sys_id), data=json.dumps(payload))
        return self._get_content(response)

    def _get_content(self, response):
        """
        Checks for errors in the response object. Returns response content, in bytes.
        :param response: response object
        :return: ServiceNow response content
        """

        method = response.request.method

        if method == 'DELETE':
            if response.status_code != 204:
                raise UnexpectedResponse("Unexpected HTTP response code. Expected: 204, got %d" % response.status_code)
            else:
                return {'success': True}
        elif method == 'POST' and response.status_code != 201:
            raise UnexpectedResponse("Unexpected HTTP response code. Expected: 201, got %d" % response.status_code)

        content_json = response.json()

        if response.status_code == 404 and self.raise_on_empty is False:
            content_json['result'] = []
        elif 'error' in content_json:
            raise UnexpectedResponse("ServiceNow responded (%i): %s" % (response.status_code,
                                                                        content_json['error']['message']))

        return content_json['result']

    def _get_url(self, table, sysid=None):
        if table == 'attachment':
            base = self.base
        else:
            base = "%s/%s" % (self.base, "table")

        url_str = 'https://%(fqdn)s/%(base)s/%(table)s' % (
            {
                'fqdn': self.fqdn,
                'base': base,
                'table': table
            }
        )

        if sysid:
            return "%s/%s" % (url_str, sysid)

        return url_str

    def _get_formatted_query(self):
        """ Converts the query to a ServiceNow-interpretable format
        :return: ServiceNow query
        """

        if isinstance(self.query, dict):  # Dict-type query
            try:
                items = self.query.iteritems()  # Python 2
            except AttributeError:
                items = self.query.items()  # Python 3

            sysparm_query = '^'.join(['%s=%s' % (field, value) for field, value in items])
        elif isinstance(self.query, str):  # String-type query
            sysparm_query = self.query
        else:
            raise InvalidUsage("You must pass a query using either a dictionary or string (for advanced queries)")

        result = {'sysparm_query': sysparm_query}
        result.update(self.default_payload)

        if self.fields is not None:
            if isinstance(self.fields, list):
                result.update({'sysparm_fields': ",".join(self.fields)})
            else:
                raise InvalidUsage("You must pass the fields as a list")

        return result

