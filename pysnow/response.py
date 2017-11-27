# -*- coding: utf-8 -*-

from requests.exceptions import HTTPError

from pysnow.exceptions import (ResponseError,
                               NoResults,
                               UnexpectedResponseFormat,
                               MissingResult)


class Response(object):
    records = -1

    def __init__(self, response, raise_on_empty):
        self.method = response.request.method
        self.status_code = response.status_code
        self._raise_on_empty = raise_on_empty

        self.response = response

        if 'X-Total-Count' in response.headers:
            self.records = int(response.headers['X-Total-Count'])

        if self.method == 'DELETE' and self.status_code == 204:
            self._content = {'result': {'status': 'record deleted'}}
        else:
            self._content = self._parse_response(response)

    def _parse_response(self, response):
        try:
            response = response.json()
        except ValueError:
            raise UnexpectedResponseFormat('Expected JSON in response, got something else. '
                                           'Have you enabled the REST API in ServiceNow?')

        return self._validate_response(response)

    def _validate_response(self, response):
        if 'error' in response:
            raise ResponseError(response['error'])
        elif 'result' not in response:
            raise MissingResult('The expected `result` key was missing in the response from ServiceNow. '
                                'Cannot continue')

        try:
            self.response.raise_for_status()
        except HTTPError:
            # Versions prior to Helsinki returns 404 on empty result sets
            if self.status_code == 404:
                if self._raise_on_empty is True:
                    raise NoResults('Query yielded no results')
                else:
                    return {}
            raise

        # Helsinki and later returns status 200 instead of 404 on empty result sets
        if len(response['result']) < 1:
            if self._raise_on_empty is True:
                raise NoResults('Query yielded no results')

            return {'result': [{}]}

        return response

    @property
    def result(self):
        return self._content['result']

