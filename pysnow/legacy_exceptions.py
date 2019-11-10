# -*- coding: utf-8 -*-


class InvalidUsage(Exception):
    pass


class QueryTypeError(TypeError):
    pass


class QueryMissingField(Exception):
    pass


class QueryEmpty(Exception):
    pass


class QueryExpressionError(Exception):
    pass


class QueryMultipleExpressions(Exception):
    pass


class MissingResult(Exception):
    pass


class MissingToken(Exception):
    pass


class UnexpectedResponseFormat(Exception):
    pass


class ReportUnavailable(Exception):
    pass


class UnexpectedResponse(Exception):
    """Provides detailed information about a server error response

    :param code_expected: Expected HTTP status code
    :param code_actual: Actual HTTP status code
    :param http_method: HTTP method used
    :param error_summary: Summary of what went wrong
    :param error_details: Details about the error
    """

    def __init__(
        self, code_expected, code_actual, http_method, error_summary, error_details
    ):
        if code_expected == code_actual:
            message = "Unexpected response on HTTP %s from server: %s" % (
                http_method,
                error_summary,
            )
        else:
            message = "Unexpected HTTP %s response code. Expected %d, got %d" % (
                http_method,
                code_expected,
                code_actual,
            )

        super(UnexpectedResponse, self).__init__(message)
        self.status_code = code_actual
        self.error_summary = error_summary
        self.error_details = error_details


class NoResults(Exception):
    pass


class MultipleResults(Exception):
    pass


class NoRequestExecuted(Exception):
    pass
