# -*- coding: utf-8 -*-

import warnings
import logging

from oauthlib.oauth2 import LegacyApplicationClient
from oauthlib.oauth2.rfc6749.errors import OAuth2Error
from requests_oauthlib import OAuth2Session

from .client import Client
from .exceptions import InvalidUsage, MissingToken, TokenCreateError

logger = logging.getLogger("pysnow")


class OAuthClient(Client):
    """Pysnow `Client` with extras for oauth session and token handling.

    :param client_id: client_id from ServiceNow
    :param client_secret: client_secret from ServiceNow
    :param token_updater: function called when a token has been refreshed
    :param kwargs: kwargs passed along to :class:`pysnow.Client`
    """

    token = None

    def __init__(
        self, client_id=None, client_secret=None, token_updater=None, **kwargs
    ):

        if not (client_secret and client_id):
            raise InvalidUsage("You must supply a client_id and client_secret")

        if kwargs.get("session") or kwargs.get("user"):
            warnings.warn(
                "pysnow.OAuthClient manages sessions internally, "
                "provided user / password credentials or sessions will be ignored."
            )

        # Forcibly set session, user and password
        kwargs["user"] = None
        kwargs["password"] = None

        super(OAuthClient, self).__init__(**kwargs)

        self.token_updater = token_updater
        self.client_id = client_id
        self.client_secret = client_secret

        self.token_url = "%s/oauth_token.do" % self.base_url

    def _get_oauth_session(self):
        """Creates a new OAuth session

        :return:
            - OAuth2Session object
        """

        return self._get_session(
            OAuth2Session(
                client_id=self.client_id,
                token=self.token,
                token_updater=self.token_updater,
                auto_refresh_url=self.token_url,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
        )

    def set_token(self, token):
        """Validate and set token

        :param token: the token (dict) to set
        """

        if not token:
            self.token = None
            return

        expected_keys = [
            "token_type",
            "refresh_token",
            "access_token",
            "scope",
            "expires_in",
            "expires_at",
        ]
        if not isinstance(token, dict) or not set(token) >= set(expected_keys):
            raise InvalidUsage(
                "Expected a token dictionary containing the following keys: {0}".format(
                    expected_keys
                )
            )

        # Set sanitized token
        self.token = dict((k, v) for k, v in token.items() if k in expected_keys)

    def _legacy_request(self, *args, **kwargs):
        """Makes sure token has been set, then calls parent to create a new :class:`pysnow.LegacyRequest` object

        :param args: args to pass along to _legacy_request()
        :param kwargs: kwargs to pass along to _legacy_request()
        :return:
            - :class:`pysnow.LegacyRequest` object
        :raises:
            - MissingToken: If token hasn't been set
        """

        if isinstance(self.token, dict):
            self.session = self._get_oauth_session()
            return super(OAuthClient, self)._legacy_request(*args, **kwargs)

        raise MissingToken(
            "You must set_token() before creating a legacy request with OAuthClient"
        )

    def resource(self, api_path=None, base_path="/api/now", chunk_size=None):
        """Overrides :meth:`resource` provided by :class:`pysnow.Client` with extras for OAuth

        :param api_path: Path to the API to operate on
        :param base_path: (optional) Base path override
        :param chunk_size: Response stream parser chunk size (in bytes)
        :return:
            - :class:`Resource` object
        :raises:
            - InvalidUsage: If a path fails validation
        """

        if isinstance(self.token, dict):
            self.session = self._get_oauth_session()
            return super(OAuthClient, self).resource(api_path, base_path, chunk_size)

        raise MissingToken(
            "You must set_token() before creating a resource with OAuthClient"
        )

    def generate_token(self, user, password):
        """Takes user and password credentials and generates a new token

        :param user: user
        :param password: password
        :return:
            - dictionary containing token data
        :raises:
            - TokenCreateError: If there was an error generating the new token
        """

        logger.debug("(TOKEN_CREATE) :: User: %s" % user)

        session = OAuth2Session(
            client=LegacyApplicationClient(client_id=self.client_id)
        )

        try:
            return dict(
                session.fetch_token(
                    token_url=self.token_url,
                    username=user,
                    password=password,
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                )
            )
        except OAuth2Error as exception:
            raise TokenCreateError(
                "Error creating user token",
                exception.description,
                exception.status_code,
            )
