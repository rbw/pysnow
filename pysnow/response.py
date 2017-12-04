# -*- coding: utf-8 -*-

import ijson.backends.yajl2_cffi as ijson
from ijson.common import ObjectBuilder

from requests.exceptions import HTTPError

from .exceptions import (ResponseError,
                         NoResults,
                         MultipleResults,
                         UnexpectedResponseFormat,
                         MissingResult)


class Response(object):
    """Takes a :class:`requests.Response` object and performs deserialization and validation and offers
    an interface for obtaining the content in a safe manner.

    :param response: :class:`request.Response` object
    :param raise_on_empty: whether or not to raise an exception if the content doesn't contain any records
    """

    def __init__(self, response, raise_on_empty):
        self._raise_on_empty = raise_on_empty
        self._response = response
        self.count = 0

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

        if 'error' in content:
            raise ResponseError(content['error'])

        # In rare cases `result` may not be present in the response content. Let the user know.
        if 'result' not in content:
            raise MissingResult('The expected `result` key was missing in the response from ServiceNow. '
                                'Cannot continue')

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
        #self.add_record_count(len(content['result']))
        self.count = self.count + int(count)

    def __repr__(self):
        return '<%s [%d - %s]>' % (self.__class__.__name__, self._response.status_code, self._response.request.method)

    def all(self):
        """Yields streamed response

        :return: Iterable response
        """

        key = '-'
        for prefix, event, value in ijson.parse(self._response.raw):
            if prefix == '' and event == 'map_key':  # found new object at the root
                key = value  # mark the key value
                builder = ObjectBuilder()
            elif key == 'error' and event == 'end_map':
                raise ResponseError(getattr(builder, 'value'))
            elif prefix.startswith(key):  # while at this key, build the object
                builder.event(event, value)
                if event == 'end_map':  # found the end of an object at the current key, yield
                    yield getattr(builder, 'value')

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
            raise MultipleResults("Expected single-record result, got multiple")
        elif len(content) < 1:
            raise NoResults("Expected single-record result, got none")

        return content[0]

    def one_or_none(self):
        """Returns a dictionary if the content contains exactly one item, or None

        :return: Dictionary containing the only item in the response content, or None
        """

        try:
            return self.one()
        except NoResults:
            return None
