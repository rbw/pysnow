# -*- coding: utf-8 -*-
import unittest
import httpretty
import json

from pysnow.response import Response
from pysnow.client import Client
from pysnow.request import SnowRequest


def get_serialized(dict_mock):
    return json.dumps({'result': [dict_mock]})


class TestResourceRequest(unittest.TestCase):
    """Performs resource-request tests"""

    def setUp(self):
        self.record_response_get = {
            'sys_id': '98ace1a537ea2a00cf5c9c9953990e19',
            'attr1': 'foo',
            'attr2': 'bar'
        }

        self.record_response_insert = {
            'sys_id': '90e11a537ea2a00cf598ace9c99539c9',
            'attr1': 'foo_insert',
            'attr2': 'bar_insert'
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
        self.resource = self.client.resource(base_path=self.base_path, api_path=self.api_path, enable_reporting=True)

        self.mock_url_builder = self.resource._url_builder

        self.mock_url_builder_base = self.resource._url_builder.get_url()
        self.mock_url_builder_sys_id = (self.mock_url_builder
                                        .get_appended_custom('/{}'.format(self.record_response_get['sys_id'])))

        self.dict_query = {'sys_id': self.record_response_get['sys_id']}
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
    def test_get_request_fields(self):
        """:meth:`get_request` should return a :class:`pysnow.Response` object"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               status=200,
                               content_type="application/json")

        response = self.resource.get(self.dict_query, fields=self.get_fields)
        report_params = response.report.request_params

        # List of fields should end up as comma-separated string
        self.assertEquals(report_params['sysparm_fields'], ','.join(self.get_fields))
        self.assertEquals(type(response), Response)

    @httpretty.activate
    def test_insert_request(self):
        """:meth:`insert` should return a dictionary of the new record"""

        httpretty.register_uri(httpretty.POST,
                               self.mock_url_builder_base,
                               body=get_serialized(self.record_response_insert),
                               status=200,
                               content_type="application/json")

        result = self.resource.insert(self.record_response_insert)

        self.assertEquals(type(result), dict)
        self.assertEquals(result, self.record_response_insert)

    @httpretty.activate
    def test_update_request(self):
        """:meth:`update` should return a dictionary of the updated record"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized(self.record_response_get),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               self.mock_url_builder_sys_id,
                               body=get_serialized(self.record_response_update),
                               status=200,
                               content_type="application/json")

        result = self.resource.update(self.dict_query, self.record_response_update)

        self.assertEquals(type(result), dict)
        self.assertEquals(self.record_response_update['attr1'], result['attr1'])

    @httpretty.activate
    def test_integration_delete(self):
        """:meth:`delete` should return a dictionary containing status"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized(self.record_response_get),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               self.mock_url_builder_sys_id,
                               body=get_serialized(self.record_response_delete),
                               status=200,
                               content_type="application/json")

        result = self.resource.delete(self.dict_query)

        self.assertEquals(type(result), dict)
        self.assertEquals(result['status'], 'record deleted')

    @httpretty.activate
    def test_integration_custom(self):
        """:meth:`custom` should return a :class:`pysnow.Response` object"""

        httpretty.register_uri(httpretty.GET,
                               self.mock_url_builder_base,
                               body=get_serialized(self.record_response_get),
                               status=200,
                               content_type="application/json")

        response = self.resource.custom('GET')

        self.assertEquals(type(response), Response)

