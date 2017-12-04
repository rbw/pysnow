# -*- coding: utf-8 -*-

import inspect
import warnings

import requests
from requests.auth import HTTPBasicAuth

from .legacy.request import LegacyRequest
from .exceptions import InvalidUsage
from .resource import Resource
from .url_builder import URLBuilder
from .sysparms import Sysparms

warnings.simplefilter("always", DeprecationWarning)


class Client(object):
    """User-created :class:`pysnow.Client` object.

    :param instance: Instance name, used to construct host
    :param host: Host can be passed as an alternative to instance
    :param user: User name
    :param password: Password
    :param raise_on_empty: Whether or not to raise an exception on 404 (no matching records), defaults to True
    :param request_params: Request params to send with requests globally
    :param use_ssl: Enable or disable SSL, defaults to True
    :param session: Optional :class:`requests.Session` object to use instead of passing user/pass
    to :class:`Client`
    :raise:
        :InvalidUsage: If validation fails for an input argument
    """

    def __init__(self,
                 instance=None,
                 host=None,
                 user=None,
                 password=None,
                 raise_on_empty=True,
                 request_params=None,
                 use_ssl=True,
                 session=None):

        if (host and instance) is not None:
            raise InvalidUsage("Arguments 'instance' and 'host' are mutually exclusive, you cannot use both.")

        if type(use_ssl) is not bool:
            raise InvalidUsage("Argument 'use_ssl' must be of type bool")

        if type(raise_on_empty) is not bool:
            raise InvalidUsage("Argument 'raise_on_empty' must be of type bool")

        if not (host or instance):
            raise InvalidUsage("You must supply either 'instance' or 'host'")

        if not (user and password) and not session:
            raise InvalidUsage("You must supply either username and password or a session object")
        elif (user and session) is not None:
            raise InvalidUsage("Provide either username and password or a session, not both.")

        self._sysparms = Sysparms()

        if request_params is not None:
            try:
                self._sysparms.add_foreign(request_params)
            except TypeError:
                raise InvalidUsage("Request params must be of type dict")

        self.request_params = request_params or {}
        self.instance = instance
        self.host = host
        self._user = user
        self._password = password
        self.raise_on_empty = raise_on_empty
        self.use_ssl = use_ssl

        self.base_url = URLBuilder.get_base_url(use_ssl, instance, host)
        self.session = self._get_session(session)

    def _get_session(self, session):
        """Creates a new session with basic auth, unless one was provided, and sets headers.

        :param session: (optional) Session to re-use
        :return: :class:`requests.Session` object
        """
        if not session:
            s = requests.Session()
            s.auth = HTTPBasicAuth(self._user, self._password)
        else:
            s = session

        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})

        return s

    def _legacy_request(self, method, table, **kwargs):
        """Returns a :class:`LegacyRequest` object, compatible with Client.query and Client.insert

        :param method: HTTP method
        :param table: Table to operate on
        :return: :class:`LegacyRequest` object
        """

        warnings.warn("`%s` is deprecated and will be removed in a future release. "
                      "Please use `resource()` instead." % inspect.stack()[1][3], DeprecationWarning)

        return LegacyRequest(method,
                             table,
                             request_params=self.request_params,
                             raise_on_empty=self.raise_on_empty,
                             session=self.session,
                             instance=self.instance,
                             base_url=self.base_url,
                             **kwargs)

    def resource(self, api_path=None, base_path='/api/now'):
        """Creates a new :class:`Resource` object after validating paths

        :param api_path: Path to the API to operate on
        :param base_path: (optional) Base path override
        :return: :class:`Resource` object
        """

        for path in [api_path, base_path]:
            URLBuilder.validate_path(path)

        return Resource(api_path=api_path,
                        base_path=base_path,
                        sysparms=self._sysparms,
                        raise_on_empty=self.raise_on_empty,
                        session=self.session,
                        base_url=self.base_url)

    def query(self, table, **kwargs):
        """Query (GET) request wrapper.

        :param table: table to perform query on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: List of dictionaries containing the matching records
        """

        return self._legacy_request('GET', table, **kwargs)

    def insert(self, table, payload, **kwargs):
        """Insert (POST) request wrapper

        :param table: table to insert on
        :param payload: update payload (dict)
        :param kwargs: Keyword arguments passed along to `Request`
        :return: Dictionary containing the created record
        """

        r = self._legacy_request('POST', table, **kwargs)
        return r.insert(payload)

