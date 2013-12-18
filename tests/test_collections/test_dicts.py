"""
Tests for the .collections.dicts module.
"""
from taipan.testing import TestCase

import taipan.collections.dicts as __unit__


class _Filter(TestCase):
    TRUTHY_DICT = {'foo': 1, 'bar': 2, 'baz': 3}
    FALSY_DICT = {'foo': 0, '': 1, False: 2, 'bar': 3, (): 4, 'baz': ()}


class FilterItems(_Filter):
    COALESCED_FALSY_DICT = {'bar': 3}

    FILTER = staticmethod(
        lambda k, v: (k and k[0] == 'b') or (v and v % 2 == 1))
    FILTERED_TRUTHY_DICT = {'foo': 1, 'bar': 2, 'baz': 3}
    FILTERED_FALSY_DICT = {'': 1, 'bar': 3, 'baz': ()}

    def test_function__none(self):
        self.assertEquals(self.TRUTHY_DICT,
                          __unit__.filteritems(None, self.TRUTHY_DICT))
        self.assertEquals(self.COALESCED_FALSY_DICT,
                          __unit__.filteritems(None, self.FALSY_DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.filteritems(object(), self.TRUTHY_DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.filteritems(FilterItems.FILTER, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.filteritems(FilterItems.FILTER, None)

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.filteritems(None, {}))
        self.assertEquals({}, __unit__.filteritems(self.FILTER, {}))

    def test_filter(self):
        self.assertEquals(
            self.FILTERED_TRUTHY_DICT,
            __unit__.filteritems(FilterItems.FILTER, self.TRUTHY_DICT))
        self.assertEquals(
            self.FILTERED_FALSY_DICT,
            __unit__.filteritems(FilterItems.FILTER, self.FALSY_DICT))


class FilterKeys(_Filter):
    COALESCED_FALSY_DICT = {'foo': 0, 'bar': 3, 'baz': ()}

    FILTER = staticmethod(lambda k: k and k[0] == 'b')
    FILTERED_TRUTHY_DICT = {'bar': 2, 'baz': 3}
    FILTERED_FALSY_DICT = {'bar': 3, 'baz': ()}

    def test_function__none(self):
        self.assertEquals(self.TRUTHY_DICT,
                          __unit__.filterkeys(None, self.TRUTHY_DICT))
        self.assertEquals(self.COALESCED_FALSY_DICT,
                          __unit__.filterkeys(None, self.FALSY_DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.filterkeys(object(), self.TRUTHY_DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.filterkeys(FilterKeys.FILTER, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.filterkeys(FilterKeys.FILTER, None)

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.filterkeys(None, {}))
        self.assertEquals({}, __unit__.filterkeys(self.FILTER, {}))

    def test_filter(self):
        self.assertEquals(
            self.FILTERED_TRUTHY_DICT,
            __unit__.filterkeys(FilterKeys.FILTER, self.TRUTHY_DICT))
        self.assertEquals(
            self.FILTERED_FALSY_DICT,
            __unit__.filterkeys(FilterKeys.FILTER, self.FALSY_DICT))


class FilterValues(_Filter):
    COALESCED_FALSY_DICT = {'': 1, False: 2, 'bar': 3, (): 4}

    FILTER = staticmethod(lambda v: v and v % 2 == 1)
    FILTERED_TRUTHY_DICT = {'foo': 1, 'baz': 3}
    FILTERED_FALSY_DICT = {'': 1, 'bar': 3}

    def test_function__none(self):
        self.assertEquals(self.TRUTHY_DICT,
                          __unit__.filtervalues(None, self.TRUTHY_DICT))
        self.assertEquals(self.COALESCED_FALSY_DICT,
                          __unit__.filtervalues(None, self.FALSY_DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.filtervalues(object(), self.TRUTHY_DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.filtervalues(FilterValues.FILTER, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.filtervalues(FilterValues.FILTER, None)

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.filtervalues(None, {}))
        self.assertEquals({}, __unit__.filtervalues(self.FILTER, {}))

    def test_filter(self):
        self.assertEquals(
            self.FILTERED_TRUTHY_DICT,
            __unit__.filtervalues(FilterValues.FILTER, self.TRUTHY_DICT))
        self.assertEquals(
            self.FILTERED_FALSY_DICT,
            __unit__.filtervalues(FilterValues.FILTER, self.FALSY_DICT))


class Get(TestCase):
    pass


class Merge(TestCase):
    pass


class Reverse(TestCase):
    pass


class Select(TestCase):
    pass
