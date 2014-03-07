"""
Tests for the .collections.dicts module.
"""
from taipan.collections import is_mapping
from taipan.testing import TestCase

import taipan.collections.dicts as __unit__


ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


class AbsentDict(TestCase):
    EXISTING_KEY = 'foo'
    EXISTING_VALUE = 0
    NONEXISTING_KEY = 'baz'
    DICT_WITH_ALL_PRESENT = {EXISTING_KEY: EXISTING_VALUE, 'bar': 2}

    ABSENT_KEY = 'bar'
    DICT_WITH_ONE_ABSENT = {EXISTING_KEY: EXISTING_VALUE,
                            ABSENT_KEY: __unit__.ABSENT}
    DICT_WITH_ALL_ABSENT = {'foo': __unit__.ABSENT, 'bar': __unit__.ABSENT}

    def test_ctor__no_args(self):
        dict_ = __unit__.AbsentDict()
        self._assertIsMapping(dict_)
        self.assertEmpty(dict_)

    def test_ctor__none(self):
        with self.assertRaises(TypeError):
            __unit__.AbsentDict(None)

    def test_ctor__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.AbsentDict(object())

    def test_ctor__dict__empty(self):
        self.assertEquals({}, __unit__.AbsentDict({}))

    def test_ctor__dict__all_present(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_PRESENT)
        self.assertEquals(self.DICT_WITH_ALL_PRESENT, dict_)

    def test_ctor__dict__one_absent(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ONE_ABSENT)
        self.assertEquals(len(self.DICT_WITH_ONE_ABSENT) - 1, len(dict_))
        self.assertNotIn(self.ABSENT_KEY, dict_)

    def test_ctor__dict__all_absent(self):
        self.assertEquals({}, __unit__.AbsentDict(self.DICT_WITH_ALL_ABSENT))

    def test_ctor__pairlist__empty(self):
        self.assertEquals({}, __unit__.AbsentDict([]))

    def test_ctor__pairlist__all_present(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_PRESENT.items())
        self.assertEquals(self.DICT_WITH_ALL_PRESENT, dict_)

    def test_ctor__pairlist__one_absent(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ONE_ABSENT.items())
        self.assertEquals(len(self.DICT_WITH_ONE_ABSENT) - 1, len(dict_))
        self.assertNotIn(self.ABSENT_KEY, dict_)

    def test_ctor__dict__all_absent(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_ABSENT.items())
        self.assertEquals({}, dict_)

    def test_setitem__existing_present(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_PRESENT)
        dict_[self.EXISTING_KEY] = self.EXISTING_VALUE  # should be no-op
        self.assertEquals(self.DICT_WITH_ALL_PRESENT, dict_)

    def test_setitem__nonexisting_present(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_PRESENT)
        dict_[self.NONEXISTING_KEY] = 42  # should add the key normally
        self.assertIn(self.NONEXISTING_KEY, dict_)

    def test_setitem__present_to_absent(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ALL_PRESENT)
        dict_[self.EXISTING_KEY] = __unit__.ABSENT  # should delete the key
        self.assertNotIn(self.EXISTING_KEY, dict_)

    def test_setitem__absent_to_present(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ONE_ABSENT)
        dict_[self.ABSENT_KEY] = 42  # should add the key
        self.assertIn(self.ABSENT_KEY, dict_)

    def test_setitem__still_absent(self):
        dict_ = __unit__.AbsentDict(self.DICT_WITH_ONE_ABSENT)
        dict_[self.ABSENT_KEY] = __unit__.ABSENT  # should be no-op
        self.assertNotIn(self.ABSENT_KEY, dict_)

    # Assertions

    def _assertIsMapping(self, obj, msg=None):
        if not is_mapping(obj):
            self.fail(msg or "%r is not a mapping" % (obj,))


# Access functions

class Get(TestCase):
    DICT = dict(zip(ALPHABET, range(1, len(ALPHABET) + 1)))

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


