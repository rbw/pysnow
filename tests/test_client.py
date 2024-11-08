# -*- coding: utf-8 -*-
import unittest
import requests

from pysnow.client import Client
from pysnow.exceptions import InvalidUsage


class TestClient(unittest.TestCase):
    def test_client_context_manager(self):
        with Client("snow.example.com", user="foo", password="bar") as c:
            assert isinstance(c, Client)
            assert c.session

    def test_client_missing_args(self):
        """Client should raise an exception if it is missing arguments."""
        self.assertRaises(InvalidUsage, Client, instance="test")
        self.assertRaises(InvalidUsage, Client, instance="test", user="foo")
        self.assertRaises(InvalidUsage, Client, instance="test", password="foo")

    def test_client_incompatible_args(self):
        """Client should raise an exception if it receives incompatible args."""
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="bar",
            session="foobar",
        )

    def test_client_user_password(self):
        """Should be able to create a client given user name and password."""
        Client("snow.example.com", user="foo", password="bar")

    def test_invalid_resource_paths(self):
        """:meth:`resource` should raise an InvalidUsage exception if an invalid api_path was provided"""
        c = Client(user="foo", password="foo", instance="instance")
        self.assertRaises(InvalidUsage, c.resource)
        self.assertRaises(InvalidUsage, c.resource, api_path="not_valid")
        self.assertRaises(InvalidUsage, c.resource, api_path="not/valid")
        self.assertRaises(InvalidUsage, c.resource, api_path="not/valid/")
        self.assertRaises(InvalidUsage, c.resource, api_path="/")
        self.assertRaises(InvalidUsage, c.resource, base_path="not_valid")
        self.assertRaises(InvalidUsage, c.resource, base_path="not/valid")
        self.assertRaises(InvalidUsage, c.resource, base_path="not/valid/")
        self.assertRaises(InvalidUsage, c.resource, base_path="/")

    def test_valid_resource_paths(self):
        """:meth:`resource` should return a :class:`pysnow.Response` object with paths set to the expected value"""
        api_path = "/api/path"
        base_path = "/base/path"
        c = Client(user="foo", password="foo", instance="instance")
        r = c.resource(api_path=api_path, base_path=base_path)
        self.assertEqual(r._api_path, api_path)
        self.assertEqual(r._base_path, base_path)

    def test_valid_resource_paths_unicode(self):
        """:meth:`resource` should return a :class:`pysnow.Response` object with paths set to the expected value"""
        api_path = u"/api/path"
        base_path = u"/base/path"
        c = Client(user="foo", password="foo", instance="instance")
        r = c.resource(api_path=api_path, base_path=base_path)
        self.assertEqual(r._api_path, api_path)
        self.assertEqual(r._base_path, base_path)

    def test_client_with_session(self):
        """Should be able to create a client given a requests session object."""
        session = requests.Session()
        Client("snow.example.com", session=session)

    def test_client_with_host_and_instance(self):
        """Client should raise an exception if it receives both host and instance"""
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            host="test",
            user="foo",
            password="bar",
        )

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
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params="a string",
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=["item0", "item1"],
        )

        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=3,
        )

        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=0,
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=(1, "2"),
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=True,
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            request_params=2.89,
        )

    def test_client_invalid_use_ssl(self):
        """ Invalid use_ssl type should raise InvalidUsage"""
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            use_ssl="a string",
        )
        self.assertRaises(
            InvalidUsage, Client, instance="test", user="foo", password="foo", use_ssl=1
        )

    def test_client_invalid_raise_on_empty(self):
        """ Non-bool type to raise_on_empty should raise InvalidUsage"""
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            raise_on_empty=0,
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            raise_on_empty="test",
        )
        self.assertRaises(
            InvalidUsage,
            Client,
            instance="test",
            user="foo",
            password="foo",
            raise_on_empty={"a": "b"},
        )

    def test_client_use_ssl(self):
        """ Client should construct base URL with correct scheme depending on use_ssl """
        instance = "foo"
        host = "foo.bar.com"

        # Test with instance
        c = Client(user="foo", password="foo", instance=instance, use_ssl=False)
        self.assertEqual(c.base_url, "http://foo.service-now.com")
        c = Client(user="foo", password="foo", instance=instance, use_ssl=True)
        self.assertEqual(c.base_url, "https://foo.service-now.com")

        # Test with host
        c = Client(user="foo", password="foo", host=host, use_ssl=False)
        self.assertEqual(c.base_url, "http://foo.bar.com")
        c = Client(user="foo", password="foo", host=host, use_ssl=True)
        self.assertEqual(c.base_url, "https://foo.bar.com")

    def test_client_valid_request_params(self):
        """Client `request_params` property should match what was passed as an argument"""
        params = {"foo": "bar"}
        c = Client(instance="test", user="foo", password="foo", request_params=params)
        self.assertEqual(c.request_params, params)
