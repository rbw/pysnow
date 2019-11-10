# -*- coding: utf-8 -*-

from .client import Client
from .oauth_client import OAuthClient
from .query_builder import QueryBuilder
from .resource import Resource
from .params_builder import ParamsBuilder

# Set default logging handler to avoid "No handler found" warnings.
import logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: no cover

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
