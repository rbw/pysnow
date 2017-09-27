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
        self.mock_connection['host'] = "%s.service-now.com" % self.mock_connection['instance']

        # Mock incident attributes
        self.mock_incident = {
            'stats': 'api/now/stats/incident',
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

    def test_invalid_request_params(self):
        """
        Make sure passing an invalid payload doesn't work
        """
        self.assertRaises(pysnow.InvalidUsage, pysnow.Client,
                          instance=self.mock_connection['instance'],
                          user=self.mock_connection['user'],
                          password=self.mock_connection['pass'],
                          raise_on_empty=self.mock_connection['raise_on_empty'],
                          request_params='invalid payload')

    def test_connection(self):
        self.assertEqual(self.client.instance, self.mock_connection['instance'])
        self.assertEqual(self.client._user, self.mock_connection['user'])
        self.assertEqual(self.client._password, self.mock_connection['pass'])
        self.assertEqual(self.client.raise_on_empty, self.mock_connection['raise_on_empty'])
        self.assertEqual(self.client.request_params, {})

    @httpretty.activate
    def test_client_request_params(self):
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': ''}),
                               status=200,
                               content_type="application/json")
        client = pysnow.Client(instance=self.mock_connection['instance'],
                               user=self.mock_connection['user'],
                               password=self.mock_connection['pass'],
                               raise_on_empty=self.mock_connection['raise_on_empty'],
                               request_params={'foo1': 'bar1', 'foo2': 'bar2'})

        r = client.query(table='incident', query={})
        r.get_one()

        # Parse QS and make sure `request_params` actually ended up in the request
        qs_str = r.last_response.url.split("?")[1]

        qs = dict((x[0], x[1]) for x in [x.split("=") for x in qs_str.split("&")])

        self.assertEqual(qs['foo1'], 'bar1')
        self.assertEqual(qs['foo2'], 'bar2')

    @httpretty.activate
    def test_invalid_query_type(self):
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query=1)
        self.assertRaises(pysnow.InvalidUsage, r.get_one)

    @httpretty.activate
    def test_get_count(self):
        json_body = json.dumps({'result': {'stats': {'count': '30'}}})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['stats']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})
        self.assertEqual(r.count, 30)

    @httpretty.activate
    def test_last_response_not_executed(self):
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        try:
            str(self.client.query(table='incident', query={}).last_response)
            self.assertFalse('Getting last_response should fail when no `Request` has been executed')
        except pysnow.NoRequestExecuted:
            pass

    @httpretty.activate
    def test_last_response(self):
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})
        r.get_one()

        # Make sure we get the expected status code back
        self.assertEqual(r.status_code, 200)

        # Make sure last_response is not None
        self.assertNotEqual(r.last_response, None)

    @httpretty.activate
    def test_get_incident_by_qb(self):
        """
        Make sure fetching by dict type query works
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        q = pysnow.QueryBuilder().field('number').equals(self.mock_incident['number'])
        r = self.client.query(table='incident', query=q)

        # Make sure we got an incident back with the expected number
        self.assertEqual(r.get_one()['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_incident_by_dict_query(self):
        """
        Make sure fetching by dict type query works
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        # Make sure we got an incident back with the expected number
        self.assertEqual(r.get_one()['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_content_without_result(self):
        """
        Make sure content without `result` fails
        """
        json_body = json.dumps({})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})

        self.assertRaises(pysnow.MissingResult, r.get_one)

    @httpretty.activate
    def test_get_limited_result(self):
        """
        Make sure fetching by dict type query works
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})

        # Trigger a request by fetching next element from the generator
        next(r.get_all(limit=2))

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
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query='nameINincident,task^elementLIKEstate')

        # Make sure we got an incident back with the expected number
        self.assertEqual(r.get_one()['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_sorted(self):
        """
        Make sure order_by generates the expected sysparm_query string
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})
        next(r.get_multiple(order_by=['-number', 'category']))

        qs_str = r.last_response.url.split("?")[1]
        qs = dict((x[0], x[1]) for x in [x.split("=") for x in qs_str.split("&")])

        self.assertEqual(str(qs['sysparm_query']), '%5EORDERBYDESCnumber%5EORDERBYcategory')

    @httpretty.activate
    def test_get_sorted_invalid(self):
        """
        Make sure get_multiple fails if order_by is not of type list()
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={})
        self.assertRaises(pysnow.InvalidUsage, next, r.get_multiple(order_by='number'))
        self.assertRaises(pysnow.InvalidUsage, next, r.get_multiple(order_by={'number': 1}))
        self.assertRaises(pysnow.InvalidUsage, next, r.get_multiple(order_by=1))

    @httpretty.activate
    def test_get_incident_content_error(self):
        """
        Make sure error in content is properly handled
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'error': {'message': 'test'}}),
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.UnexpectedResponse, r.get_one)

    @httpretty.activate
    def test_get_incident_invalid_query(self):
        """
        Make sure querying by non-dict and non-string doesn't work
        """
        json_body = json.dumps({'result': [{'number': self.mock_incident['number']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        # Pass query as a list() , which is invalid
        r = self.client.query(table='incident', query=list())
        self.assertRaises(pysnow.InvalidUsage, r.get_one)

    @httpretty.activate
    def test_get_linked_result(self):
        """
        Fetch multiple incident records from a linked result
        """

        link_header = "<https://%s/%s/%s>; rel='next'" % (
            self.mock_connection['host'],
            self.mock_incident['path'],
            self.mock_incident['link_arg']
        )

        json_body_first = json.dumps({'result': [{'number': self.mock_incident['number'], 'linked': False}]})
        json_body_second = json.dumps({'result': [{'number': self.mock_incident['number'], 'linked': True}]})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body_first,
                               status=200,
                               content_type="application/json",
                               adding_headers={'Link': link_header})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s/%s" % (
                                   self.mock_connection['host'],
                                   self.mock_incident['path'],
                                   self.mock_incident['link_arg']
                               ),
                               body=json_body_second,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})

        result = r.get_multiple()

        # Return the first result from the container
        first = next(result)
        self.assertEqual(first['number'], self.mock_incident['number'])
        # Make sure it's the record we're after
        self.assertFalse(first['linked'])

        # Return the second result from the container (linked)
        second = next(result)
        self.assertEqual(second['number'], self.mock_incident['number'])
        # Make sure it's the record we're after
        self.assertTrue(second['linked'])

    @httpretty.activate
    def test_get_incident_invalid_field_format(self):
        """
        Make sure passing fields as non-list fails
        """
        client = copy(self.client)
        json_body = json.dumps({'result': []})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=404,
                               content_type="application/json")

        client.raise_on_empty = True

        # If `raise_on_empty` is True and status code is 404, or 200 and empty result, an exception should be thrown.
        r = client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.get_one)

        client.raise_on_empty = False
        r = client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.InvalidUsage, r.get_one, fields='test')

    @httpretty.activate
    def test_get_incident_field_filter(self):
        """
        Make sure passing fields works as intended
        """
        client = copy(self.client)
        json_body = json.dumps(
            {
                'result':
                    [
                        {
                             'sys_id': self.mock_incident['sys_id'],
                             'number': self.mock_incident['number']
                        }
                    ]
            }
        )
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = client.query(table='incident', query={'number': self.mock_incident['number']})

        result = r.get_one(fields=['sys_id', 'number'])

        # Make sure we get the selected fields back
        self.assertEqual(result['sys_id'], self.mock_incident['sys_id'])
        self.assertEqual(result['number'], self.mock_incident['number'])

    @httpretty.activate
    def test_get_incident_no_results(self):
        """
        Make sure empty result sets are properly handled
        """
        client = copy(self.client)
        json_body = json.dumps({'result': []})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=404,
                               content_type="application/json")

        client.raise_on_empty = True

        # If `raise_on_empty` is True and status code is 404, or 200 and empty result, an exception should be thrown.
        r = client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.get_one)

        client.raise_on_empty = False
        r = client.query(table='incident', query={'number': self.mock_incident['number']})

        res = r.get_one()

        # Quietly continue if `raise_on_empty` if False
        self.assertEqual(res, {})
        self.assertEqual(r.status_code, 404)

    @httpretty.activate
    def test_insert_incident(self):
        """
        Create new incident, make sure we get a sys_id back
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=201,
                               content_type="application/json")

        result = self.client.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})

        # Make sure we got an incident back
        self.assertEqual(result[0]['sys_id'], self.mock_incident['sys_id'])

    @httpretty.activate
    def test_insert_incident_status(self):
        """
        Create new incident, make sure status code is 201
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=201,
                               content_type="application/json")

        r = self.client._request('POST', 'incident')
        r.insert(payload={'field1': 'value1', 'field2': 'value2'})

        # Make sure we got code 201 back
        self.assertEqual(r.status_code, 201)

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
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps(json_body),
                               status=403,
                               content_type="application/json")

        r = self.client._request('POST', 'incident')

        try:
            r.insert(payload={'field1': 'value1', 'field2': 'value2'})
        except pysnow.UnexpectedResponse as e:
            # Make sure the exception object contains summary and details
            self.assertEqual(e.error_summary, json_body['error']['message'])
            self.assertEqual(e.error_details, json_body['error']['detail'])
            pass

    @httpretty.activate
    def test_update_incident(self):
        """
        Updates an existing incident. Checks for sys_id and status code 200
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.update({'this': 'that'})

        # Make sure we got an incident back with the expected sys_id
        self.assertEqual(result[0]['sys_id'], self.mock_incident['sys_id'])
        self.assertEqual(result[0]['this'], 'that')
        self.assertEqual(r.status_code, 200)

    @httpretty.activate
    def test_update_incident_non_existent(self):
        """
        Attempt to update a non-existent incident
        """
        json_body = json.dumps({'result': {}})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body={},
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.update, {'foo': 'bar'})

    @httpretty.activate
    def test_update_incident_invalid_update(self):
        """
        Make sure updates which are non-dict and non-string type are properly handled
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.InvalidUsage, r.update, 'invalid update')

    @httpretty.activate
    def test_update_incident_multiple(self):
        """
        Make sure update queries yielding more than 1 record fails
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'},
                                           {'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.PUT,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(NotImplementedError, r.update, {'foo': 'bar'})

    @httpretty.activate
    def test_get_multiple_with_offset(self):
        """
        Make sure offset works properly
        """
        json_body = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id'], 'this': 'that'},
                                           {'sys_id': self.mock_incident['sys_id'], 'this': 'that'}]})

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        list(r.get_multiple(limit=100, offset=50))

        qs = httpretty.last_request().querystring

        # Make sure sysparm_offset is set to the expected value
        self.assertEqual(int(qs['sysparm_offset'][0]), 50)

        # Make sure sysparm_limit is set to the expected value
        self.assertEqual(int(qs['sysparm_limit'][0]), 100)


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
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_get_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.attach('tests/example.txt')

        # Make sure we got an incident back with the expected sys_id
        self.assertEqual(result['table_sys_id'], self.mock_incident['sys_id'])
        self.assertEqual(result['file_name'], self.mock_attachment['file_name'])
        self.assertEqual(r.status_code, 201)

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
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': {}}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.attach, 'tests/example.txt')

    @httpretty.activate
    def test_attach_incident_non_file(self):
        """
        Attempts to attach a non-file to an incident
        """
        json_post_body = json.dumps(
            {
                'result':
                    [
                        {
                             'sys_id': self.mock_attachment['sys_id'],
                             'table_sys_id': self.mock_incident['sys_id'],
                             'file_name': self.mock_attachment['file_name']
                        }
                    ]
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_post_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.InvalidUsage, r.attach, 'tests/non_existing_file.txt')

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
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_get_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_attachment['path']),
                               body=json_post_body,
                               status=201,
                               content_type="multipart/form-data")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(NotImplementedError, r.attach, 'tests/example.txt')

    @httpretty.activate
    def test_delete_incident(self):
        """
        Delete an incident, make sure we get a 204 back along with expected body
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        result = r.delete()

        self.assertEqual(result['success'], True)
        self.assertEqual(r.status_code, 204)

    @httpretty.activate
    def test_delete_incident_multiple(self):
        """
        Make sure delete queries yielding more than 1 record fails
        """
        json_body_get = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']},
                                               {'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body_get,
                               status=200,
                               content_type="application/json")

        json_body_delete = json.dumps({'success': True})
        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json_body_delete,
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(NotImplementedError, r.delete)

    @httpretty.activate
    def test_delete_incident_invalid_response(self):
        """
        Make sure non-204 responses are properly handled
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']}]}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.UnexpectedResponse, r.delete)

    @httpretty.activate
    def test_delete_incident_non_existent(self):
        """
        Attempt to delete a non-existing record
        """
        client = copy(self.client)
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': {}}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        client.raise_on_empty = False

        r = client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.delete)

    @httpretty.activate
    def test_clone_incident_non_existent(self):
        """
        Attempt to clone a non-existing record
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': {}}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.NoResults, r.clone)

    @httpretty.activate
    def test_clone_incident_invalid_reset_fields(self):
        """
        Attempt to pass reset_fields as non-list to clone()
        """
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json.dumps({'result': {}}),
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.DELETE,
                               "https://%s/%s/%s" % (self.mock_connection['host'],
                                                     self.mock_incident['path'],
                                                     self.mock_incident['sys_id']),
                               body=json.dumps({'success': True}),
                               status=204,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.InvalidUsage, r.clone, reset_fields='test')

    @httpretty.activate
    def test_clone_incident_multiple(self):
        """
        Make sure clone queries yielding more than 1 record fails
        """
        json_body_get = json.dumps({'result': [{'sys_id': self.mock_incident['sys_id']},
                                               {'sys_id': self.mock_incident['sys_id']}]})
        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body_get,
                               status=200,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(NotImplementedError, r.clone)

    @httpretty.activate
    def test_clone_incident_flatten(self):
        """
        Make sure clone payload is properly flattened
        """
        json_body = json.dumps(
            {
                'result':
                    [
                        {
                            'sys_id': self.mock_incident['sys_id'],
                            'test': {
                                'value': 'test_value'
                            }
                        }
                    ]
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=201,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        r.clone(reset_fields=['sys_id'])
        request_body = json.loads(httpretty.last_request().body.decode('utf-8'))

        self.assertEqual(request_body['test'], 'test_value')

    @httpretty.activate
    def test_clone_incident_reset_fields(self):
        """
        Make sure reset fields works
        """
        json_body = json.dumps(
            {
                'result':
                    [
                        {
                            'sys_id': self.mock_incident['sys_id'],
                            'number': self.mock_incident['number']
                        }
                    ]
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=201,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        r.clone(reset_fields=['sys_id'])
        request_body = json.loads(httpretty.last_request().body.decode('utf-8'))

        self.assertEqual(request_body['number'], self.mock_incident['number'])
        self.assertFalse('sys_id' in request_body)

    @httpretty.activate
    def test_clone_unexpected_response(self):
        """
        Make sure status code 403 is properly handled when cloning
        """
        json_body = json.dumps(
            {
                'result':
                    [
                        {
                            'sys_id': self.mock_incident['sys_id'],
                            'number': self.mock_incident['number']
                        }
                    ]
            }
        )

        httpretty.register_uri(httpretty.GET,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=200,
                               content_type="application/json")

        httpretty.register_uri(httpretty.POST,
                               "https://%s/%s" % (self.mock_connection['host'], self.mock_incident['path']),
                               body=json_body,
                               status=403,
                               content_type="application/json")

        r = self.client.query(table='incident', query={'number': self.mock_incident['number']})
        self.assertRaises(pysnow.UnexpectedResponse, r.clone)
