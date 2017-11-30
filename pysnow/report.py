# -*- coding: utf-8 -*-


class Report(object):
    def __init__(self, resource, generator_size, session):
        """Constructs a report, keeping track of resources, requests and responses

        :param resource: :class:`pysnow.Resource` object
        :param generator_size: Generator size (integer)
        :param session: :class:`requests.Session` object
        """
        self.x_total_count = -1
        self.consumed_records = 0
        self.responses = []
        self.generator_size = generator_size
        self.request_params = None
        self.resource = resource
        self.session = session

    def set_x_total_count(self, count):
        """Sets the x-total-count (from response header)

        :param count: total count
        :raise:
            :TypeError: If passed count is of invalid type
        """

        if not isinstance(count, int) or isinstance(count, bool):
            raise TypeError('x-total-count must be of type integer')

        self.x_total_count = int(count)

    def add_consumed_count(self, consumed_count):
        """Adds the number of records present in a response to the :prop:`consumed_count`

        :param consumed_count: response content record count
        :raise:
            :TypeError: If passed count is of invalid type
        """

        if not isinstance(consumed_count, int) or isinstance(consumed_count, bool):
            raise TypeError('consumed count must be of type integer')

        self.consumed_records = self.consumed_records + int(consumed_count)

    def add_response(self, response):
        """Adds a :class:`requests.Response` object to the :prop:`responses` list

        :param response: :class:`requests.Response` object
        """
        self.responses.append(response)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __repr__(self):
        return "%s %s" % (self.__class__, self.__dict__)
