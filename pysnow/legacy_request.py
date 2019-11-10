# -*- coding: utf-8 -*-

import itertools
import json
import os
import six
import ntpath
import warnings

from pysnow.query_builder import QueryBuilder

from .legacy_exceptions import (
    NoRequestExecuted,
    MultipleResults,
    NoResults,
    InvalidUsage,
    UnexpectedResponse,
    MissingResult,
)


class LegacyRequest(object):
    base_path = "api/now"

    def __init__(self, method, table, **kwargs):
        """Takes arguments used to perform a HTTP request

        :param method: HTTP request method
        :param table: table to operate on
        """
        self.method = method
        self.table = table
        self.url_link = None  # Updated when a linked request is iterated on
        self.base_url = kwargs.pop("base_url")
        self.request_params = kwargs.pop("request_params")
        self.raise_on_empty = kwargs.pop("raise_on_empty")
        self.session = kwargs.pop("session")
        self._last_response = None

        if method in ("GET", "DELETE"):
            self.query = kwargs.pop("query")

    @property
    def last_response(self):
        """Return _last_response after making sure an inner `requests.request` has been performed

        :raise:
            :NoRequestExecuted: If no request has been executed
        :return:
            - last response
        """
        if self._last_response is None:
            raise NoRequestExecuted("%s hasn't been executed" % self)
        return self._last_response

    @last_response.setter
    def last_response(self, response):
        """ Sets last_response property
        :param response: `requests.request` response
        """
        self._last_response = response

    @property
    def count(self):
        """ Returns the number of records the query would yield"""
        self.request_params.update({"sysparm_count": True})
        response = self.session.get(
            self._get_stats_url(),
            params=self._get_formatted_query(
                fields=list(), limit=None, order_by=list(), offset=None
            ),
        )

        content = self._get_content(response)

        return int(content["stats"]["count"])

    @property
    def status_code(self):
        """Return last_response.status_code after making sure an inner `requests.request` has been performed

        :return: status_code of last_response
        """
        return self.last_response.status_code

    def _all_inner(self, fields, limit, order_by, offset):
        """Yields all records for the query and follows links if present on the response after validating

        :return: List of records with content
        """
        response = self.session.get(
            self._get_table_url(),
            params=self._get_formatted_query(fields, limit, order_by, offset),
        )

        yield self._get_content(response)
        while "next" in response.links:
            self.url_link = response.links["next"]["url"]
            response = self.session.get(self.url_link)
            yield self._get_content(response)

    def get_all(self, fields=list(), limit=None, order_by=list(), offset=None):
        """DEPRECATED - see get_multiple()"""
        warnings.warn(
            "get_all() is deprecated, please use get_multiple() instead",
            DeprecationWarning,
        )
        return self.get_multiple(fields, limit, order_by, offset)

    def get_multiple(self, fields=list(), limit=None, order_by=list(), offset=None):
        """Wrapper method that takes whatever was returned by the _all_inner() generators and chains it in one result

        The response can be sorted by passing a list of fields to order_by.

        Example:
        get_multiple(order_by=['category', '-created_on']) would sort the category field in ascending order,
        with a secondary sort by created_on in descending order.

        :param fields: List of fields to return in the result
        :param limit: Limits the number of records returned
        :param order_by: Sort response based on certain fields
        :param offset: A number of records to skip before returning records (for pagination)
        :return:
            - Iterable chain object
        """
        return itertools.chain.from_iterable(
            self._all_inner(fields, limit, order_by, offset)
        )

    def get_one(self, fields=list()):
        """Convenience function for queries returning only one result. Validates response before returning.

        :param fields: List of fields to return in the result
        :raise:
            :MultipleResults: if more than one match is found
        :return:
            - Record content
        """
        response = self.session.get(
            self._get_table_url(),
            params=self._get_formatted_query(
                fields, limit=None, order_by=list(), offset=None
            ),
        )

        content = self._get_content(response)
        l = len(content)
        if l > 1:
            raise MultipleResults("Multiple results for get_one()")

        if len(content) == 0:
            return {}

        return content[0]

    def insert(self, payload):
        """Inserts a new record with the payload passed as an argument

        :param payload: The record to create (dict)
        :return:
            - Created record
        """
        response = self.session.post(self._get_table_url(), data=json.dumps(payload))
        return self._get_content(response)

    def delete(self):
        """Deletes the queried record and returns response content after response validation

        :raise:
            :NoResults: if query returned no results
            :NotImplementedError: if query returned more than one result (currently not supported)
        :return:
            - Delete response content (Generally always {'Success': True})
        """
        try:
            result = self.get_one()
            if "sys_id" not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults("Deletion of multiple records is not supported")
        except NoResults as e:
            e.args = ("Cannot delete a non-existing record",)
            raise

        response = self.session.delete(self._get_table_url(sys_id=result["sys_id"]))
        return self._get_content(response)

    def update(self, payload):
        """Updates the queried record with `payload` and returns the updated record after validating the response

        :param payload: Payload to update the record with
        :raise:
            :NoResults: if query returned no results
            :MultipleResults: if query returned more than one result (currently not supported)
        :return:
            - The updated record
        """
        try:
            result = self.get_one()
            if "sys_id" not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults("Update of multiple records is not supported")
        except NoResults as e:
            e.args = ("Cannot update a non-existing record",)
            raise

        if not isinstance(payload, dict):
            raise InvalidUsage("Update payload must be of type dict")

        response = self.session.put(
            self._get_table_url(sys_id=result["sys_id"]), data=json.dumps(payload)
        )
        return self._get_content(response)

    def clone(self, reset_fields=list()):
        """Clones the queried record

        :param reset_fields: Fields to reset
        :raise:
            :NoResults: if query returned no results
            :MultipleResults: if query returned more than one result (currently not supported)
            :UnexpectedResponse: informs the user about what likely went wrong
        :return:
            - The cloned record
        """

        if not isinstance(reset_fields, list):
            raise InvalidUsage("reset_fields must be a `list` of fields")

        try:
            response = self.get_one()
            if "sys_id" not in response:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults("Cloning multiple records is not supported")
        except NoResults as e:
            e.args = ("Cannot clone a non-existing record",)
            raise

        payload = {}

        # Iterate over fields in the result
        for field in response:
            # Ignore fields in reset_fields
            if field in reset_fields:
                continue

            item = response[field]
            # Check if the item is of type dict and has a sys_id ref (value)
            if isinstance(item, dict) and "value" in item:
                payload[field] = item["value"]
            else:
                payload[field] = item

        try:
            return self.insert(payload)
        except UnexpectedResponse as e:
            if e.status_code == 403:
                # User likely attempted to clone a record without resetting a unique field
                e.args = (
                    "Unable to create clone. Make sure unique fields has been reset.",
                )
            raise

    def attach(self, file):
        """Attaches the queried record with `file` and returns the response after validating the response

        :param file: File to attach to the record
        :raise:
            :NoResults: if query returned no results
            :MultipleResults: if query returned more than one result (currently not supported)
        :return:
            - The attachment record metadata
        """
        try:
            result = self.get_one()
            if "sys_id" not in result:
                raise NoResults()
        except MultipleResults:
            raise MultipleResults(
                "Attaching a file to multiple records is not supported"
            )
        except NoResults:
            raise NoResults("Attempted to attach file to a non-existing record")

        if not os.path.isfile(file):
            raise InvalidUsage(
                "Attachment '%s' must be an existing regular file" % file
            )

        response = self.session.post(
            self._get_attachment_url("upload"),
            data={
                "table_name": self.table,
                "table_sys_id": result["sys_id"],
                "file_name": ntpath.basename(file),
            },
            files={"file": open(file, "rb")},
            headers={"content-type": None},  # Temporarily override header
        )
        return self._get_content(response)

    def _get_content(self, response):
        """Checks for errors in the response. Returns response content, in bytes.

        :param response: response object
        :raise:
            :UnexpectedResponse: if the server responded with an unexpected response
        :return:
            - ServiceNow response content
        """
        method = response.request.method
        self.last_response = response

        server_error = {"summary": None, "details": None}

        try:
            content_json = response.json()
            if "error" in content_json:
                e = content_json["error"]
                if "message" in e:
                    server_error["summary"] = e["message"]
                if "detail" in e:
                    server_error["details"] = e["detail"]
        except ValueError:
            content_json = {}

        if method == "DELETE":
            # Make sure the delete operation returned the expected response
            if response.status_code == 204:
                return {"success": True}
            else:
                raise UnexpectedResponse(
                    204,
                    response.status_code,
                    method,
                    server_error["summary"],
                    server_error["details"],
                )
        # Make sure the POST operation returned the expected response
        elif method == "POST" and response.status_code != 201:
            raise UnexpectedResponse(
                201,
                response.status_code,
                method,
                server_error["summary"],
                server_error["details"],
            )
        # It seems that Helsinki and later returns status 200 instead of 404 on empty result sets
        if (
            "result" in content_json and len(content_json["result"]) == 0
        ) or response.status_code == 404:
            if self.raise_on_empty is True:
                raise NoResults("Query yielded no results")
        elif "error" in content_json:
            raise UnexpectedResponse(
                200,
                response.status_code,
                method,
                server_error["summary"],
                server_error["details"],
            )

        if "result" not in content_json:
            raise MissingResult(
                "The request was successful but the content didn't contain the expected 'result'"
            )

        return content_json["result"]

    def _get_table_url(self, **kwargs):
        return self._get_url("table", item=self.table, **kwargs)

    def _get_attachment_url(self, action):
        return self._get_url("attachment", item=action)

    def _get_stats_url(self):
        return self._get_url("stats", item=self.table)

    def _get_url(self, resource, item, sys_id=None):
        """Takes table and sys_id (if present), and returns a URL

        :param resource: API resource
        :param item: API resource item
        :param sys_id: Record sys_id
        :return:
            - url string
        """

        url_str = "%(base_url)s/%(base_path)s/%(resource)s/%(item)s" % (
            {
                "base_url": self.base_url,
                "base_path": self.base_path,
                "resource": resource,
                "item": item,
            }
        )

        if sys_id:
            return "%s/%s" % (url_str, sys_id)

        return url_str

    def _get_formatted_query(self, fields, limit, order_by, offset):
        """
        Converts the query to a ServiceNow-interpretable format
        :return:
            - ServiceNow query
        """

        if not isinstance(order_by, list):
            raise InvalidUsage("Argument order_by should be a `list` of fields")

        if not isinstance(fields, list):
            raise InvalidUsage("Argument fields should be a `list` of fields")

        if isinstance(self.query, QueryBuilder):
            sysparm_query = str(self.query)
        elif isinstance(self.query, dict):  # Dict-type query
            sysparm_query = "^".join(
                ["%s=%s" % (k, v) for k, v in six.iteritems(self.query)]
            )
        elif isinstance(self.query, six.string_types):  # String-type query
            sysparm_query = self.query
        else:
            raise InvalidUsage(
                "Query must be instance of %s, %s or %s" % (QueryBuilder, str, dict)
            )

        for field in order_by:
            if field[0] == "-":
                sysparm_query += "^ORDERBYDESC%s" % field[1:]
            else:
                sysparm_query += "^ORDERBY%s" % field

        params = {"sysparm_query": sysparm_query}
        params.update(self.request_params)

        if limit is not None:
            params.update(
                {"sysparm_limit": limit, "sysparm_suppress_pagination_header": True}
            )

        if offset is not None:
            params.update({"sysparm_offset": offset})

        if len(fields) > 0:
            params.update({"sysparm_fields": ",".join(fields)})

        return params
