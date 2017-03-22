# -*- coding: utf-8 -*-

import os
import ntpath
import requests
import json
import itertools
import inspect

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.3.1"


class UnexpectedResponse(Exception):
    """Informs the user about what went wrong when interfacing with the API

    :param code_expected: Expected HTTP status code
    :param code_actual: Actual HTTP status code
    :param http_method: HTTP method used
    :param error_summary: Summary of what went wrong
    :param error_details: Details about the error
    """
    def __init__(self, code_expected, code_actual, http_method, error_summary, error_details):
        if code_expected == code_actual:
            message = "Unexpected response on HTTP %s from server: %s" % (
                http_method,
                error_summary
            )
        else:
            message = "Unexpected HTTP %s response code. Expected %d, got %d" % (
                http_method,
                code_expected,
                code_actual
            )

        super(UnexpectedResponse, self).__init__(message)
        self.error_summary = error_summary
        self.error_details = error_details


class InvalidUsage(Exception):
    pass


class MultipleResults(Exception):
    pass


class NoResults(Exception):
    pass


class QueryTypeError(TypeError):
    pass


class QueryMissingField(Exception):
    pass


class QueryEmpty(Exception):
    pass


class QueryExpressionError(Exception):
    pass


class QueryMultipleExpressions(Exception):
    pass


class QueryBuilder(object):
    def __init__(self):
        """Query builder - used for building complex queries"""
        self._query = []
        self.current_field = None
        self.c_oper = None
        self.l_oper = None

    def AND(self):
        """Operator for use between expressions"""
        return self._add_logical_operator('^')

    def OR(self):
        """Operator for use between expressions"""
        return self._add_logical_operator('^OR')

    def NQ(self):
        """Operator for use between expressions"""
        return self._add_logical_operator('^NQ')

    def field(self, field):
        """ Sets the field to operate on

        :param field: field (str) to operate on
        :return: self
        """
        self.current_field = field
        return self

    def starts_with(self, value):
        """Query records with the given field starting with the value specified"""
        return self._add_condition('STARTSWITH', value, types=[str])

    def ends_with(self, value):
        """Query records with the given field ending with the value specified"""
        return self._add_condition('ENDSWITH', value, types=[str])

    def contains(self, value):
        """Query records with the given field containing the value specified"""
        return self._add_condition('LIKE', value, types=[str])

    def not_contains(self, value):
        """Query records with the given field not containing the value specified"""
        return self._add_condition('NOTLIKE', value, types=[str])

    def is_empty(self):
        """Query records with the given field empty"""
        return self._add_condition('ISEMPTY', '', types=[str, int])

    def equals(self, value):
        """Query records with the given field equalling the value specified"""
        return self._add_condition('=', value, types=[int, str])

    def not_equals(self, value):
        """Query records with the given field not equalling the value specified"""
        return self._add_condition('!=', value, types=[int, str])

    def greater_than(self, value):
        """Query records with the given field greater than the value specified"""
        if hasattr(value, 'strftime'):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, str):
            raise QueryTypeError('Expected value of type `int` or instance of `datetime`, not %s' % type(value))

        return self._add_condition('>', value, types=[int, str])

    def less_than(self, value):
        """Query records with the given field less than the value specified"""
        if hasattr(value, 'strftime'):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, str):
            raise QueryTypeError('Expected value of type `int` or instance of `datetime`, not %s' % type(value))

        return self._add_condition('<', value, types=[int, str])

    def between(self, start, end):
        """Query records in a start and end range

        :param start: `int` or `datetime` object
        :param end: `int` or `datetime` object
        :raise:
            :QueryTypeError: if start or end arguments is of an invalid type
        :return: self
        """
        if hasattr(start, 'strftime') and hasattr(end, 'strftime'):
            dt_between = (
              'javascript:gs.dateGenerate("%(start)s")'
              "@"
              'javascript:gs.dateGenerate("%(end)s")'
            ) % {
              'start': start.strftime('%Y-%m-%d %H:%M:%S'),
              'end': end.strftime('%Y-%m-%d %H:%M:%S')
            }
        elif isinstance(start, int) and isinstance(end, int):
            dt_between = '%d@%d' % (start, end)
        else:
            raise QueryTypeError("Expected `start` and `end` of type `int` "
                                 "or instance of `datetime`, not %s and %s" % (type(start), type(end)))

        return self._add_condition('BETWEEN', dt_between, types=[str])

    def _add_condition(self, operator, value, types):
        """ Appends condition to self._query after performing validation

        :param operator: operator (str)
        :param value: value / operand
        :param types: allowed types
        :raise:
            :QueryMissingField: if a field hasn't been set
            :QueryMultipleExpressions: if a condition already has been set
            :QueryTypeError: if the value is of an unexpected type
        :return: self
        """
        if not self.current_field:
            raise QueryMissingField("Expressions requires a field()")
        elif not type(value) in types:
            caller = inspect.currentframe().f_back.f_code.co_name
            raise QueryTypeError("Invalid type passed to %s() , expected: %s" % (caller, types))
        elif self.c_oper:
            raise QueryMultipleExpressions("Expected logical operator after expression")

        self.c_oper = inspect.currentframe().f_back.f_code.co_name
        self._query.append("%(current_field)s%(operator)s%(value)s" % {
                               'current_field': self.current_field,
                               'operator': operator,
                               'value': value})
        return self

    def _add_logical_operator(self, operator):
        """ Adds a logical operator between expressions in query

        :param operator: logical operator (str)
        :raise:
            :QueryExpressionError: if a expression hasn't been set
        :return: self
        """
        if not self.c_oper:
            raise QueryExpressionError("Logical operators must be preceded by a expression")

        self.current_field = None
        self.c_oper = None

        self.l_oper = inspect.currentframe().f_back.f_code.co_name
        self._query.append(operator)
        return self

    def __str__(self):
        """ String representation of the query object
        :raise:
            :QueryEmpty: if there's no expression defined
            :QueryMissingField: if field() hasn't been set
            :QueryExpressionError: if a expression hasn't been set
        :return: Query string
        """
        if len(self._query) == 0:
            raise QueryEmpty("At least one expression is required")
        elif self.current_field is None:
            raise QueryMissingField("Logical operator expects a field()")
        elif self.c_oper is None:
            raise QueryExpressionError("field() expects a expression")

        return str().join(self._query)


