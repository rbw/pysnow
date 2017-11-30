# -*- coding: utf-8 -*-
import unittest

from pysnow.report import Report


class TestReport(unittest.TestCase):
    def setUp(self):
        self.mock_report = {
            'session': 'mock_session',
            'resource': 'mock_resource',
            'generator_size': 10
        }

    def test_create_report(self):
        """Creating a new :class:`Report` should be a dict-like object with session, resource and generator_size set"""

        r = Report(**self.mock_report)

        self.assertEquals(r['generator_size'], self.mock_report['generator_size'])
        self.assertEquals(r['session'], self.mock_report['session'])
        self.assertEquals(r['resource'], self.mock_report['resource'])

    def test_set_valid_x_total_size(self):
        """:meth:`set_x_total_count` should set :prop:`x_total_count`"""

        r = Report(**self.mock_report)

        total_count = 20
        r.set_x_total_count(total_count)

        self.assertEquals(r.x_total_count, total_count)

    def test_set_invalid_x_total_size(self):
        """:meth:`set_x_total_count` should raise TypeError if the passed count is of an invalid type"""

        r = Report(**self.mock_report)

        self.assertRaises(TypeError, r.set_x_total_count, 'foo')
        self.assertRaises(TypeError, r.set_x_total_count, {'foo': 'bar'})
        self.assertRaises(TypeError, r.set_x_total_count, True)

    def test_set_valid_consumed_count(self):
        """The value passed to :meth:`add_consumed_count` should be added to :prop:`consumed_records`"""

        r = Report(**self.mock_report)

        previous_count = 30
        count_to_add = 10
        r.consumed_records = previous_count
        r.add_consumed_count(count_to_add)

        self.assertEquals(r.consumed_records, previous_count + count_to_add)

    def test_set_invalid_consumed_count(self):
        """:meth:`add_consumed_count` should raise TypeError if the passed count is of an invalid type"""

        r = Report(**self.mock_report)

        self.assertRaises(TypeError, r.add_consumed_count, 'foo')
        self.assertRaises(TypeError, r.add_consumed_count, {'foo': 'bar'})
        self.assertRaises(TypeError, r.add_consumed_count, True)

    def test_add_response(self):
        """Responses added with :meth:`add_response` should be appended to :prop:`responses`"""

        r = Report(**self.mock_report)

        r.responses = ['response1']
        added_response0 = 'response2'
        added_response1 = 'response3'

        expected_responses = r.responses
        expected_responses.extend([added_response0, added_response1])

        r.add_response(added_response0)
        r.add_response(added_response1)

        self.assertEquals(r.responses, expected_responses)

    def test_get_report(self):
        """The accessing repr of a :class:`Report` object should print out a string"""

        report_type = type(repr(Report(**self.mock_report)))

        self.assertEquals(report_type, str)

