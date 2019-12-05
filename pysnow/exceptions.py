# -*- coding: utf-8 -*-


class PysnowException(Exception):
    pass


class InvalidUsage(PysnowException):
    pass


class UnexpectedResponseFormat(PysnowException):
    pass


class ResponseError(PysnowException):
    message = "<empty>"
    detail = "<empty>"

    def __init__(self, error):
        if "message" in error:
            self.message = error["message"] or self.message
        if "detail" in error:
            self.detail = error["detail"] or self.detail

    def __str__(self):
        return "Error in response. Message: %s, Details: %s" % (
            self.message,
            self.detail,
        )


class MissingResult(PysnowException):
    pass


class NoResults(PysnowException):
    pass


class EmptyContent(PysnowException):
    pass


class MultipleResults(PysnowException):
    pass


class MissingToken(PysnowException):
    pass


class TokenCreateError(PysnowException):
    def __init__(self, error, description, status_code):
        self.error = error
        self.description = description
        self.snow_status_code = status_code


class QueryTypeError(PysnowException):
    pass


class QueryMissingField(PysnowException):
    pass


class QueryEmpty(PysnowException):
    pass


class QueryExpressionError(PysnowException):
    pass


class QueryMultipleExpressions(PysnowException):
    pass
