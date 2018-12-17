# -*- coding: utf-8 -*-

# Public API
from .client import Client
from .oauth_client import OAuthClient
from .query_builder import QueryBuilder
from .resource import Resource
from .params_builder import ParamsBuilder

__author__ = "Robert Wikman <rbw@vault13.org>"
__version__ = "0.7.6"

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
