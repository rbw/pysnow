# -*- coding: utf-8 -*-


class Report(object):
    def __init__(self, resource, request_params, generator_size, session):
        self.x_total_count = -1
        self.consumed_records = 0
        self.responses = []
        self.generator_size = generator_size
        self.request_params = request_params
        self.resource = resource
        self.session = session

    def set_x_total_count(self, count):
        self.x_total_count = int(count)

    def add_consumed_count(self, records):
        self.consumed_records = self.consumed_records + int(records)

    def add_response(self, response):
        self.responses.append(response)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __repr__(self):
        return "%s %s" % (self.__class__, self.__dict__)
