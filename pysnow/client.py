# -*- coding: utf-8 -*-

import logging
import inspect
import warnings

import requests
import pysnow

from requests.auth import HTTPBasicAuth
from .legacy_request import LegacyRequest
from .exceptions import InvalidUsage
from .resource import Resource
from .url_builder import URLBuilder
from .params_builder import ParamsBuilder

logger = logging.getLogger("pysnow")


class Client(object):
    """User-created Client object.

    :param instance: Instance name, used to construct host
    :param host: Host can be passed as an alternative to instance
    :param user: User name
    :param password: Password
    :param raise_on_empty: Whether or not to raise an exception on 404 (no matching records), defaults to True
    :param request_params: Request params to send with requests globally (deprecated)
    :param use_ssl: Enable or disable the use of SSL, defaults to True
    :param session: Optional :class:`requests.Session` object to use instead of passing user/pass to :class:`Client`
    :raises:
        - InvalidUsage: On argument validation error
    """

    def __init__(
        self,
        instance=None,
        host=None,
        user=None,
        password=None,
        raise_on_empty=None,
        request_params=None,
        use_ssl=True,
        session=None,
    ):

        if (host and instance) is not None:
            raise InvalidUsage(
                "Arguments 'instance' and 'host' are mutually exclusive, you cannot use both."
            )

        if type(use_ssl) is not bool:
            raise InvalidUsage("Argument 'use_ssl' must be of type bool")

        if raise_on_empty is None:
            self.raise_on_empty = True
        elif type(raise_on_empty) is bool:
            warnings.warn(
                "The use of the `raise_on_empty` argument is deprecated and will be removed in a "
                "future release.",
                DeprecationWarning,
            )

            self.raise_on_empty = raise_on_empty
        else:
            raise InvalidUsage("Argument 'raise_on_empty' must be of type bool")

        if not (host or instance):
            raise InvalidUsage("You must supply either 'instance' or 'host'")

        if not isinstance(self, pysnow.OAuthClient):
            if not (user and password) and not session:
                raise InvalidUsage(
                    "You must supply either username and password or a session object"
                )
            elif (user and session) is not None:
                raise InvalidUsage(
                    "Provide either username and password or a session, not both."
                )

        self.parameters = ParamsBuilder()

        if request_params is not None:
            warnings.warn(
                "The use of the `request_params` argument is deprecated and will be removed in a "
                "future release. Please use Client.parameters instead.",
                DeprecationWarning,
            )

            self.parameters.add_custom(request_params)

        self.request_params = request_params or {}
        self.instance = instance
        self.host = host
        self._user = user
        self._password = password
        self.use_ssl = use_ssl
        self.base_url = URLBuilder.get_base_url(use_ssl, instance, host)

        if not isinstance(self, pysnow.OAuthClient):
            self.session = self._get_session(session)
        else:
            self.session = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def close(self):
        self.session.close()

    def _get_session(self, session):
        """Creates a new session with basic auth, unless one was provided, and sets headers.

        :param session: (optional) Session to re-use
        :return:
            - :class:`requests.Session` object
        """

        if not session:
            logger.debug("(SESSION_CREATE) User: %s" % self._user)
            s = requests.Session()
            s.auth = HTTPBasicAuth(self._user, self._password)
        else:
            logger.debug("(SESSION_CREATE) Object: %s" % session)
            s = session

        s.headers.update(
            {
                "content-type": "application/json",
                "accept": "application/json",
                "User-Agent": "pysnow",
            }
        )

        return s

    def _legacy_request(self, method, table, **kwargs):
        """Returns a :class:`LegacyRequest` object, compatible with Client.query and Client.insert

        :param method: HTTP method
        :param table: Table to operate on
        :return:
            - :class:`LegacyRequest` object
        """

        warnings.warn(
            "`%s` is deprecated and will be removed in a future release. "
            "Please use `resource()` instead." % inspect.stack()[1][3],
            DeprecationWarning,
        )

        return LegacyRequest(
            method,
            table,
            request_params=self.request_params,
            raise_on_empty=self.raise_on_empty,
            session=self.session,
            instance=self.instance,
            base_url=self.base_url,
            **kwargs
        )

    def resource(self, api_path=None, base_path="/api/now", chunk_size=None, **kwargs):
        """Creates a new :class:`Resource` object after validating paths

        :param api_path: Path to the API to operate on
        :param base_path: (optional) Base path override
        :param chunk_size: Response stream parser chunk size (in bytes)
        :param **kwargs: Pass request.request parameters to the Resource object
        :return:
            - :class:`Resource` object
        :raises:
            - InvalidUsage: If a path fails validation
        """

        for path in [api_path, base_path]:
            URLBuilder.validate_path(path)

        return Resource(
            api_path=api_path,
            base_path=base_path,
            parameters=self.parameters,
            chunk_size=chunk_size or 8192,
            session=self.session,
            base_url=self.base_url,
            **kwargs
        )

    def query(self, table, **kwargs):
        """Query (GET) request wrapper.

        :param table: table to perform query on
        :param kwargs: Keyword arguments passed along to `Request`
        :return:
            - List of dictionaries containing the matching records
        """

        return self._legacy_request("GET", table, **kwargs)

    def insert(self, table, payload, **kwargs):
        """Insert (POST) request wrapper

        :param table: table to insert on
        :param payload: update payload (dict)
        :param kwargs: Keyword arguments passed along to `Request`
        :return:
            - Dictionary containing the created record
        """

        r = self._legacy_request("POST", table, **kwargs)
        return r.insert(payload)
