# -*- coding: utf-8 -*-
import unittest
import httpretty
import json

from pysnow.response import Response
from pysnow.client import Client


class TestResource(unittest.TestCase):
    """Performs basic request/response integration tests for :class:`Resource`,
    more detailed tests are available in the test_request and test_response modules"""

    def setUp(self):
        api_path = '/api/path'
        base_path = '/base/path'

        self.mock_client = {
            'user': 'mock_user',
            'password': 'mock_password',
            'instance': 'mock_instance',
            'generator_size': 50,
        }

        self.mock_resource_path = {
            'api_path': api_path,
            'base_path': base_path
        }

        self.mock_sys_id = "98ace1a537ea2a00cf5c9c9953990e19"
        self.mock_query = "sys_id=%s" % self.mock_sys_id

        self.client = Client(**self.mock_client)

        self.mock_url = self.client.base_url + base_path + api_path
        self.mock_url_put = self.mock_url_delete = "%s/%s" % (self.mock_url, self.mock_sys_id)

    def test_create_resource(self):
        """:class:`Resource` object repr type should be string, and its path should be set to api_path + base_path """

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        resource_repr = type(repr(r))

        path = self.mock_resource_path['base_path'] + self.mock_resource_path['api_path']

        self.assertEquals(resource_repr, str)
        self.assertEquals(r.path, path)

    @httpretty.activate
    def test_integration_get(self):
        """:meth:`get` should return a :class:`pysnow.Response` object"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url,
                               status=200,
                               content_type="application/json")

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        response = r.get(self.mock_query)

        self.assertEquals(type(response), Response)

    @httpretty.activate
    def test_integration_insert(self):
        """:meth:`insert` should return a dictionary of the new record"""

        response = {'foo': 'bar'}
        json_body = json.dumps({'result': [response]})
        httpretty.register_uri(httpretty.POST,
                               self.mock_url,
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        result = r.insert(response)

        self.assertEquals(type(result), dict)
        self.assertEquals(result['foo'], response['foo'])

    @httpretty.activate
    def test_integration_update(self):
        """:meth:`update` should return a dictionary of the updated record"""

        get_response = {'sys_id': self.mock_sys_id}
        get_json_body = json.dumps({'result': [get_response]})
        httpretty.register_uri(httpretty.GET,
                               self.mock_url,
                               body=get_json_body,
                               status=200,
                               content_type="application/json")

        put_response = {'foo': 'bar'}
        put_json_body = json.dumps({'result': [put_response]})
        httpretty.register_uri(httpretty.PUT,
                               self.mock_url_put,
                               body=put_json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        result = r.update(self.mock_query, put_response)

        self.assertEquals(type(result), dict)
        self.assertEquals(result['foo'], put_response['foo'])

    @httpretty.activate
    def test_integration_delete(self):
        """:meth:`delete` should return a dictionary containing status"""

        get_response = {'sys_id': self.mock_sys_id}
        get_json_body = json.dumps({'result': [get_response]})
        httpretty.register_uri(httpretty.GET,
                               self.mock_url,
                               body=get_json_body,
                               status=200,
                               content_type="application/json")

        put_response = {'foo': 'bar'}
        put_json_body = json.dumps({'result': [put_response]})
        httpretty.register_uri(httpretty.DELETE,
                               self.mock_url_delete,
                               body=put_json_body,
                               status=204,
                               content_type="application/json")

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        result = r.delete(get_response)

        self.assertEquals(type(result), dict)
        self.assertEquals(result['status'], 'record deleted')

    @httpretty.activate
    def test_integration_custom(self):
        """:meth:`custom` should return a :class:`pysnow.Response` object"""

        get_response = {'sys_id': self.mock_sys_id}
        get_json_body = json.dumps({'result': [get_response]})
        httpretty.register_uri(httpretty.GET,
                               self.mock_url,
                               body=get_json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.resource(api_path=self.mock_resource_path['api_path'],
                                 base_path=self.mock_resource_path['base_path'])

        response = r.custom('GET')

        self.assertEquals(type(response), Response)

