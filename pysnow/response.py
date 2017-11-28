# -*- coding: utf-8 -*-

import itertools

from requests.exceptions import HTTPError

from pysnow.exceptions import (ResponseError,
                               NoResults,
                               MultipleResults,
                               UnexpectedResponseFormat,
                               MissingResult,
                               ReportUnavailable)


class Response(object):
    """Takes a :class:`requests.Response` object and performs deserialization and validation and offers
    an interface for obtaining the content in a safe manner.

    :param response: :class:`request.Response <Response>` object
    :param raise_on_empty: whether or not to raise an exception if the content doesn't contain any records
    :param report: :class:`pysnow.request.Report <Report>` object
    :param request_callback: callback function to use when following linked requests
    """

    def __init__(self, response, raise_on_empty, report, request_callback):
        self._raise_on_empty = raise_on_empty
        self._report = report
        self._request_callback = request_callback
        self._response = response
        self.count = 0

        if 'X-Total-Count' in response.headers and self._report is not None:
            self._report.set_x_total_count(int(response.headers['X-Total-Count']))

    @property
    def report(self):
        """Returns a report containing information about the resource-request-response stack.

        :return: :class:`Report <Report>` object
        :raise:
            :ReportUnavailable: If no :class:`pysnow.request.Report <Report>` object is available
        """

        if not self._report:
            raise ReportUnavailable("Reporting was not enabled for this resource")

        return self._report

    def _deserialize_content(self, response):
        """Response content deserialization (JSON string to Dict)

        :param response: :class:`requests.Response` object
        :return: Result dictionary containing a list, of records if any
        :raise:
            :UnexpectedResponseFormat: Raised if deserialization failed
        """

        # Make sure we're dealing with JSON content, if not, let the user know.
        try:
            content = response.json()
        except ValueError:
            raise UnexpectedResponseFormat('Expected JSON in response, got something else. '
                                           'Have you enabled the REST API in ServiceNow?')

        return dict(content)

    def _get_validated_content(self, response):
        """Validates the content after performing deserialization of the JSON body

        :param response: :class:`requests.Response` object
        :return: validated content as list, of records if any.
        :raise:
            :ResponseError: If `error` was present in the content
            :MissingResult: If no `result` was present in the content
            :NoResults: If no records and raise_on_empty is set to True
        """

        # Don't even attempt to deserialize successful delete, as it doesn't contain a body.
        if response.request.method == 'DELETE' and response.status_code == 204:
            return [{'status': 'record deleted'}]

        content = self._deserialize_content(response)

        if 'error' in content:
            raise ResponseError(content['error'])

        # In rare cases `result` may not be present in the response content. Let the user know.
        if 'result' not in content:
            raise MissingResult('The expected `result` key was missing in the response from ServiceNow. '
                                'Cannot continue')

        # Yes, I'm aware this doesn't belong in this function. But it's so damn practical to put here.
        self.add_record_count(len(content['result']))

        if self._report:
            self._report.add_response(response)

        try:
            # Raise an HTTPError if we hit a non-200 status code
            response.raise_for_status()
        except HTTPError:
            # Versions prior to Helsinki returns 404 on empty result sets
            if response.status_code == 404:
                if self._raise_on_empty is True:
                    raise NoResults('Query yielded no results')
                else:
                    return [{}]
            raise

        # Helsinki and later returns status 200 instead of 404 on empty result sets
        if len(content['result']) < 1:
            if self._raise_on_empty is True:
                raise NoResults('Query yielded no results')

            return [{}]

        return content['result']

    def add_record_count(self, count):
        """Updates the record counter

        :param count: Count to be added
        """
        self.count = self.count + int(count)
        if self._report:
            self._report.add_consumed_count(count)

    def _generator_response(self):
        """Yields the deserialized and validated content of the original request response, then follows
        link headers if present on the response.

        :return: generator response
        """

        response = self._response
        yield self._get_validated_content(response)

        # Follow link headers, if present
        while 'next' in response.links:
            url_link = response.links['next']['url']
            response = self._request_callback('GET', url_link)
            yield self._get_validated_content(response)

    def all(self):
        """Creates a chained generator response

        :return: Chained generator response (iterable)
        """

        return itertools.chain.from_iterable(self._generator_response())

    def first(self):
        """Returns the first item in the response content after deserialization and validation

        :return: Dictionary containing the first item in the response content
        :raise:
            :NoResults: If no results were found
        """

        content = self._get_validated_content(self._response)

        if len(content) >= 1:
            return content[0]

        raise NoResults

    def first_or_none(self):
        """Returns the first item in the response content or None

        :return: Dictionary containing the first item in the response content, or None if no records
        """

        try:
            return self.first()
        except NoResults:
            return None

    def one(self):
        """Returns a dictionary if the content contains exactly one item

        :return: Dictionary containing the only item in the response content
        :raise:
            :MultipleResults: If more than one records are present in the content
            :NoResults: If no records are present in the content
        """

        content = self._get_validated_content(self._response)

        if len(content) > 1:
            raise MultipleResults("Unexpected result containing multiple records")
        elif len(content) < 1:
            raise NoResults("Unexpected result containing no records")

        return content[0]

    def one_or_none(self):
        """Returns a dictionary if the content contains exactly one item, or None

        :return: Dictionary containing the only item in the response content, or None
        """

        try:
            return self.one()
        except NoResults:
            return None
