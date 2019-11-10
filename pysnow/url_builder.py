# -*- coding: utf-8 -*-

import re
import six
from .exceptions import InvalidUsage


class URLBuilder(object):
    def __init__(self, base_url, base_path, api_path):
        self.base_url = base_url
        self.base_path = base_path
        self.api_path = api_path
        self.full_path = base_path + api_path

        self._resource_url = "%(base_url)s%(full_path)s" % (
            {"base_url": base_url, "full_path": self.full_path}
        )

    @staticmethod
    def validate_path(path):
        """Validates the provided path

        :param path: path to validate (string)
        :raise:
            :InvalidUsage: If validation fails.
        """

        if not isinstance(path, six.string_types) or not re.match(
            "^/(?:[._a-zA-Z0-9-]/?)+[^/]$", path
        ):
            raise InvalidUsage(
                "Path validation failed - Expected: '/<component>[/component], got: %s"
                % path
            )

        return True

    @staticmethod
    def get_base_url(use_ssl, instance=None, host=None):
        """Formats the base URL either `host` or `instance`

        :return: Base URL string
        """

        if instance is not None:
            host = ("%s.service-now.com" % instance).rstrip("/")

        if use_ssl is True:
            return "https://%s" % host

        return "http://%s" % host

    def get_appended_custom(self, path_component):
        """Validates the provided path_component, then returns it appended to :prop:`_resource_url`

        :param path_component: Path component string
        :return: Full URL to the custom resource
        """
        self.validate_path(path_component)

        return self._resource_url + path_component

    def get_url(self):
        """Returns :prop:`_resource_url`

        :return: :prop:`_resource_url`
        """
        return self._resource_url
