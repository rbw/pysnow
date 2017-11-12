# -*- coding: utf-8 -*-

import requests
import warnings
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from pysnow import request
from pysnow.exceptions import InvalidUsage, MissingToken

warnings.simplefilter("always", DeprecationWarning)


class Client(object):
    def __init__(self,
                 instance=None,
                 host=None,
                 user=None,
                 password=None,
                 raise_on_empty=True,
                 request_params=None,
                 use_ssl=True,
                 session=None):
        """Creates a client ready to handle requests

        :param instance: instance name, used to construct host
        :param host: host can be passed as an alternative to instance
        :param user: username
        :param password: password
        :param raise_on_empty: whether or not to raise an exception on 404 (no matching records)
        :param request_params: request params to send with requests
        :param use_ssl: Enable or disable SSL
        :param session: a requests session object
        """

        if (host and instance) is not None:
            raise InvalidUsage("Instance and host are mutually exclusive, you cannot use both.")

        if type(use_ssl) is not bool:
            raise InvalidUsage("Argument use_ssl must be of type bool")

        if type(raise_on_empty) is not bool:
            raise InvalidUsage("Argument raise_on_empty must be of type bool")

        if not (host or instance):
            raise InvalidUsage("You must supply an instance name or a host")

        if not (user and password) and not session:
            raise InvalidUsage("You must provide either username and password or a session object")
        elif (user and session) is not None:
            raise InvalidUsage("Provide either username and password or a session, not both.")

        if request_params is not None:
            if isinstance(request_params, dict):
                self.request_params = request_params
            else:
                raise InvalidUsage("Request params must be of type dict")
        else:
            self.request_params = {}

        self.instance = instance
        self.host = host
        self._user = user
        self._password = password
        self.raise_on_empty = raise_on_empty
        self.use_ssl = use_ssl

        self.base_url = self._get_base_url()
        self.session = self._get_session(session)

    def _get_session(self, session):
        if not session:
            s = requests.Session()
            s.auth = requests.auth.HTTPBasicAuth(self._user, self._password)
        else:
            s = session

        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})

        return s

    def _get_base_url(self):
        if self.instance is not None:
            self.host = "%s.service-now.com" % self.instance

        if self.use_ssl is True:
            return "https://%s" % self.host

        return "http://%s" % self.host

    def _request(self, method, table, **kwargs):
        """Creates and returns a new `Request` object, takes some basic settings from the `Client` object and
        passes along to the `Request` constructor

        :param method: HTTP method
        :param table: Table to operate on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """
        return request.Request(method,
                               table,
                               request_params=self.request_params,
                               raise_on_empty=self.raise_on_empty,
                               session=self.session,
                               instance=self.instance,
                               base_url=self.base_url,
                               **kwargs)

    def query(self, table, **kwargs):
        """Query (GET) request wrapper.

        :param table: table to perform query on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """
        return self._request('GET', table, **kwargs)

    def insert(self, table, payload, **kwargs):
        """Insert (POST) request wrapper

        :param table: table to insert on
        :param payload: update payload (dict)
        :param kwargs: Keyword arguments passed along to `Request`
        :return: New record content
        """
        r = self._request('POST', table, **kwargs)
        return r.insert(payload)


class OAuthClient(Client):
    """Pysnow `Client` with extras for oauth session and token handling.

    This API exposes two extra public methods:
    1) generate_token(user, pass)
       - This method takes user and password credentials in order to generate a new OAuth token, that can be stored
         outside the context of pysnow, e.g. in a session or database.
    2) set_token(token)
       - Takes an OAuth token (dict) and internally creates a new pysnow-compatible session,
       enabling pysnow.OAuthClient to create requests.

    :param client_id: client_id from ServiceNow
    :param client_secret: client_secret from ServiceNow
    :param token_updater: callback function called when a token has been refreshed
    :param instance: instance name, used to construct host
    :param host: host can be passed as an alternative to instance
    :param raise_on_empty: whether or not to raise an exception on 404 (no matching records)
    :param request_params: request params to send with requests
    :param use_ssl: Enable or disable SSL
    """
    token = None

    def __init__(self, client_id, client_secret, token_updater=None, *args, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_updater = token_updater

        if kwargs.get('session') or kwargs.get('user'):
            warnings.warn('pysnow.OAuthClient manages sessions internally, '
                          'provided user / password credentials or sessions will be ignored.')

        # Forcibly set session, user and password
        kwargs['session'] = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        kwargs['user'] = None
        kwargs['password'] = None

        super(OAuthClient, self).__init__(*args, **kwargs)

        self.token_url = "%s/oauth_token.do" % self._get_base_url()

    def _get_oauth_session(self):
        """Creates a new OAuth session

        :return: OAuth2Session object
        """

        return OAuth2Session(
            client_id=self.client_id,
            token={
                "refresh_token": self.token['refresh_token'],
                "access_token": self.token['access_token']
            },
            token_updater=self.token_updater,
            auto_refresh_url=self.token_url,
            auto_refresh_kwargs={
                "client_id": self.client_id,
                "client_secret": self.client_secret
            })

    def set_token(self, token):
        """Validates token and creates a pysnow compatible session

        :param token: dict containing the information required to create an OAuth2Session
        """
        expected_keys = {"token_type", "refresh_token", "access_token", "scope", "expires_in", "expires_at"}
        if not expected_keys <= set(token):
            raise InvalidUsage("Token should contain a dictionary obtained from generate_token()")

        self.token = token
        self.session = self._get_oauth_session()

    def _request(self, *args, **kwargs):
        """Checks if token has been set then calls parent

        :return: pysnow.Request object
        """

        if isinstance(self.token, dict):
            return super(OAuthClient, self)._request(*args, **kwargs)

        raise MissingToken("You must set_token() before creating a request with pysnow.OAuthClient")

    def generate_token(self, user, password):
        """Takes user and password credentials and generates a new token

        :param user: user
        :param password: password
        :return: dictionary containing token data
        """
        return dict(self.session.fetch_token(token_url=self.token_url,
                                             username=user,
                                             password=password,
                                             client_id=self.client_id,
                                             client_secret=self.client_secret))


