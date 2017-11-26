# -*- coding: utf-8 -*-

import warnings
import re
import inspect

import requests
from requests.auth import HTTPBasicAuth

import pysnow
from pysnow.exceptions import InvalidUsage

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
                 generator_size=500,
                 session=None):
        """Creates a client ready to handle requests

        Note on `generator_size` and `limit` : both of these parameters sets sysparm_limit,
        setting `limit` for a request effectively disables the advantages of using generators, as this sets
        `sysparm_suppress_pagination_header` to True (disables link headers), which the request generators relies on.
        This is a limitation in the ServiceNow API and can't be fixed in the pysnow library.

        :param instance: instance name, used to construct host
        :param host: host can be passed as an alternative to instance
        :param user: user name
        :param password: password
        :param raise_on_empty: whether or not to raise an exception on 404 (no matching records)
        :param request_params: request params to send with requests
        :param use_ssl: Enable or disable SSL
        :param generator_size: Decides the size of each yield, a higher value might increases performance some but
        will cause pysnow to consume more memory.
        :param session: a requests session object
        """

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
        self.generator_size = generator_size

        self.base_url = self._get_base_url()
        self.session = self._get_session(session)

    def _get_session(self, session):
        if not session:
            s = requests.Session()
            s.auth = HTTPBasicAuth(self._user, self._password)
        else:
            s = session

        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})

        return s

    def _get_base_url(self):
        if self.instance is not None:
            self.host = "%s.service-now.com" % self.instance

        if self.use_ssl is True:
            return "https://%s" % self.host

        return "http://%s" % self.host.rstrip('/')

    def _validate_path(self, path):
        if not isinstance(path, str) or not re.match('^/(?:[._a-zA-Z0-9-]/?)+[^/]$', path):
            raise InvalidUsage(
                "Path validation failed - Expected: '/<component>[/component], got: %s" % path
            )

    def _legacy_request(self, method, table, **kwargs):
        """Returns a LegacyRequest object. Uses old Request, compatible with Client.query and Client.insert

        :param method: HTTP method
        :param table: Table to operate on
        :return: `Request` object
        """

        warnings.warn("`%s` is deprecated and will be removed in a future release. "
                      "Please use `request()` instead." % inspect.stack()[1][3])

        return pysnow.LegacyRequest(method,
                                    table,
                                    request_params=self.request_params,
                                    raise_on_empty=self.raise_on_empty,
                                    session=self.session,
                                    instance=self.instance,
                                    base_url=self.base_url,
                                    **kwargs)

    def resource(self, api_path=None, base_path='/api/now', **kwargs):
        """Validates the api_path before passing it along to pysnow.Request

        :param api_path: Path to the API to operate on
        :return: pysnow.Request
        """

        for path in [api_path, base_path]:
            self._validate_path(path)

        return pysnow.Resource(api_path=api_path,
                               base_path=base_path,
                               request_params=self.request_params,
                               raise_on_empty=self.raise_on_empty,
                               session=self.session,
                               instance=self.instance,
                               base_url=self.base_url,
                               generator_size=self.generator_size,
                               **kwargs)

    def query(self, table, **kwargs):
        """Query (GET) request wrapper.

        :param table: table to perform query on
        :param kwargs: Keyword arguments passed along to `Request`
        :return: `Request` object
        """
        return self._legacy_request('GET', table, **kwargs)

    def insert(self, table, payload, **kwargs):
        """Insert (POST) request wrapper

        :param table: table to insert on
        :param payload: update payload (dict)
        :param kwargs: Keyword arguments passed along to `Request`
        :return: New record content
        """
        r = self._legacy_request('POST', table, **kwargs)
        return r.insert(payload)

