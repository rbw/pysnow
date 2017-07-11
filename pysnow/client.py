# -*- coding: utf-8 -*-

import requests
import warnings
from pysnow import request
from pysnow.exceptions import InvalidUsage

warnings.simplefilter("always", DeprecationWarning)


class Client(object):
    def __init__(self, instance, user=None, password=None, raise_on_empty=True,
                 default_payload=None, request_params=None, session=None):
        """Sets configuration and creates a session object used in `Request` later on

        You must either provide a username and password or a requests session.
        If you provide a requests session it must handle the authentication.
        For example, providing a session can be used to do OAuth authentication.

        :param instance: instance name, used to resolve FQDN in `Request`
        :param user: username
        :param password: password
        :param raise_on_empty: whether or not to raise an exception on 404 (no matching records)
        :param request_params: request params to send with requests
        :param session: a requests session object
        """

        if ((not (user and password)) and not session) or ((user or password) and session):
            raise InvalidUsage("You must either provide username and password or a session")

        # Connection properties
        self.instance = instance
        self._user = user
        self._password = password
        self.raise_on_empty = raise_on_empty
        self.request_params = self.default_payload = {}

        # default_payload is deprecated, let user know
        if default_payload is not None:
            warnings.warn("default_payload is deprecated, please use request_params instead", DeprecationWarning)
            self.request_params = self.default_payload = default_payload

        if request_params is not None:
            self.request_params = request_params

        # Sets request parameters for requests
        if not isinstance(self.request_params, dict):
            raise InvalidUsage("Payload must be of type dict")

        # Create new session object
        self.session = self._get_session(session)

    def _get_session(self, session):
        """Creates and returns a new session object with the credentials passed to the constructor

        :return: session object
        """
        if session:
            s = session
        else:
            s = requests.Session()
            s.auth = requests.auth.HTTPBasicAuth(self._user, self._password)

        s.headers.update({'content-type': 'application/json', 'accept': 'application/json'})
        return s

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

