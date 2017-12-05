# -*- coding: utf-8 -*-
import unittest
import httpretty
import json
from six.moves.urllib.parse import urlparse, unquote

from pysnow.response import Response
from pysnow.client import Client

from requests.exceptions import HTTPError

from pysnow.exceptions import (
    ResponseError,
    NoResults,
    MultipleResults,
    InvalidUsage,
    MissingResult
)


def get_serialized_result(dict_mock):
    return json.dumps({'result': dict_mock})


def get_serialized_error(dict_mock):
    return json.dumps({'error': dict_mock})


def qs_as_dict(url):
    qs_str = urlparse(url).query
    return dict((x[0], unquote(x[1])) for x in [x.split("=") for x in qs_str.split("&")])


class TestResourceRequest(unittest.TestCase):
    """Performs resource-request tests"""

    def setUp(self):
        self.error_message_body = {
            'message': 'test_message',
            'detail': 'test_details'
        }
        
        self.record_response_get_one = [{
            'sys_id': '98ace1a537ea2a00cf5c9c9953990e19',
            'attr1': 'foo',
            'attr2': 'bar'
        }]

        self.record_response_get_three = [
            {
                'sys_id': '37ea2a00cf5c9c995399098ace1a5e19',
                'attr1': 'foo1',
                'attr2': 'bar1'
            },
            {
                'sys_id': '98ace1a537ea2a00cf5c9c9953990e19',
                'attr1': 'foo2',
                'attr2': 'bar2'
            },
            {
                'sys_id': 'a00cf5c9c9953990e1998ace1a537ea2',
                'attr1': 'foo3',
                'attr2': 'bar3'
            }
        ]

        self.record_response_create = {
            'sys_id': '90e11a537ea2a00cf598ace9c99539c9',
            'attr1': 'foo_create',
            'attr2': 'bar_create'
        }

        self.record_response_update = {
            'sys_id': '2a00cf5c9c99539998ace1a537ea0e19',
            'attr1': 'foo_updated',
            'attr2': 'bar_updated'
        }

        self.record_response_delete = {
            'status': 'record deleted'
        }

        self.client_kwargs = {
            'user': 'mock_user',
            'password': 'mock_password',
            'instance': 'mock_instance'
        }

        self.base_path = '/table/incident'
        self.api_path = '/api/now/test'

        self.client = Client(**self.client_kwargs)
        self.resource = self.client.resource(base_path=self.base_path, api_path=self.api_path)

        self.mock_url_builder = self.resource._url_builder

        self.mock_url_builder_base = self.resource._url_builder.get_url()
        self.mock_url_builder_sys_id = (self.mock_url_builder
                                        .get_appended_custom('/{0}'.format(self.record_response_get_one[0]['sys_id'])))

        self.dict_query = {'sys_id': self.record_response_get_one[0]['sys_id']}
        self.get_fields = ['foo', 'bar']

    def test_create_resource(self):
        """:class:`Resource` object repr type should be string, and its path should be set to api_path + base_path """

        r = self.client.resource(base_path=self.base_path,
                                 api_path=self.api_path)

        resource_repr = type(repr(r))

        self.assertEquals(resource_repr, str)
        self.assertEquals(r._base_path, self.base_path)
        self.assertEquals(r._api_path, self.api_path)
        self.assertEquals(r.path, self.base_path + self.api_path)

    @httpretty.activate
    def test_response_count(self):
        """:prop:`count` of :class:`pysnow.Response` should raise an exception if count is set to non-integer"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)

        self.assertRaises(TypeError, setattr, response, 'count', 'foo')
        self.assertRaises(TypeError, setattr, response, 'count', True)
        self.assertRaises(TypeError, setattr, response, 'count', {'foo': 'bar'})

    @httpretty.activate
    def test_response_error(self):
        """:class:`pysnow.Response` should raise an exception if an error is encountered in the response body"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_error(self.error_message_body),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)

        expected_str = "Error in response. Message: %s, Details: %s" % (self.error_message_body['message'],
                                                                        self.error_message_body['detail'])

        try:
            response.first()
        except ResponseError as e:
            self.assertEquals(str(e), expected_str)

    @httpretty.activate
    def test_get_request_fields(self):
        """:meth:`get_request` should return a :class:`pysnow.Response` object"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query, fields=self.get_fields)
        qs = qs_as_dict(response._response.request.url)

        str_fields = ','.join(self.get_fields)

        # List of fields should end up as comma-separated string
        self.assertEquals(type(response), Response)
        self.assertEquals(qs['sysparm_fields'], str_fields)

    @httpretty.activate
    def test_get_offset(self):
        """offset passed to :meth:`get` should set sysparm_offset in query"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        offset = 5
        response = self.resource.get(self.dict_query, offset=offset)
        qs = qs_as_dict(response._response.request.url)

        self.assertEquals(int(qs['sysparm_offset']), offset)

    @httpretty.activate
    def test_get_limit(self):
        """limit passed to :meth:`get` should set sysparm_limit in QS"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        limit = 2

        response = self.resource.get(self.dict_query, limit=limit)
        qs = qs_as_dict(response._response.request.url)
        self.assertEquals(int(qs['sysparm_limit']), limit)

    @httpretty.activate
    def test_get_one(self):
        """:meth:`one` of :class:`pysnow.Response` should raise an exception if more than one match was found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        result = response.one()

        self.assertEquals(result['sys_id'], self.record_response_get_one[0]['sys_id'])

    @httpretty.activate
    def test_get_all_empty(self):
        """:meth:`all` of :class:`pysnow.Response` should return a list with an empty object if `raise_on_empty`
        is set to False"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result([]),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        response._raise_on_empty = False
        result = list(response.all())

        self.assertEquals(result[0], {})

    @httpretty.activate
    def test_get_one_missing_result_keys(self):
        """:meth:`one` of :class:`pysnow.Response` should raise an exception if none of the expected keys
        was found in the result"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=json.dumps({}),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)

        self.assertRaises(MissingResult, response.one)

    @httpretty.activate
    def test_response_404_not_raise_on_empty(self):
        """:meth:`all` of :class:`pysnow.Response` should return empty record if a 404 response is encountered when
        :prop:`raise_on_empty` is set to False"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=404,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        response._raise_on_empty = False
        result = response.all()
        self.assertEquals(next(result), {})

    @httpretty.activate
    def test_response_404_raise_on_empty(self):
        """:meth:`all` of :class:`pysnow.Response` should raise an exception if a 404 response is encountered when
        :prop:`raise_on_empty` is set to True"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=404,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        response._raise_on_empty = True
        result = response.all()
        self.assertRaises(NoResults, next, result)

    @httpretty.activate
    def test_http_error_get_one(self):
        """:meth:`one` of :class:`pysnow.Response` should raise an HTTPError exception if a
        non-200 response code was encountered"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=500,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        self.assertRaises(HTTPError, response.one)

    @httpretty.activate
    def test_get_one_many(self):
        """:meth:`one` of :class:`pysnow.Response` should raise an exception if more than one match was found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_three),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        self.assertRaises(MultipleResults, response.one)

    @httpretty.activate
    def test_get_one_empty(self):
        """:meth:`one` of :class:`pysnow.Response` should raise an exception if no matches were found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result([]),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        self.assertRaises(NoResults, response.one)

    @httpretty.activate
    def test_get_one_or_none_empty(self):
        """:meth:`one_or_none` of :class:`pysnow.Response` should return `None` if no matches were found """

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result([]),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        result = response.one_or_none()

        self.assertEquals(result, None)

    @httpretty.activate
    def test_get_first_or_none_empty(self):
        """:meth:`first_or_none` of :class:`pysnow.Response` should return None if no records were found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result([]),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        result = response.first_or_none()

        self.assertEquals(result, None)

    @httpretty.activate
    def test_get_first_or_none(self):
        """:meth:`first_or_none` of :class:`pysnow.Response` should return first match if multiple records were found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_three),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        result = response.first_or_none()

        self.assertEquals(result, self.record_response_get_three[0])

    @httpretty.activate
    def test_get_first(self):
        """:meth:`first` of :class:`pysnow.Response` should return first match if multiple records were found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_three),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)
        result = response.first()

        self.assertEquals(result, self.record_response_get_three[0])

    @httpretty.activate
    def test_get_first_empty(self):
        """:meth:`first` of :class:`pysnow.Response` should raise an exception if matches were found"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result([]),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query)

        self.assertRaises(NoResults, response.first)

    @httpretty.activate
    def test_create(self):
        """:meth:`create` should return a dictionary of the new record"""

        httpretty.register_uri(httpretty.POST,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_create),
                               status=200,
                               content_type="application/json")

        result = self.resource.create(self.record_response_create)

        self.assertEquals(type(result), dict)
        self.assertEquals(result, self.record_response_create)

    @httpretty.activate
    def test_update(self):
        """:meth:`update` should return a dictionary of the updated record"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               self.mock_url_builder_sys_id,
                               body=get_serialized_result(self.record_response_update),
                               status=200,
                               content_type="application/json")

        result = self.resource.update(self.dict_query, self.record_response_update)

        self.assertEquals(type(result), dict)
        self.assertEquals(self.record_response_update['attr1'], result['attr1'])

    @httpretty.activate
    def test_update_invalid_payload(self):
        """:meth:`update` should raise an exception if payload is of invalid type"""

        self.assertRaises(InvalidUsage, self.resource.update, self.dict_query, 'foo')
        self.assertRaises(InvalidUsage, self.resource.update, self.dict_query, False)
        self.assertRaises(InvalidUsage, self.resource.update, self.dict_query, 1)
        self.assertRaises(InvalidUsage, self.resource.update, self.dict_query, ('foo', 'bar'))
        self.assertRaises(InvalidUsage, self.resource.update, self.dict_query, ['foo', 'bar'])

    @httpretty.activate
    def test_delete(self):
        """:meth:`delete` should return a dictionary containing status"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               self.mock_url_builder_sys_id,
                               body=get_serialized_result(self.record_response_delete),
                               status=204,
                               content_type="application/json")

        result = self.resource.delete(self.dict_query)

        self.assertEquals(type(result), dict)
        self.assertEquals(result['status'], 'record deleted')

    @httpretty.activate
    def test_custom(self):
        """:meth:`custom` should return a :class:`pysnow.Response` object"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        method = 'GET'

        response = self.resource.custom(method)

        self.assertEquals(response._response.request.method, method)
        self.assertEquals(type(response), Response)

    @httpretty.activate
    def test_custom_with_headers(self):
        """Headers provided to :meth:`custom` should end up in the request"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        headers = {'foo': 'bar'}

        response = self.resource.custom('GET', headers=headers)

        self.assertEquals(response._response.request.headers['foo'], headers['foo'])

    @httpretty.activate
    def test_custom_with_path(self):
        """path_append passed to :meth:`custom` should get appended to the request path"""

        path_append = '/foo'

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base + path_append,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        response = self.resource.custom('GET', path_append='/foo')

        self.assertEquals(response._response.status_code, 200)

    @httpretty.activate
    def test_custom_with_path_invalid(self):
        """:meth:`custom` should raise an exception if the provided path is invalid"""

        self.assertRaises(InvalidUsage, self.resource.custom, 'GET', path_append='foo')
        self.assertRaises(InvalidUsage, self.resource.custom, 'GET', path_append={'foo': 'bar'})
        self.assertRaises(InvalidUsage, self.resource.custom, 'GET', path_append='foo/')
        self.assertRaises(InvalidUsage, self.resource.custom, 'GET', path_append=True)

    @httpretty.activate
    def test_response_repr(self):
        """:meth:`get` should result in response obj repr describing the response"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized_result(self.record_response_get_one),
                               status=200,
                               content_type="application/json")

        response = self.resource.get(query={})
        response_repr = repr(response)

        self.assertEquals(response_repr, '<Response [200 - GET]>')
