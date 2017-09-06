# -*- coding: utf-8 -*-
import unittest
import requests

from pysnow.client import Client
from pysnow.exceptions import InvalidUsage


class TestClient(unittest.TestCase):
    def test_client_missing_args(self):
        """Client should raise an exception if it is missing arguments."""
        self.assertRaises(InvalidUsage, Client, instance="test")
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo")
        self.assertRaises(InvalidUsage, Client, instance="test", password="foo")

    def test_client_incompabtible_args(self):
        """Client should raise an exception if it receives incompatible args."""
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="bar", session="foobar")

    def test_client_user_password(self):
        """Should be able to create a client given user name and password."""
        Client("snow.example.com", user="foo", password="bar")

    def test_client_with_session(self):
        """Should be able to create a client given a requests session object."""
        session = requests.Session()
        Client("snow.example.com", session=session)

    def test_client_with_host_and_instance(self):
        """Client should raise an exception if it receives both host and instance"""
        self.assertRaises(InvalidUsage, Client, instance="test", host="test", user="foo", password="bar")

    def test_client_without_host_or_instance(self):
        """Client should raise an exception if it doesn't receive instance nor host"""
        self.assertRaises(InvalidUsage, Client, user="foo", password="bar")

    def test_client_host(self):
        """Client host property should match host passed to constructor"""
        host = "123.123.123.123"
        c = Client(user="foo", password="foo", host=host)
        self.assertEqual(c.host, host)

    def test_client_instance(self):
        """Client instance property should match instance passed to constructor"""
        instance = "foo"
        c = Client(user="foo", password="foo", instance=instance)
        self.assertEqual(c.instance, instance)

    def test_client_invalid_request_params(self):
        """Client should raise an exception if `request_params` is of an invalid type """
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params="a string")
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo",
                          request_params=['item0', 'item1'])

        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params=3)

        # test if request_params == 0 (evaluates to true but is not valid)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params=0)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params=(1, "2"))
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params=True)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", request_params=2.89)

    def test_client_valid_request_params(self):
        """Client `request_params` property should match what was passed as an argument"""
        params = {'foo': 'bar'}
        c = Client(instance="test", user="foo", password="foo", request_params=params)
        self.assertEqual(c.request_params, params)

        # Remove tests below when `default_payload` has been removed from `Client`
        c = Client(instance="test", user="foo", password="foo", default_payload=params)
        self.assertEqual(c.default_payload, params)


