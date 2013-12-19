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
    DICT = dict(zip(map(chr, range(ord('a'), ord('z') + 1)),  # a..z
                    range(1, 26 + 1)))

    ABSENT_KEYS = ('not_present', 'also_absent')
    PRESENT_KEYS = tuple('hax')
    KEYS = ABSENT_KEYS + PRESENT_KEYS  # assumed typical situation

    DEFAULT = 0

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.get(None, self.KEYS, self.DEFAULT)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.get(object(), self.KEYS, self.DEFAULT)

    def test_dict__empty(self):
        self.assertEquals(self.DEFAULT,
                          __unit__.get({}, self.KEYS, self.DEFAULT))

    def test_keys__none(self):
        with self.assertRaises(TypeError):
            __unit__.get(self.DICT, None, self.DEFAULT)

    def test_keys__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.get(self.DICT, object(), self.DEFAULT)

    def test_keys__empty(self):
        self.assertEquals(self.DEFAULT,
                          __unit__.get(self.DICT, (), self.DEFAULT))

    def test_keys__typical(self):
        self.assertEquals(
            self.DICT[self.PRESENT_KEYS[0]],
            __unit__.get(self.DICT, self.KEYS, self.DEFAULT))

    def test_default__omitted(self):
        self.assertIsNone(__unit__.get(self.DICT, self.ABSENT_KEYS))

    def test_default__provided(self):
        self.assertEquals(
            self.DEFAULT,
            __unit__.get(self.DICT, self.ABSENT_KEYS, self.DEFAULT))


class Merge(TestCase):
    pass


class Reverse(TestCase):
    pass


class Select(TestCase):
    pass