# For backwards compatibility
class Query(QueryBuilder):
    pass


class Client(object):
    def __init__(self, instance, user, password, raise_on_empty=True, default_payload=None):
        """Sets configuration and creates a session object used in `Request` later on

        :param instance: instance name, used to resolve FQDN in `Request`
        :param user: username
        :param password: password
        :param raise_on_empty: whether or not to raise an exception on 404 (no matching records)
        :param default_payload: default payload to send with all requests, set i.e. 'sysparm_limit' here
        """
        # Connection properties
        self.instance = instance
        self._user = user
        self._password = password
        self.raise_on_empty = raise_on_empty
        self.default_payload = default_payload or dict()

        # Sets default payload for all requests, i.e. sysparm_limit, sysparm_offset etc
        if not isinstance(self.default_payload, dict):
            raise InvalidUsage("Payload must be of type dict")

        # Create new session object
        self.session = self._create_session()

    def _create_session(self):
        """Creates and returns a new session object with the credentials passed to the constructor

        :return: session object
        """
        s = requests.Session()
        s.auth = requests.auth.HTTPBasicAuth(self._user, self._password)
        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})
        return s

    def _request(self, method, table, **kwargs):
        """Creates and returns a new `Request` object, takes some basic settings from the `Client` object and
        passes along to the `Request` constructor

        :param method: HTTP method
        :param table: Table to operate on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """
        return Request(method,
                       table,
                       default_payload=self.default_payload,
                       raise_on_empty=self.raise_on_empty,
                       session=self.session,
                       instance=self.instance,
                       **kwargs)

    def query(self, table, **kwargs):
        """Query wrapper method.

        :param table: table to perform query on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """
        return self._request('GET', table, **kwargs)

    def insert(self, table, payload, **kwargs):
        """Creates a new `Request` object and calls insert()

        :param table: table to insert on
        :param payload: update payload (dict)
        :param kwargs: Keyword arguments passed along to `Request`
        :return: New record content
        """
        r = self._request('POST', table, **kwargs)
        return r.insert(payload)


