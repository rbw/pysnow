# -*- coding: utf-8 -*-

######################
# Generic exceptions #
######################
class InvalidUsage(Exception):
    pass


#######################
# Response exceptions #
#######################
class ResponseError(Exception):
    message = '<empty>'
    detail = '<empty>'

    def __init__(self, error):
        if 'message' in error:
            self.message = error['message'] or self.message
        if 'detail' in error:
            self.detail = error['detail'] or self.detail

    def __str__(self):
        return 'Error in response. Message: %s, Details: %s' % (self.message, self.detail)


class MissingResult(Exception):
    pass


class UnexpectedResponseFormat(Exception):
    pass


class ReportUnavailable(Exception):
    pass


class NoResults(Exception):
    pass


class MultipleResults(Exception):
    pass


##########################
# OAuthClient exceptions #
##########################
class MissingToken(Exception):
    pass


class TokenCreateError(Exception):
    def __init__(self, error, description, status_code):
        self.error = error
        self.description = description
        self.snow_status_code = status_code


############################
# Query builder exceptions #
############################
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
