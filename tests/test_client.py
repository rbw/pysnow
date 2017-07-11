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

    def test_client_with_default_payload(self):

        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload="a string")
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo",
                          default_payload=['item0', 'item1'])
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload=3)
        # test if default_payload == 0 (evaluates to true but is not valid)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload=0)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload=(1, "2"))
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload=True)
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo", password="foo", default_payload=2.89)



