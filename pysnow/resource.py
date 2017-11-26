# -*- coding: utf-8 -*-

from .request import Request


class Resource(object):
    _report = None

    def __init__(self, *args, **kwargs):
        """Takes arguments used to perform a HTTP request

        :param method: HTTP request method
        """

        self._base_path = kwargs.get('base_path', '/api/now')
        self._api_path = kwargs.get('api_path')
        self._base_url = kwargs.get('base_url')

        self._url = self._get_url()
        self._request = Request(self._url, *args, resource=self, **kwargs)

    def __repr__(self):
        return '<%s [%s]>' % (self.__class__.__name__, self.path)

    @property
    def path(self):
        return "%s" % self._base_path + self._api_path

    def _get_url(self, api_path_override=None, sys_id=None):
        api_path = api_path_override or self._api_path
        url_str = self._base_url + self._base_path + api_path

        if sys_id:
            return "%s/%s" % (url_str, sys_id)

        return url_str

    @property
    def report(self):
        return self._request.get_report()

    def get(self, *args, **kwargs):
        return self._request.all(*args, **kwargs)

    def get_first(self, *args, **kwargs):
        return self._request.one(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self._request.insert(*args, **kwargs)

