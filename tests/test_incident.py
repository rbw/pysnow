# -*- coding: utf-8 -*-
import unittest
import pysnow
import logging
import json
import httpretty
from copy import copy


class TestIncident(unittest.TestCase):
    def setUp(self):
        # Mock client configuration
        self.mock_connection = {
            'instance': 'mock_instance',
            'user': 'mock_user',
            'pass': 'mock_pass',
            'raise_on_empty': False
        }
        self.mock_connection['fqdn'] = "%s.service-now.com" % self.mock_connection['instance']

        # Mock incident attributes
        self.mock_incident = {
            'path': 'api/now/table/incident',
            'number': 'INC01234',
            'sys_id': '98ace1a537ea2a00cf5c9c9953990e19',
            'link_arg': '?page=2'
        }

        # Mock attachment attributes
        self.mock_attachment = {
            'path': 'api/now/attachment/upload',
            'sys_id': 'b39fb9c1db0032000062f34ebf96198b',
            'file_name': 'example.txt',
        }

        self.client = pysnow.Client(instance=self.mock_connection['instance'],
                                    user=self.mock_connection['user'],
                                    password=self.mock_connection['pass'],
                                    raise_on_empty=self.mock_connection['raise_on_empty'])

        # Use `nosetests -l debug` to enable this logger
        logging.basicConfig(level=logging.DEBUG)
        self.log = logging.getLogger('debug')

    def test_invalid_default_payload(self):
        """
        Make sure passing an invalid payload doesn't work
        """
        try:
            pysnow.Client(instance=self.mock_connection['instance'],
                          user=self.mock_connection['user'],
                          password=self.mock_connection['pass'],
                          raise_on_empty=self.mock_connection['raise_on_empty'],
                          default_payload='invalid payload')
        except pysnow.InvalidUsage:
            pass

    def test_connection(self):
        self.assertEqual(self.client.instance, self.mock_connection['instance'])
        self.assertEqual(self.client._user, self.mock_connection['user'])
        self.assertEqual(self.client._password, self.mock_connection['pass'])
        self.assertEqual(self.client.raise_on_empty, self.mock_connection['raise_on_empty'])
        self.assertEqual(self.client.default_payload, {})

    @httpretty.activate
    def test_invalid_query_type(self):
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        try:
            self.client.query(table='incident', query=1).get_one()
            self.assertFalse('Query of type int should fail')
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_get_incident_by_dict_query(self):
        """
        Make sure fetching by dict type query works
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        # Make sure we got an incident back with the expected number
        self.assertEquals(r.get_one()['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_limited_result(self):
        """
        Make sure fetching by dict type query works
        """
        json_body = json.dumps({'result':
                                    [
                                        {
                                            'number': self.mock_incident['number']
                                        },
                                        {
                                            'number': self.mock_incident['number']
                                        },
                                        {
                                            'number': self.mock_incident['number']
                                        },
                                        {
                                            'number': self.mock_incident['number']
                                        }
                                    ]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})

        # Trigger a request by fetching next element from the generator
        r.get_all(limit=2).__next__()

        # Get last request QS
        qs = httpretty.last_request().querystring

        # Make sure sysparm_limit equals limit
        self.assertEqual(int(qs['sysparm_limit'][0]), 2)

        # Make sure sysparm_suppress_pagination_header is True
        self.assertTrue(qs['sysparm_suppress_pagination_header'])


    @httpretty.activate
    def test_get_incident_by_string_query(self):
        """
        Make sure fetching by string type query works
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query='nameINincident,task^elementLIKEstate')

        # Make sure we got an incident back with the expected number
        self.assertEquals(r.get_one()['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_incident_content_error(self):
        """
        Make sure error in content is properly handled
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({'error': {'message': 'test'}}),
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        try:
            r.get_one()
        except pysnow.UnexpectedResponse:
            pass

    @httpretty.activate
    def test_get_incident_invalid_query(self):
        """
        Make sure querying by non-dict and non-string doesn't work
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        # Pass query as a list() , which is invalid
        r = self.client.query(table='incident', query=list())
        try:
            r.get_one()
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_get_linked_result(self):
        """
        Fetch multiple incident records from a linked result
        """

        link_header = "<https://%s/%s/%s>; rel='next'" % (
            self.mock_connection['fqdn'],
            self.mock_incident['path'],
            self.mock_incident['link_arg']
        )

        json_body_first = json.dumps({'result': [{'number': self.mock_incident['number'], 'linked': False}]})
        json_body_second = json.dumps({'result': [{'number': self.mock_incident['number'], 'linked': True}]})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body_first,
                               status=200,
                               content_type="application/json",
                               adding_headers={'Link': link_header})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s/%s" % (
                                   self.mock_connection['fqdn'],
                                   self.mock_incident['path'],
                                   self.mock_incident['link_arg']
                               ),
                               body=json_body_second,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        result = r.get_all()

        # Return the first result from the container
        first = next(result)
        self.assertEquals(first['number'], self.mock_incident['number'])
        # Make sure it's the record we're after
        self.assertFalse(first['linked'])

        # Return the second result from the container (linked)
        second = next(result)
        self.assertEquals(second['number'], self.mock_incident['number'])
        # Make sure it's the record we're after
        self.assertTrue(second['linked'])

    @httpretty.activate
    def test_get_incident_no_results(self):
        """
        Make sure empty result sets are properly handled
        """
        client = copy(self.client)
        json_body = json.dumps({'result': []})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=404,
                               content_type="application/json")

        client.raise_on_empty = True

        # If `raise_on_empty` is True and status code is 404, or 200 and empty result, an exception should be thrown.
        try:
            result = client.query(table='incident', query={'number': self.mock_incident['number']}).get_one()
            self.assertNotEquals(result, {})
        except pysnow.NoResults:
            pass

        client.raise_on_empty = False
        r = client.query(table='incident', query={'number': self.mock_incident['number']})

        # Quietly continue if `raise_on_empty` if False
        self.assertEquals(r.get_one(), {})
        self.assertEquals(r.status_code, 404)

    @httpretty.activate
    def test_insert_incident(self):
        """
        Create new incident, make sure status code is 201 and we get a sys_id back
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=201,
                               content_type="application/json")

        r = self.client._request('POST', 'incident')
        result = r.insert(payload={'field1': 'value1', 'field2': 'value2'})

        # Make sure we got an incident back with the expected number and status code 201
        self.assertEquals(result[0]['sys_id'], self.mock_incident['sys_id'])
        self.assertEquals(r.status_code, 201)

    @httpretty.activate
    def test_insert_incident_invalid_status(self):
        """
        Update an incident and get an unexpected status code back, make sure it fails properly.
        """
        json_body = {
            'result':
                [
                    {
                        'sys_id': self.mock_incident['sys_id']
                    }
                ],
            'error':
                {
                    'message': 'Error summary',
                    'detail': 'Error detail '
                }
        }

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps(json_body),
                               status=403,
                               content_type="application/json")

        r = self.client._request('POST', 'incident')

        try:
            r.insert(payload={'field1': 'value1', 'field2': 'value2'})
        except pysnow.UnexpectedResponse as e:
            # Make sure the exception object contains summary and details
            self.assertEquals(e.error_summary, json_body['error']['message'])
            self.assertEquals(e.error_details, json_body['error']['detail'])
            pass

    @httpretty.activate
    def test_update_incident(self):
        """
        Updates an existing incident. Checks for sys_id and status code 200
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.update({'this': 'that'})

        # Make sure we got an incident back with the expected sys_id
        self.assertEquals(result[0]['sys_id'], self.mock_incident['sys_id'])
        self.assertEquals(result[0]['this'], 'that')
        self.assertEquals(r.status_code, 200)

    @httpretty.activate
    def test_update_incident_non_existent(self):
        """
        Attempt to update a non-existent incident
        """
        json_body = json.dumps({})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.update({'this': 'that'})
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_update_incident_invalid_update(self):
        """
        Make sure updates which are non-dict and non-string type are properly handled
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.update('invalid update')
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_update_incident_multiple(self):
        """
        Make sure update queries yielding more than 1 record fails
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'},
                                           {'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        try:
            r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
            r.update({'this': 'that'})
            self.assertEquals(True, False)
        except NotImplementedError:
            pass

    @httpretty.activate
    def test_attach_incident(self):
        """
        Attaches file to an existing incident. Checks for table_sys_id, file_name and status code 201
        """
        json_get_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]})
        json_post_body = json.dumps(
            {
                'result':
                    {
                         'sys_id': self.mock_attachment['sys_id'],
                         'table_sys_id': self.mock_incident['sys_id'],
                         'file_name': self.mock_attachment['file_name']
                    }
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_get_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.attach('tests/example.txt')

        # Make sure we got an incident back with the expected sys_id
        self.assertEquals(result['table_sys_id'], self.mock_incident['sys_id'])
        self.assertEquals(result['file_name'], self.mock_attachment['file_name'])
        self.assertEquals(r.status_code, 201)

    @httpretty.activate
    def test_attach_incident_non_existent(self):
        """
        Attempts to attach file to a non-existent incident
        """
        json_post_body = json.dumps(
            {
                'result':
                    {
                         'sys_id': self.mock_attachment['sys_id'],
                         'table_sys_id': self.mock_incident['sys_id'],
                         'file_name': self.mock_attachment['file_name']
                    }
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.attach('tests/example.txt')
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_attach_incident_non_file(self):
        """
        Attempts to attach a non-file to an incident
        """
        json_post_body = json.dumps(
            {
                'result':
                    {
                         'sys_id': self.mock_attachment['sys_id'],
                         'table_sys_id': self.mock_incident['sys_id'],
                         'file_name': self.mock_attachment['file_name']
                    }
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.attach('tests/non_existing_file.txt')
            self.assertEquals(True, False)
        except pysnow.InvalidUsage:
            pass

    @httpretty.activate
    def test_attach_incident_multiple(self):
        """
        Make sure attach fails when getting multiple records back
        """
        json_get_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']},
                                               {'sys_id': self.mock_incident['sys_id']}]})

        json_post_body = json.dumps(
            {
                'result':
                    {
                         'sys_id': self.mock_attachment['sys_id'],
                         'table_sys_id': self.mock_incident['sys_id'],
                         'file_name': self.mock_attachment['file_name']
                    }
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_get_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        try:
            r.attach('tests/example.txt')
            self.assertEquals(True, False)
        except NotImplementedError:
            pass

    @httpretty.activate
    def test_delete_incident(self):
        """
        Delete an incident, make sure we get a 204 back along with expected body
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.delete()

        self.assertEquals(result['success'], True)
        self.assertEquals(r.status_code, 204)

    @httpretty.activate
    def test_delete_incident_multiple(self):
        """
        Make sure delete queries yielding more than 1 record fails
        """
        json_body_get = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']},
                                               {'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json_body_get,
                               status=200,
                               content_type="application/json")

        json_body_delete = json.dumps({'success': True})
        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body_delete,
                               status=204,
                               content_type="application/json")

        try:
            r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
            r.delete()
            self.assertEquals(True, False)
        except NotImplementedError:
            pass

    @httpretty.activate
    def test_delete_incident_invalid_response(self):
        """
        Make sure non-204 responses are properly handled
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.delete()
        except pysnow.UnexpectedResponse:
            pass

    @httpretty.activate
    def test_delete_incident_non_existent(self):
        """
        Attempt to delete a non-existing record
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['fqdn'], self.mock_incident['path']),
                               body=json.dumps({}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['fqdn'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        try:
            r.delete()
        except pysnow.NoResults:
            pass
