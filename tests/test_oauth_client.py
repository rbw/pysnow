# -*- coding: utf-8 -*-
import unittest
import datetime
import httpretty
import json

from copy import copy
from pysnow import OAuthClient
from pysnow.exceptions import InvalidUsage, MissingToken, TokenCreateError


class TestOAuthClient(unittest.TestCase):
    def setUp(self):
        seconds = 3600

        in_one_hour = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        expires_at = int(in_one_hour.strftime("%s"))

        one_hour_ago = datetime.datetime.now() - datetime.timedelta(seconds=seconds)
        expired_at = int(one_hour_ago.strftime("%s"))

        self.mock_token = {
            "refresh_token": "refresh",
            "token_type": "Bearer",
            "access_token": "access",
            "expires_at": expires_at,
            "scope": ["useraccount"],
            "expires_in": seconds,
        }

        self.mock_token_expired = {
            "refresh_token": "refresh",
            "token_type": "Bearer",
            "access_token": "access",
            "expires_at": expired_at,
            "scope": ["useraccount"],
            "expires_in": -seconds,
        }

        self.incident_path = "api/now/table/incident"
        self.mock_incident_number = "INC012345"

        self.mock_token_url = "https://test.service-now.com/oauth_token.do"

        self.client = OAuthClient(
            instance="test", client_id="test1", client_secret="test2"
        )

    def token_updater(self, token):
        self.assertEqual(token["expires_in"], False)

    def test_oauth_client_missing_args(self):
        """OAuthClient should raise an exception if it is missing arguments."""
        self.assertRaises(InvalidUsage, OAuthClient, instance="test")
        self.assertRaises(
            InvalidUsage,
            OAuthClient,
            instance="test",
            client_id="test",
            token_updater=self.token_updater,
        )
        self.assertRaises(
            InvalidUsage,
            OAuthClient,
            instance="test",
            client_secret="test",
            token_updater=self.token_updater,
        )
        self.assertRaises(InvalidUsage, OAuthClient, token_updater=self.token_updater)

    def test_oauth_session_user_override(self):
        """OAuthClient should override user, pass and session"""
        c = OAuthClient(
            instance="test",
            client_id="test1",
            client_secret="test2",
            session="testsess",
            user="testuser",
            password="testpass",
        )

        self.assertEqual(c._user, None)
        self.assertEqual(c._password, None)

    def test_set_token_malformed(self):
        """set_token() should raise InvalidUsage if the token is not of the expected schema"""

        c = self.client
        token = self.mock_token.pop("refresh_token")

        self.assertRaises(InvalidUsage, c.set_token, token)

    def test_set_token_sanitation(self):
        """Unexpected keys passed to token in set_token() should get sanitized"""

        c = self.client
        token = copy(self.mock_token)
        token["extra"] = "test"
        c.set_token(token)

        # The `extra` key should not be available in the set token
        self.assertEqual(c.token, self.mock_token)

    def test_set_token(self):
        """set_token() should set token property and create an OAuth2Session"""
        c = self.client
        c.set_token(self.mock_token)

        self.assertEqual(c.token, self.mock_token)

    def test_request_without_token(self):
        """OauthClient should raise MissingToken when creating query when no token has been set"""
        c = self.client

        self.assertRaises(MissingToken, c.query, table="incident", query={})

    def test_resource_without_token(self):
        """OauthClient should raise MissingToken when creating a resource when no token has been set"""
        c = self.client

        self.assertRaises(MissingToken, c.resource, api_path="/valid/path")

    def test_resource_with_token(self):
        """OauthClient should raise MissingToken when creating a resource when no token has been set"""
        api_path = "/valid/path"

        c = self.client
        c.set_token(self.mock_token)

        r = c.resource(api_path="/valid/path")
        self.assertEqual(r._api_path, api_path)

    def test_reset_token(self):
        """OAuthClient should set token property to None and bypass validation if passed token is `False`"""
        c = self.client
        c.set_token(self.mock_token)

        c.set_token(None)

        self.assertEqual(c.token, None)

    @httpretty.activate
    def test_generate_token_error(self):
        """generate_token() should raise a TokenCreateError exception if OAuth2Error was raised"""
        httpretty.register_uri(
            httpretty.POST,
            self.mock_token_url,
            body={},
            status=400,
            content_type="application/json",
        )

        c = self.client

        self.assertRaises(TokenCreateError, c.generate_token, "foo", "bar")

    @httpretty.activate
    def test_generate_token(self):
        """generate_token() should return a dict with the expected keys"""
        json_body = json.dumps(self.mock_token)
        httpretty.register_uri(
            httpretty.POST,
            self.mock_token_url,
            body=json_body,
            status=201,
            content_type="application/json",
        )

        c = self.client
        token = c.generate_token("foo", "bar")

        self.assertEqual(token["access_token"], self.mock_token["access_token"])
        self.assertEqual(token["refresh_token"], self.mock_token["refresh_token"])

    @httpretty.activate
    def test_token_refresh(self):
        """expired tokens should refresh automatically, the new token should be passed to token_updater()"""

        def token_updater(token):
            self.assertEqual(token["access_token"], self.mock_token["access_token"])
            self.assertEqual(token["refresh_token"], self.mock_token["refresh_token"])

        json_body_token = json.dumps(self.mock_token)
        httpretty.register_uri(
            httpretty.POST,
            self.mock_token_url,
            body=json_body_token,
            status=201,
            content_type="application/json",
        )

        json_body_incident = json.dumps(
            {"result": [{"number": self.mock_incident_number}]}
        )
        httpretty.register_uri(
            httpretty.GET,
            "%s%s" % (self.client.base_url, "/api/now/table/incident"),
            body=json_body_incident,
            status=200,
            content_type="application/json",
        )

        c = self.client
        c.token_updater = token_updater
        c.set_token(self.mock_token_expired)

        r = c.query(table="incident", query={}).get_one()
        number = r["number"]

        self.assertEqual(number, self.mock_incident_number)