class Request(object):
    base = "api/now"

    def __init__(self, method, table, **kwargs):
        """Takes arguments used to perform a HTTP request

        :param method: HTTP request method
        :param table: table to operate on
        """
        self.method = method
        self.table = table
        self.url_link = None  # Updated when a linked request is iterated on
        self.fqdn = "%s.service-now.com" % kwargs.pop('instance')
        self.default_payload = kwargs.pop('default_payload')
        self.raise_on_empty = kwargs.pop('raise_on_empty')
        self.session = kwargs.pop('session')
        self.status_code = None

        if method in ('GET', 'DELETE'):
            self.query = kwargs.pop('query')

    def _all_inner(self, fields):
        """Yields all records for the query and follows links if present on the response after validating

        :return: List of records with content
        """
        response = self.session.get(self._get_url(self.table), params=self._get_formatted_query(fields))
        yield self._get_content(response)
        while 'next' in response.links:
            self.url_link = response.links['next']['url']
            response = self.session.get(self.url_link)
            yield self._get_content(response)

    def get_all(self, fields=list()):
        """Wrapper method that takes whatever was returned by the _all_inner() generators and chains it in one result

        :param fields: List of fields to return in the result
        :return: Iterable chain object
        """
        return itertools.chain.from_iterable(self._all_inner(fields))

    def get_one(self, fields=list()):
        """Convenience function for queries returning only one result. Validates response before returning.

        :param fields: List of fields to return in the result
        :raise:
            :MultipleResults: if more than one match is found
        :return: Record content
        """
        response = self.session.get(self._get_url(self.table), params=self._get_formatted_query(fields))
        content = self._get_content(response)
        l = len(content)
        if l > 1:
            raise MultipleResults('Multiple results for one()')

        return content[0]

    def insert(self, payload):
        """Inserts a new record with the payload passed as an argument

        :param payload: The record to create (dict)
        :return: Created record
        """
        response = self.session.post(self._get_url(self.table), data=json.dumps(payload))
        return self._get_content(response)   # @TODO - update to return first key (API breakage)

    def delete(self):
        """Deletes the queried record and returns response content after response validation

        :raise:
            :NoResults: if query returned no results
            :NotImplementedError: if query returned more than one result (currently not supported)
        :return: Delete response content (Generally always {'Success': True})
        """
        try:
            try:
                sys_id = self.get_one()['sys_id']
            except KeyError:
                raise NoResults('Attempted to delete a non-existing record')
        except MultipleResults:
            raise NotImplementedError("Deletion of multiple records is not supported")
        response = self.session.delete(self._get_url(self.table, sys_id))
        return self._get_content(response)

    def update(self, payload):
        """Updates the queried record with `payload` and returns the updated record after validating the response

        :param payload: Payload to update the record with
        :raise:
            :NoResults: if query returned no results
            :NotImplementedError: if query returned more than one result (currently not supported)
        :return: The updated record
        """
        try:
            try:
                sys_id = self.get_one()['sys_id']
            except KeyError:
                raise InvalidUsage('Attempted to update a non-existing record')
        except MultipleResults:
            raise NotImplementedError("Update of multiple records is not supported")

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        response = self.session.put(self._get_url(self.table, sys_id), data=json.dumps(payload))
        return self._get_content(response)   # @TODO - update to return first key (API breakage)

    def attach(self, file):
        """Attaches the queried record with `file` and returns the response after validating the response

        :param file: File to attach to the record
        :raise:
            :NoResults: if query returned no results
            :NotImplementedError: if query returned more than one result (currently not supported)
        :return: The attachment record metadata
        """
        try:
            try:
                sys_id = self.get_one()['sys_id']
            except KeyError:
                raise InvalidUsage('Attempted to update a non-existing record')
        except MultipleResults:
            raise NotImplementedError("Update of multiple records is not supported")

        if not os.path.isfile(file):
            raise InvalidUsage("Attachment '%s' must be an existing regular file" % file)

        response = self.session.post(
            self._get_attachment_url(),
            data={
                'table_name': self.table,
                'table_sys_id': sys_id,
                'file_name': ntpath.basename(file)
            },
            files={'file': open(file, 'rb')},
            headers={'content-type': None}  # Temporarily override header
        )
        return self._get_content(response)

    def _get_content(self, response):
        """Checks for errors in the response. Returns response content, in bytes.

        :param response: response object
        :raise:
            :UnexpectedResponse: if the server responded with an unexpected response
        :return: ServiceNow response content
        """
        method = response.request.method
        self.status_code = response.status_code

        server_error = {
            'summary': None,
            'details': None
        }

        try:
            content_json = response.json()
            if 'error' in content_json:
                e = content_json['error']
                if 'message' in e:
                    server_error['summary'] = e['message']
                if 'detail' in e:
                    server_error['details'] = e['detail']
        except ValueError:
            content_json = {}

        if method == 'DELETE':
            # Make sure the delete operation returned the expected response
            if response.status_code == 204:
                return {'success': True}
            else:
                raise UnexpectedResponse(
                    204, response.status_code, method,
                    server_error['summary'], server_error['details']
                )
        # Make sure the POST operation returned the expected response
        elif method == 'POST' and response.status_code != 201:
            raise UnexpectedResponse(
                201, response.status_code, method,
                server_error['summary'], server_error['details']
            )
        # It seems that Helsinki and later returns status 200 instead of 404 on empty result sets
        if ('result' in content_json and len(content_json['result']) == 0) or response.status_code == 404:
            if self.raise_on_empty is False:
                content_json['result'] = [{}]
            else:
                raise NoResults('Query yielded no results')
        elif 'error' in content_json:
            raise UnexpectedResponse(
                200, response.status_code, method,
                server_error['summary'], server_error['details']
            )

        return content_json['result']

    def _get_url(self, table, sys_id=None):
        """Takes table and sys_id (if present), and returns a URL

        :param table: ServiceNow table
        :param sys_id: Record sys_id
        :return: url string
        """
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

        if sys_id:
            return "%s/%s" % (url_str, sys_id)

        return url_str

    def _get_attachment_url(self, sys_id=None):
        """Takes sys_id (if present), and returns an attachment URL

        :param sys_id: Record sys_id
        :return: url string
        """
        url_str = 'https://%(fqdn)s/%(base)s/attachment' % (
            {
                'fqdn': self.fqdn,
                'base': self.base
            }
        )

        if sys_id:
            url_str = "%s/%s" % (url_str, sys_id)

        return "%s/%s" % (url_str, "upload")

    def _get_formatted_query(self, fields):
        """
        Converts the query to a ServiceNow-interpretable format
        :return: ServiceNow query
        """

        if isinstance(self.query, QueryBuilder):
            sysparm_query = str(self.query)
        elif isinstance(self.query, dict):  # Dict-type query
            try:
                items = self.query.iteritems()  # Python 2
            except AttributeError:
                items = self.query.items()  # Python 3

            sysparm_query = '^'.join(['%s=%s' % (field, value) for field, value in items])
        elif isinstance(self.query, str):  # String-type query
            sysparm_query = self.query
        else:
            raise InvalidUsage("Query must be instance of %s, %s or %s" % (QueryBuilder, str, dict))

        result = {'sysparm_query': sysparm_query}
        result.update(self.default_payload)

        if len(fields) > 0:
            if isinstance(fields, list):
                result.update({'sysparm_fields': ",".join(fields)})
            else:
                raise InvalidUsage("You must pass the fields as a list")

        return result
