# -*- coding: utf-8 -*-

import inspect
import re
import warnings

import requests
from requests.auth import HTTPBasicAuth

from .legacy.request import LegacyRequest
from .exceptions import InvalidUsage
from .resource import Resource

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
    :param generator_size: Decides the size of each yield, a higher value might increases performance some but
    will cause pysnow to consume more memory when serving big results. Defaults to 500 (records).
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
                 generator_size=50,
                 session=None):

        if (host and instance) is not None:
            raise InvalidUsage("Arguments 'instance' and 'host' are mutually exclusive, you cannot use both.")

        if type(generator_size) is not int:
            raise InvalidUsage("Argument 'generator_size' must be of type int")

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

        if request_params is not None:
            if not isinstance(request_params, dict):
                raise InvalidUsage("Request params must be of type dict")
            self.request_params = request_params
        else:
            self.request_params = {}

        self.instance = instance
        self.host = host
        self._user = user
        self._password = password
        self.raise_on_empty = raise_on_empty
        self.use_ssl = use_ssl
        self.generator_size = generator_size

        self.base_url = self._get_base_url()
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

    def _get_base_url(self):
        """Formats the base URL using either `host` or `instance`

        :return: Base URL string
        """
        if self.instance is not None:
            self.host = "%s.service-now.com" % self.instance

        if self.use_ssl is True:
            return "https://%s" % self.host

        return "http://%s" % self.host.rstrip('/')

    def _validate_path(self, path):
        """Validates the provided path

        :param path: path to validate (string)
        :raise:
            :InvalidUsage: If validation fails.
        """

        if not isinstance(path, str) or not re.match('^/(?:[._a-zA-Z0-9-]/?)+[^/]$', path):
            raise InvalidUsage(
                "Path validation failed - Expected: '/<component>[/component], got: %s" % path
            )

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

    def resource(self, api_path=None, base_path='/api/now', request_params=None, enable_reporting=False):
        """Creates a new :class:`Resource` object after validating paths

        :param api_path: Path to the API to operate on
        :param base_path: (optional) Base path override
        :param request_params: (optional) Request params override for this resource
        :param enable_reporting: Set to True to enable detailed resource-request-response reporting on the
        :class:`pysnow.Response` object
        :return: :class:`Resource` object
        """

        for path in [api_path, base_path]:
            self._validate_path(path)

        if request_params is not None:
            if not isinstance(request_params, dict):
                raise InvalidUsage("Request params must be of type dict")
        else:
            request_params = self.request_params

        if type(enable_reporting) is not bool:
            raise InvalidUsage("Argument 'enable_reporting' must be of type bool")

        return Resource(api_path=api_path,
                        base_path=base_path,
                        request_params=request_params,
                        raise_on_empty=self.raise_on_empty,
                        enable_reporting=enable_reporting,
                        session=self.session,
                        base_url=self.base_url,
                        generator_size=self.generator_size)

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

