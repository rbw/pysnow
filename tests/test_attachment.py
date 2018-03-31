# -*- coding: utf-8 -*-
import unittest
import json
import httpretty
import pysnow

from pysnow.exceptions import InvalidUsage


def get_serialized_result(dict_mock):
    return json.dumps({'result': dict_mock})


attachment_path = 'tests/data/attachment.txt'
mock_sys_id = '98ace1a537ea2a00cf5c9c9953990e19'

attachments_resource = [
    {
        'sys_id': mock_sys_id,
        'size_bytes': '512',
        'file_name': 'test1.txt'
    },
    {
        'sys_id': mock_sys_id,
        'size_bytes': '1024',
        'file_name': 'test2.txt'
    },
    {
        'sys_id': mock_sys_id,
        'size_bytes': '2048',
        'file_name': 'test3.txt'
    }
]

attachments_resource_sys_id = [
    {
        'sys_id': 'mock_sys_id1',
        'size_bytes': '512',
        'file_name': 'test1.txt'
    },
    {
        'sys_id': 'mock_sys_id2',
        'size_bytes': '1024',
        'file_name': 'test2.txt'
    }
]

attachment = {
    'sys_id': mock_sys_id,
    'size_bytes': '512',
    'file_name': 'test1.txt'
}

delete_status = {'status': 'record deleted'}
mock_api_path = '/table/incident'


class TestAttachment(unittest.TestCase):
    def setUp(self):
        self.client = pysnow.Client(instance='test', user='test', password='test')
        r = self.resource = self.client.resource(api_path=mock_api_path)
        a = self.attachment_base_url = r._base_url + r._base_path + '/attachment'
        self.attachment_url_binary = a + '/file'
        self.attachment_url_multipart = a + '/upload'
        self.attachment_url_sys_id = a + '/' + mock_sys_id

    @httpretty.activate
    def test_get_resource_all(self):
        """Getting metadata for multiple attachments within a resource should work"""

        httpretty.register_uri(httpretty.GET,
                               self.attachment_base_url,
                               body=get_serialized_result(attachments_resource),
                               status=200,
                               content_type="application/json")

        result = self.resource.attachments.get()
        self.assertEqual(attachments_resource, list(result))

    @httpretty.activate
    def test_get_all_by_id(self):
        """Getting attachment metadata for a specific record by sys_id should work"""

        httpretty.register_uri(httpretty.GET,
                               self.attachment_base_url,
                               body=get_serialized_result(attachments_resource_sys_id),
                               status=200,
                               content_type="application/json")

        result = self.resource.attachments.get(sys_id=mock_sys_id)
        self.assertEqual(attachments_resource_sys_id, list(result))

    @httpretty.activate
    def test_upload_binary(self):
        """Uploading with multipart should append /file to URL"""

        httpretty.register_uri(httpretty.POST,
                               self.attachment_url_binary,
                               body=get_serialized_result(attachment),
                               status=201,
                               content_type="application/json")

        response = self.resource.attachments.upload(sys_id=mock_sys_id,
                                                    file_path=attachment_path)

        self.assertEqual(response.one(), attachment)

    @httpretty.activate
    def test_upload_multipart(self):
        """Uploading with multipart should append /upload to URL"""

        httpretty.register_uri(httpretty.POST,
                               self.attachment_url_multipart,
                               body=get_serialized_result(attachment),
                               status=201,
                               content_type="application/json")

        response = self.resource.attachments.upload(sys_id=mock_sys_id,
                                                    file_path=attachment_path,
                                                    multipart=True)

        self.assertEqual(response.one(), attachment)

    @httpretty.activate
    def test_upload_delete(self):
        """Deleting an attachment should trigger pysnow to perform a lookup followed by a delete"""

        httpretty.register_uri(httpretty.GET,
                               self.attachment_base_url,
                               body=get_serialized_result(attachment),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               self.attachment_url_sys_id,
                               body=get_serialized_result(delete_status),
                               status=204,
                               content_type="application/json")

        resource = self.client.resource(api_path=mock_api_path)
        result = resource.attachments.delete(mock_sys_id)

        self.assertEqual(result, delete_status)

    def test_upload_invalid_multipart_type(self):
        """Passing a non-bool type as multipart argument should raise InvalidUsage"""

        a = self.resource.attachments
        self.assertRaises(InvalidUsage, a.upload, mock_sys_id, attachment_path, multipart=dict())
