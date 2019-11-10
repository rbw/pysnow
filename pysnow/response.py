# -*- coding: utf-8 -*-

import ijson

from ijson.common import ObjectBuilder
from itertools import chain
from .exceptions import (
    ResponseError,
    NoResults,
    InvalidUsage,
    MultipleResults,
    EmptyContent,
    MissingResult,
)


class Response(object):
    """Takes a :class:`requests.Response` object and performs deserialization and validation.

    :param response: :class:`requests.Response` object
    :param resource: parent :class:`resource.Resource` object
    :param chunk_size: Read and return up to this size (in bytes) in the stream parser
    """

    def __init__(self, response, resource, chunk_size=8192, stream=False):
        self._response = response
        self._chunk_size = chunk_size
        self._count = 0
        self._resource = resource
        self._stream = stream

    @property
    def headers(self):
        return self._response.headers

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, count):
        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError("Count must be an integer")

        self._count = count

    def __getitem__(self, key):
        return self.one().get(key)

    def __repr__(self):
        return "<%s [%d - %s]>" % (
            self.__class__.__name__,
            self._response.status_code,
            self._response.request.method,
        )

    def _parse_response(self):
        """Looks for `result.item` (array), `result` (object) and `error` (object) keys and parses
        the raw response content (stream of bytes)

        :raise:
            - ResponseError: If there's an error in the response
            - MissingResult: If no result nor error was found
        """

        response = self._get_response()

        has_result_single = False
        has_result_many = False
        has_error = False

        builder = ObjectBuilder()

        for prefix, event, value in ijson.parse(
            response.raw, buf_size=self._chunk_size
        ):
            if (prefix, event) == ("error", "start_map"):
                # Matched ServiceNow `error` object at the root
                has_error = True
            elif prefix == "result" and event in ["start_map", "start_array"]:
                # Matched ServiceNow `result`
                if event == "start_map":  # Matched object
                    has_result_single = True
                elif event == "start_array":  # Matched array
                    has_result_many = True

            if has_result_many:
                # Build the result
                if (prefix, event) == ("result.item", "end_map"):
                    # Reached end of object. Set count and yield
                    builder.event(event, value)
                    self.count += 1
                    yield getattr(builder, "value")
                elif prefix.startswith("result.item"):
                    # Build the result object
                    builder.event(event, value)
            elif has_result_single:
                if (prefix, event) == ("result", "end_map"):
                    # Reached end of the result object. Set count and yield.
                    builder.event(event, value)
                    self.count += 1
                    yield getattr(builder, "value")
                elif prefix.startswith("result"):
                    # Build the error object
                    builder.event(event, value)
            elif has_error:
                if (prefix, event) == ("error", "end_map"):
                    # Reached end of the error object - raise ResponseError exception
                    raise ResponseError(getattr(builder, "value"))
                elif prefix.startswith("error"):
                    # Build the error object
                    builder.event(event, value)

        if (has_result_single or has_result_many) and self.count == 0:  # Results empty
            return

        if not (
            has_result_single or has_result_many or has_error
        ):  # None of the expected keys were found
            raise MissingResult(
                "The expected `result` key was missing in the response. Cannot continue"
            )

    def _get_response(self):
        response = self._response

        # Raise an HTTPError if we hit a non-200 status code
        response.raise_for_status()

        if response.request.method == "GET" and response.status_code == 202:
            # GET request with a "202: no content" response: Raise NoContent Exception.
            raise EmptyContent(
                "Unexpected empty content in response for GET request: {}".format(
                    response.request.url
                )
            )

        return response

    def _get_streamed_response(self):
        """Parses byte stream (memory efficient)

        :return: Parsed JSON
        """

        yield self._parse_response()

    def _get_buffered_response(self):
        """Returns a buffered response

        :return: Buffered response
        """

        response = self._get_response()

        if response.request.method == "DELETE" and response.status_code == 204:
            return [{"status": "record deleted"}], 1

        result = self._response.json().get("result", None)

        if result is None:
            raise MissingResult(
                "The expected `result` key was missing in the response. Cannot continue"
            )

        length = 0

        if isinstance(result, list):
            length = len(result)
        elif isinstance(result, dict):
            result = [result]
            length = 1

        return result, length

    def all(self):
        """Returns a chained generator response containing all matching records

        :return:
            - Iterable response
        """

        if self._stream:
            return chain.from_iterable(self._get_streamed_response())

        return self._get_buffered_response()[0]

    def first(self):
        """Return the first record or raise an exception if the result doesn't contain any data

        :return:
            - Dictionary containing the first item in the response content

        :raise:
            - NoResults: If no results were found
        """

        if not self._stream:
            raise InvalidUsage("first() is only available when stream=True")

        try:
            content = next(self.all())
        except StopIteration:
            raise NoResults("No records found")

        return content

    def first_or_none(self):
        """Return the first record or None

        :return:
            - Dictionary containing the first item or None
        """

        try:
            return self.first()
        except NoResults:
            return None

    def one(self):
        """Return exactly one record or raise an exception.

        :return:
            - Dictionary containing the only item in the response content

        :raise:
            - MultipleResults: If more than one records are present in the content
            - NoResults: If the result is empty
        """

        result, count = self._get_buffered_response()

        if count == 0:
            raise NoResults("No records found")
        elif count > 1:
            raise MultipleResults("Expected single-record result, got multiple")

        return result[0]

    def one_or_none(self):
        """Return at most one record or raise an exception.

        :return:
            - Dictionary containing the matching record or None

        :raise:
            - MultipleResults: If more than one records are present in the content
        """

        try:
            return self.one()
        except NoResults:
            return None

    def update(self, payload):
        """Convenience method for updating a fetched record

        :param payload: update payload
        :return: update response object
        """

        return self._resource.update({"sys_id": self["sys_id"]}, payload)

    def delete(self):
        """Convenience method for deleting a fetched record

        :return: delete response object
        """

        return self._resource.delete({"sys_id": self["sys_id"]})

    def upload(self, *args, **kwargs):
        """Convenience method for attaching files to a fetched record

        :param args: args to pass along to `Attachment.upload`
        :param kwargs: kwargs to pass along to `Attachment.upload`
        :return: upload response object
        """

        return self._resource.attachments.upload(self["sys_id"], *args, **kwargs)