class Select(TestCase):
    DICT = dict(zip(('foo', 'bar', 'baz', 'thud', 'qux'), range(5)))

    STRICT_KEYS = ('foo', 'bar')
    EXTRANEOUS_KEY = 'blah'
    NONSTRICT_KEYS = ('bar', 'qux', EXTRANEOUS_KEY)

    SELECTED_BY_STRICT_KEYS = {'foo': 0, 'bar': 1}
    SELECTED_BY_NONSTRICT_KEYS = {'bar': 1, 'qux': 4}

    def test_keys__none(self):
        with self.assertRaises(TypeError):
            __unit__.select(None, self.DICT)

    def test_keys__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.select(object(), self.DICT)

    def test_keys__empty(self):
        self.assertEquals({}, __unit__.select((), self.DICT))

    def test_from__none(self):
        with self.assertRaises(TypeError):
            __unit__.select(self.STRICT_KEYS, None)

    def test_from__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.select(self.STRICT_KEYS, object())

    def test_from__empty(self):
        with self.assertRaises(KeyError):
            __unit__.select(self.STRICT_KEYS, {}, strict=True)
        self.assertEquals(
            {}, __unit__.select(self.NONSTRICT_KEYS, {}, strict=False))

    def test_strict__true(self):
        self.assertEquals(
            self.SELECTED_BY_STRICT_KEYS,
            __unit__.select(self.STRICT_KEYS, self.DICT, strict=True))

        with self.assertRaises(KeyError) as r:
            __unit__.select(self.NONSTRICT_KEYS, self.DICT, strict=True)
        self.assertIn(repr(self.EXTRANEOUS_KEY), str(r.exception))

    def test_strict__false(self):
        self.assertEquals(
            self.SELECTED_BY_STRICT_KEYS,
            __unit__.select(self.STRICT_KEYS, self.DICT, strict=False))
        self.assertEquals(
            self.SELECTED_BY_NONSTRICT_KEYS,
            __unit__.select(self.NONSTRICT_KEYS, self.DICT, strict=False))


# Filter functions

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


# Mutation functions

class Merge(TestCase):
    KEYS = ('foo', 'bar', 'baz', 'qux', 'thud')

    DICT = dict(zip(KEYS[:3], range(3)))
    OTHER_DICT = dict(zip(KEYS[3:], range(3, len(KEYS))))
    MANY_DICTS = [{k: v} for k, v in zip(KEYS, range(len(KEYS)))]

    MERGED = dict(zip(KEYS, range(5)))

    def test_no_args(self):
        self.assertEquals({}, __unit__.merge())

    def test_single_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.merge(None)

    def test_single_arg__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.merge(object())

    def test_single_arg__dict(self):
        result =  __unit__.merge(self.DICT)
        self.assertEquals(self.DICT, result)
        self.assertIsNot(self.DICT, result)

    def test_two_args(self):
        self.assertEquals(
            self.MERGED, __unit__.merge(self.DICT, self.OTHER_DICT))

    def test_many_args(self):
        self.assertEquals(
            self.MERGED, __unit__.merge(*self.MANY_DICTS))


class Reverse(TestCase):
    REVERSIBLE_DICT = dict(zip(ALPHABET, range(1, len(ALPHABET) + 1)))
    IRREVERSIBLE_DICT = dict(zip(range(1, 2 * len(ALPHABET) + 1),
                                 ALPHABET * 2))

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.reverse(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.reverse(object())

    def test_empty(self):
        self.assertEquals({}, __unit__.reverse({}))

    def test_reversible(self):
        reversed_dict = __unit__.reverse(self.REVERSIBLE_DICT)
        self.assertItemsEqual(
            self.REVERSIBLE_DICT.values(), reversed_dict.keys())
        self.assertItemsEqual(
            self.REVERSIBLE_DICT.keys(), reversed_dict.values())

    def test_irreversible(self):
        # a bit of misnomer, but it means dictionary has duplicate values
        reversed_dict = __unit__.reverse(self.IRREVERSIBLE_DICT)
        self.assertGreater(
            set(self.IRREVERSIBLE_DICT.keys()), set(reversed_dict.values()))
