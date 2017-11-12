# -*- coding: utf-8 -*-

import warnings
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from pysnow import Client
from pysnow.exceptions import InvalidUsage, MissingToken

warnings.simplefilter("always", DeprecationWarning)


class OAuthClient(Client):
    """Pysnow `Client` with extras for oauth session and token handling.

    This API exposes two extra public methods:

    - generate_token(user, pass)
        - This method takes user and password credentials to generate a new OAuth token that can be stored outside the context of pysnow, e.g. in a session or database.


    - set_token(token)
        - Takes an OAuth token (dict) and internally creates a new pysnow-compatible session, enabling pysnow.OAuthClient to create requests.


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

    def __init__(self, client_id=None, client_secret=None, token_updater=None, *args, **kwargs):
        if not (client_secret and client_id):
            raise InvalidUsage('You must supply a client_id and client_secret')

        if token_updater is None:
            warnings.warn("No token_updater was supplied to OauthClient, you won't be notified of refreshes")

        if kwargs.get('session') or kwargs.get('user'):
            warnings.warn('pysnow.OAuthClient manages sessions internally, '
                          'provided user / password credentials or sessions will be ignored.')

        # Forcibly set session, user and password
        kwargs['session'] = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
        kwargs['user'] = None
        kwargs['password'] = None

        super(OAuthClient, self).__init__(*args, **kwargs)

        self.token_updater = token_updater
        self.client_id = client_id
        self.client_secret = client_secret

        self.token_url = "%s/oauth_token.do" % self._get_base_url()

    def _get_oauth_session(self):
        """Creates a new OAuth session

        :return: OAuth2Session object
        """

        return OAuth2Session(
            client_id=self.client_id,
            token=self.token,
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

        expected_keys = set(("token_type", "refresh_token", "access_token", "scope", "expires_in", "expires_at"))
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


