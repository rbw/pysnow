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

        self.client = pysnow.Client(instance=self.mock_connection['instance'],
                                    user=self.mock_connection['user'],
                                    password=self.mock_connection['pass'],
                                    raise_on_empty=self.mock_connection['raise_on_empty'])

        logging.basicConfig(level=logging.DEBUG)
        self.log = logging.getLogger('debug')

    def test_connection(self):
        self.assertEqual(self.client.instance, self.mock_connection['instance'])
        self.assertEqual(self.client._user, self.mock_connection['user'])
        self.assertEqual(self.client._password, self.mock_connection['pass'])
        self.assertEqual(self.client.raise_on_empty, self.mock_connection['raise_on_empty'])
        self.assertEqual(self.client.default_payload, {})

    @httpretty.activate
    def test_get_incident(self):
        """
        Fetch incident and compare numbers
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
        except pysnow.UnexpectedResponse:
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
    def test_delete_incident(self):
        """
        Delete an incident, make sure we get a 204 back along with expected body
        """
        json_body_get = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]})
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

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.delete()

        # Make sure we got an incident back with the expected number and status code 201
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

