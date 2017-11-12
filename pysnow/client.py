# -*- coding: utf-8 -*-

import requests
import warnings
from pysnow import request
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

