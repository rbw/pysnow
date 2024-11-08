# -*- coding: utf-8 -*-
import unittest

from pysnow.params_builder import ParamsBuilder
from pysnow.query_builder import QueryBuilder
from pysnow.exceptions import InvalidUsage


class TestQuery(unittest.TestCase):
    def test_stringify_dict(self):
        """:meth:`_stringify` should be able to convert a dict to a string of the expected value"""

        query = {"dict_foo": "dict_bar"}
        expected_string = "dict_foo=dict_bar"

        self.assertEqual(ParamsBuilder.stringify_query(query), expected_string)

    def test_stringify_query_builder(self):
        """:meth:`_stringify` should be able to convert a query builder object to a string of the expected value"""

        query = QueryBuilder().field("qb_foo").equals("qb_bar")
        expected_string = "qb_foo=qb_bar"

        self.assertEqual(ParamsBuilder.stringify_query(query), expected_string)

    def test_query_setter_getter(self):
        """:prop:query setter should set _sysparms['sysparm_query'] and be accessible using :prop:query getter"""

        query = "str_foo=str_bar"

        sp = ParamsBuilder()
        sp.query = query

        self.assertEqual(sp.query, query)
        self.assertEqual(sp._sysparms["sysparm_query"], query)

    def test_stringify_invalid_type(self):
        """:meth:`_stringify` should raise an InvalidUsage exception if the query is of invalid type"""

        self.assertRaises(InvalidUsage, ParamsBuilder.stringify_query, False)
        self.assertRaises(InvalidUsage, ParamsBuilder.stringify_query, True)
        self.assertRaises(InvalidUsage, ParamsBuilder.stringify_query, ("foo", "bar"))
        self.assertRaises(InvalidUsage, ParamsBuilder.stringify_query, 1)

    def test_apply_valid_limit(self):
        """:meth:`set_limit` should set `sysparm_limit`"""

        limit = 20
        sp = ParamsBuilder()
        sp.limit = limit

        self.assertEqual(sp._sysparms["sysparm_limit"], limit)
        self.assertEqual(sp.limit, limit)

    def test_apply_valid_offset(self):
        """:meth:`set_offset` should set `sysparm_offset` in :prop:`_sysparms`"""

        offset = 30
        sp = ParamsBuilder()
        sp.offset = offset

        self.assertEqual(sp._sysparms["sysparm_offset"], offset)
        self.assertEqual(sp.offset, offset)

    def test_apply_valid_fields(self):
        """:meth:`set_fields` should set `sysparm_fields` in :prop:`_sysparms` to a comma-separated string"""

        fields = ["field1", "field2"]
        sp = ParamsBuilder()
        sp.fields = fields

        self.assertEqual(sp._sysparms["sysparm_fields"], ",".join(fields))
        self.assertEqual(sp.fields, ",".join(fields))

    def test_apply_invalid_fields(self):
        """:meth:`set_fields` should raise an InvalidUsage exception if fields is of an invalid type"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, setattr, sp, "fields", "foo")
        self.assertRaises(InvalidUsage, setattr, sp, "fields", 0)
        self.assertRaises(InvalidUsage, setattr, sp, "fields", False)
        self.assertRaises(InvalidUsage, setattr, sp, "fields", ("asd", "dsa"))

    def test_apply_invalid_offset(self):
        """:meth:`set_offset` should raise an InvalidUsage exception if offset is of an invalid type"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, setattr, sp, "offset", "foo")
        self.assertRaises(InvalidUsage, setattr, sp, "offset", {"foo": "bar"})
        self.assertRaises(InvalidUsage, setattr, sp, "offset", False)
        self.assertRaises(InvalidUsage, setattr, sp, "offset", ("asd", "dsa"))

    def test_apply_invalid_limit(self):
        """:meth:`set_limit` should raise an InvalidUsage exception if limit is of an invalid type"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, setattr, sp, "limit", "foo")
        self.assertRaises(InvalidUsage, setattr, sp, "limit", {"foo": "bar"})
        self.assertRaises(InvalidUsage, setattr, sp, "limit", False)
        self.assertRaises(InvalidUsage, setattr, sp, "limit", ("asd", "dsa"))

    def test_set_suppress_pagination_header(self):
        """:prop:`suppress_pagination_header` setter should set
        `sysparm_suppress_pagination_header` in :prop:`_sysparms`"""

        sp = ParamsBuilder()

        sp.suppress_pagination_header = True
        self.assertEqual(sp._sysparms["sysparm_suppress_pagination_header"], True)
        self.assertEqual(sp.suppress_pagination_header, True)

        sp.suppress_pagination_header = False
        self.assertEqual(sp._sysparms["sysparm_suppress_pagination_header"], False)
        self.assertEqual(sp.suppress_pagination_header, False)

    def test_set_exclude_reference_link(self):
        """:prop:`exclude_reference_link` setter should set `sysparm_exclude_reference_link` in :prop:`_sysparms`"""

        sp = ParamsBuilder()

        sp.exclude_reference_link = True
        self.assertEqual(sp._sysparms["sysparm_exclude_reference_link"], True)
        self.assertEqual(sp.exclude_reference_link, True)

        sp.exclude_reference_link = False
        self.assertEqual(sp._sysparms["sysparm_exclude_reference_link"], False)
        self.assertEqual(sp.exclude_reference_link, False)

    def test_set_display_value(self):
        """:prop:`display_value` setter should set `sysparm_display_value` in :prop:`_sysparms`"""

        sp = ParamsBuilder()

        sp.display_value = True
        self.assertEqual(sp._sysparms["sysparm_display_value"], True)
        self.assertEqual(sp.display_value, True)

        sp.display_value = False
        self.assertEqual(sp._sysparms["sysparm_display_value"], False)
        self.assertEqual(sp.display_value, False)

        sp.display_value = "all"
        self.assertEqual(sp._sysparms["sysparm_display_value"], "all")
        self.assertEqual(sp.display_value, "all")

    def test_set_exclude_reference_link_invalid(self):
        """:prop:`exclude_reference_link` setter should raise an exception if type is not bool"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, setattr, sp, "exclude_reference_link", "foo")
        self.assertRaises(InvalidUsage, setattr, sp, "exclude_reference_link", None)
        self.assertRaises(InvalidUsage, setattr, sp, "exclude_reference_link", 1)
        self.assertRaises(
            InvalidUsage, setattr, sp, "exclude_reference_link", {"foo": "bar"}
        )

    def test_set_display_value_invalid(self):
        """:prop:`display_value` setter should raise an exception if type is not bool or `all`"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, setattr, sp, "display_value", "foo")
        self.assertRaises(InvalidUsage, setattr, sp, "display_value", None)
        self.assertRaises(InvalidUsage, setattr, sp, "display_value", 1)
        self.assertRaises(InvalidUsage, setattr, sp, "display_value", {"foo": "bar"})

    def test_set_suppress_pagination_header_invalid(self):
        """:meth:`suppress_pagination_header` setter should raise an exception if type is not bool"""

        sp = ParamsBuilder()

        self.assertRaises(
            InvalidUsage, setattr, sp, "suppress_pagination_header", "foo"
        )
        self.assertRaises(InvalidUsage, setattr, sp, "suppress_pagination_header", 1)
        self.assertRaises(
            InvalidUsage, setattr, sp, "suppress_pagination_header", {"foo": "bar"}
        )

    def test_add_custom_parameter(self):
        """The custom parameter dicts provided to :meth:`add_custom` should be added to :prop:`_custom_params`"""

        custom_param = {"foo": "bar"}

        sp = ParamsBuilder()
        sp.add_custom(custom_param)

        self.assertEqual(sp.custom_params, custom_param)
        self.assertEqual(sp._custom_params, custom_param)
        self.assertEqual(sp.as_dict()["foo"], custom_param["foo"])

    def test_add_invalid_custom_parameter(self):
        """:meth:`add_custom` should only accept dicts"""

        sp = ParamsBuilder()

        self.assertRaises(InvalidUsage, sp.add_custom, ("foo", "bar"))
        self.assertRaises(InvalidUsage, sp.add_custom, "foo")
        self.assertRaises(InvalidUsage, sp.add_custom, True)
        self.assertRaises(InvalidUsage, sp.add_custom, 0)
