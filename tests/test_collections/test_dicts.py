"""
Tests for the .collections.dicts module.
"""
from taipan.collections import is_mapping, is_sequence
from taipan.functional.combinators import merge
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

    def test_ctor__pairlist__all_absent(self):
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


# Compatibility shims

class _Shim(TestCase):
    KEYS = ['foo', 'bar']
    VALUES = list(range(len(KEYS)))
    ITEMS = list(zip(KEYS, VALUES))
    DICT = dict(ITEMS)

    def _assertSequence(self, obj):
        self.assertTrue(is_sequence(obj), msg="%r is not a sequence" % (obj,))

    def _assertNotSequence(self, obj):
        self.assertFalse(is_sequence(obj), msg="%r is a sequence" % (obj,))

    def _assertEmptySequence(self, obj):
        self._assertSequence(obj)
        self.assertEmpty(obj)

    def _assertEmptyNonSequence(self, obj):
        self._assertNotSequence(obj)
        self.assertEmpty(obj)

    def _assertSequenceItems(self, items, obj):
        self._assertSequence(obj)
        self.assertItemsEqual(items, obj)

    def _assertNonSequenceItems(self, items, obj):
        self._assertNotSequence(obj)
        self.assertItemsEqual(items, obj)


class IterItems(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.iteritems(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.iteritems(object())

    def test_dict__empty(self):
        self._assertEmptyNonSequence(__unit__.iteritems({}))

    def test_dict__normal(self):
        iteritems = __unit__.iteritems(self.DICT)
        self._assertNonSequenceItems(self.ITEMS, iteritems)


class IterKeys(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.iterkeys(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.iterkeys(object())

    def test_dict__empty(self):
        self._assertEmptyNonSequence(__unit__.iterkeys({}))

    def test_dict__normal(self):
        iterkeys = __unit__.iterkeys(self.DICT)
        self._assertNonSequenceItems(self.KEYS, iterkeys)


class IterValues(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.itervalues(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.itervalues(object())

    def test_dict__empty(self):
        self._assertEmptyNonSequence(__unit__.itervalues({}))

    def test_dict__normal(self):
        itervalues = __unit__.itervalues(self.DICT)
        self._assertNonSequenceItems(self.VALUES, itervalues)


class Items(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.items(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.items(object())

    def test_dict__empty(self):
        self._assertEmptySequence(__unit__.items({}))

    def test_dict__normal(self):
        items = __unit__.items(self.DICT)
        self._assertSequenceItems(self.ITEMS, items)


class Keys(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.keys(None)

    def test_some_objects(self):
        with self.assertRaises(TypeError):
            __unit__.keys(object())

    def test_dict__empty(self):
        self._assertEmptySequence(__unit__.keys({}))

    def test_dict__normal(self):
        keys = __unit__.keys(self.DICT)
        self._assertSequenceItems(self.KEYS, keys)


class Values(_Shim):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.values(None)

    def test_some_objects(self):
        with self.assertRaises(TypeError):
            __unit__.values(object())

    def test_dict__empty(self):
        self._assertEmptySequence(__unit__.values({}))

    def test_dict__normal(self):
        values = __unit__.values(self.DICT)
        self._assertSequenceItems(self.VALUES, values)


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


class PeekItem(TestCase):
    DICT = dict(zip(ALPHABET, range(1, len(ALPHABET) + 1)))

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.peekitem(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.peekitem(object())

    def test_dict__empty(self):
        with self.assertRaises(KeyError):
            __unit__.peekitem({})

    def test_dict__normal(self):
        key, value = __unit__.peekitem(self.DICT)
        self.assertIn(key, self.DICT)
        self.assertEquals(value, self.DICT[key])


class _Projection(TestCase):
    DICT = dict(zip(('foo', 'bar', 'baz', 'thud', 'qux'), range(5)))

    STRICT_KEYS = ('foo', 'bar')
    EXTRANEOUS_KEY = 'blah'
    NONSTRICT_KEYS = ('bar', 'qux', EXTRANEOUS_KEY)


class Select(_Projection):
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


class Omit(_Projection):
    WITH_STRICT_KEYS_OMITTED = {'baz': 2, 'thud': 3, 'qux': 4}
    WITH_NONSTRICT_KEYS_OMITTED = {'foo': 0, 'baz': 2, 'thud': 3}

    def test_keys__none(self):
        with self.assertRaises(TypeError):
            __unit__.omit(None, self.DICT)

    def test_keys__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.omit(object(), self.DICT)

    def test_keys__empty(self):
        self.assertEquals(self.DICT, __unit__.omit((), self.DICT))

    def test_from__none(self):
        with self.assertRaises(TypeError):
            __unit__.omit(self.STRICT_KEYS, None)

    def test_from__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.omit(self.STRICT_KEYS, object())

    def test_from__empty(self):
        with self.assertRaises(KeyError):
            __unit__.omit(self.STRICT_KEYS, {}, strict=True)
        self.assertEquals(
            {}, __unit__.omit(self.NONSTRICT_KEYS, {}, strict=False))

    def test_strict__true(self):
        self.assertEquals(
            self.WITH_STRICT_KEYS_OMITTED,
            __unit__.omit(self.STRICT_KEYS, self.DICT, strict=True))

        with self.assertRaises(KeyError) as r:
            __unit__.omit(self.NONSTRICT_KEYS, self.DICT, strict=True)
        self.assertIn(repr(self.EXTRANEOUS_KEY), str(r.exception))

    def test_strict__false(self):
        self.assertEquals(
            self.WITH_STRICT_KEYS_OMITTED,
            __unit__.omit(self.STRICT_KEYS, self.DICT, strict=False))
        self.assertEquals(
            self.WITH_NONSTRICT_KEYS_OMITTED,
            __unit__.omit(self.NONSTRICT_KEYS, self.DICT, strict=False))



# Filter functions

class _Filter(TestCase):
    TRUTHY_DICT = {'foo': 1, 'bar': 2, 'baz': 3}
    FALSY_DICT = {'foo': 0, '': 1, False: 2, 'bar': 3, (): 4, 'baz': ()}


class _FilterItems(_Filter):
    COALESCED_FALSY_DICT = {'bar': 3}

    KEY_FILTER = staticmethod(lambda k: k and k[0] == 'b')
    VALUE_FILTER = staticmethod(lambda v: v and v %2 == 1)

    FILTERED_TRUTHY_DICT = {'foo': 1, 'bar': 2, 'baz': 3}
    FILTERED_FALSY_DICT = {'': 1, 'bar': 3, 'baz': ()}


class FilterItems(_FilterItems):
    FILTER = staticmethod(lambda item: _FilterItems.KEY_FILTER(item[0]) or
                                       _FilterItems.VALUE_FILTER(item[1]))

    def test_function__none(self):
        self.assertEquals(self.TRUTHY_DICT,
                          __unit__.filteritems(None, self.TRUTHY_DICT))
        self.assertEquals(self.COALESCED_FALSY_DICT,
                          __unit__.filteritems(None, self.FALSY_DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.starfilteritems(object(), self.TRUTHY_DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.filteritems(FilterItems.FILTER, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.filteritems(FilterItems.FILTER, object())

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


class StarFilterItems(_FilterItems):
    FILTER = staticmethod(lambda k, v: _FilterItems.KEY_FILTER(k) or
                                       _FilterItems.VALUE_FILTER(v))

    def test_function__none(self):
        self.assertEquals(self.TRUTHY_DICT,
                          __unit__.starfilteritems(None, self.TRUTHY_DICT))
        self.assertEquals(self.COALESCED_FALSY_DICT,
                          __unit__.starfilteritems(None, self.FALSY_DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.starfilteritems(object(), self.TRUTHY_DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.starfilteritems(StarFilterItems.FILTER, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.starfilteritems(StarFilterItems.FILTER, object())

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.starfilteritems(None, {}))
        self.assertEquals({}, __unit__.starfilteritems(self.FILTER, {}))

    def test_filter(self):
        self.assertEquals(
            self.FILTERED_TRUTHY_DICT,
            __unit__.starfilteritems(StarFilterItems.FILTER, self.TRUTHY_DICT))
        self.assertEquals(
            self.FILTERED_FALSY_DICT,
            __unit__.starfilteritems(StarFilterItems.FILTER, self.FALSY_DICT))


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
            __unit__.filterkeys(FilterKeys.FILTER, object())

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
            __unit__.filtervalues(FilterValues.FILTER, object())

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


# Mapping functions

class _Map(TestCase):
    DICT = dict(enumerate(ALPHABET, 1))


class _MapItems(_Map):
    KEY_FUNCTION = staticmethod(lambda k: -k)
    VALUE_FUNCTION = staticmethod(lambda v: v.upper())

    #: Negative numbers to upper-case alphabet letters.
    MAPPED_DICT = dict(zip(range(-1, -(len(ALPHABET) + 1), -1),
                           ALPHABET.upper()))


class MapItems(_MapItems):
    FUNCTION = staticmethod(merge(
        (_MapItems.KEY_FUNCTION, _MapItems.VALUE_FUNCTION)
    ))

    def test_function__none(self):
        self.assertEquals(self.DICT, __unit__.mapitems(None, self.DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.mapitems(object(), self.DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.mapitems(MapItems.FUNCTION, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.mapitems(MapItems.FUNCTION, object())

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.mapitems(None, {}))
        self.assertEquals({}, __unit__.mapitems(MapItems.FUNCTION, {}))

    def test_map(self):
        self.assertEquals(self.MAPPED_DICT,
                          __unit__.mapitems(MapItems.FUNCTION, self.DICT))


class StarMapItems(_MapItems):
    FUNCTION = staticmethod(merge(
        _MapItems.KEY_FUNCTION, _MapItems.VALUE_FUNCTION
    ))

    def test_function__none(self):
        self.assertEquals(self.DICT, __unit__.starmapitems(None, self.DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.starmapitems(object(), self.DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.starmapitems(StarMapItems.FUNCTION, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.starmapitems(StarMapItems.FUNCTION, object())

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.starmapitems(None, {}))
        self.assertEquals({}, __unit__.starmapitems(StarMapItems.FUNCTION, {}))

    def test_map(self):
        self.assertEquals(
            self.MAPPED_DICT,
            __unit__.starmapitems(StarMapItems.FUNCTION, self.DICT))


class MapKeys(_Map):
    FUNCTION = staticmethod(lambda k: -k)

    #: Negative numbers to alphabet letters.
    MAPPED_DICT = dict(zip(range(-1, -(len(ALPHABET) + 1), -1), ALPHABET))

    def test_function__none(self):
        self.assertEquals(self.DICT, __unit__.mapkeys(None, self.DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.mapkeys(object(), self.DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.mapkeys(MapKeys.FUNCTION, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.mapkeys(MapKeys.FUNCTION, object())

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.mapkeys(None, {}))
        self.assertEquals({}, __unit__.mapkeys(MapKeys.FUNCTION, {}))

    def test_map(self):
        self.assertEquals(self.MAPPED_DICT,
                          __unit__.mapkeys(MapKeys.FUNCTION, self.DICT))


class MapValues(_Map):
    FUNCTION = staticmethod(lambda v: v.upper())

    #: Numbers to upper-case alphabet letters.
    MAPPED_DICT = dict(enumerate(ALPHABET.upper(), 1))

    def test_function__none(self):
        self.assertEquals(self.DICT, __unit__.mapvalues(None, self.DICT))

    def test_function__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.mapvalues(object(), self.DICT)

    def test_dict__none(self):
        with self.assertRaises(TypeError):
            __unit__.mapvalues(MapValues.FUNCTION, None)

    def test_dict__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.mapvalues(MapValues.FUNCTION, object())

    def test_dict__empty(self):
        self.assertEquals({}, __unit__.mapvalues(None, {}))
        self.assertEquals({}, __unit__.mapvalues(MapValues.FUNCTION, {}))

    def test_map(self):
        self.assertEquals(self.MAPPED_DICT,
                          __unit__.mapvalues(MapValues.FUNCTION, self.DICT))


# Extending / combining dictionaries

class _Combine(TestCase):
    KEYS = ('foo', 'bar', 'baz', 'qux', 'thud')

    DICT = dict(zip(KEYS[:3], range(3)))
    OTHER_DICT = dict(zip(KEYS[3:], range(3, len(KEYS))))
    MANY_DICTS = [{k: v} for k, v in zip(KEYS, range(len(KEYS)))]

    COMBINED = dict(zip(KEYS, range(5)))

    # dicts used for testing deep= flag
    DEEP_DICT1 = {'foo': {'bar': 1}, 'baz': 'A'}
    DEEP_DICT2 = {'foo': {'qux': 2}, 'thud': 'B'}
    NOT_DEEP_DICT = {'foo': 'a'}
    COMBINED_DEEP_1_2 = {'foo': {'bar': 1, 'qux': 2}, 'baz': 'A', 'thud': 'B'}
    COMBINED_DEEP1_AND_NOT_DEEP = {'foo': 'a', 'baz': 'A'}

    # dicts used for testing overwrite= flag
    BASE_DICT = {'foo': 1, 'bar': 2}
    OVERWRITING_DICT = {'foo': 10, 'baz': 30}
    OVERWRITTEN_DICT = {'foo': 10, 'bar': 2, 'baz': 30}
    NOT_OVERWRITTEN_DICT = {'foo': 1, 'bar': 2, 'baz': 30}


class Merge(_Combine):
    MERGED = _Combine.COMBINED
    MERGED_DEEP_1_2 = _Combine.COMBINED_DEEP_1_2
    MERGED_DEEP1_AND_NOT_DEEP = _Combine.COMBINED_DEEP1_AND_NOT_DEEP

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.merge()

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

    def test_deep__no_args(self):
        with self.assertRaises(TypeError):
            __unit__.merge(deep=True)

    def test_deep__single_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.merge(None, deep=True)

    def test_deep__single_arg__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.merge(object(), deep=True)

    def test_deep__single_arg__dict(self):
        result = __unit__.merge(self.DICT, deep=True)
        self.assertEquals(self.DICT, result)
        self.assertIsNot(self.DICT, result)

    def test_deep__two_args__shallow(self):
        result = __unit__.merge(self.DICT, self.OTHER_DICT, deep=True)
        self.assertEquals(self.MERGED, result)

    def test_deep__two_args__both_deep(self):
        result = __unit__.merge(self.DEEP_DICT1, self.DEEP_DICT2, deep=True)
        self.assertEquals(self.MERGED_DEEP_1_2, result)

    def test_deep__two_args__deep_and_shallow(self):
        result = __unit__.merge(self.DEEP_DICT1, self.NOT_DEEP_DICT, deep=True)
        self.assertEquals(self.MERGED_DEEP1_AND_NOT_DEEP, result)

    def test_overwrite__no_args(self):
        with self.assertRaises(TypeError):
            __unit__.merge(overwrite=False)

    def test_overwrite__single_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.merge(None, overwrite=False)

    def test_overwrite__single_arg__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.merge(object(), overwrite=False)

    def test_overwrite__single_arg__dict(self):
        result = __unit__.merge(self.BASE_DICT, overwrite=False)
        self.assertEquals(self.BASE_DICT, result)
        self.assertIsNot(self.BASE_DICT, result)

    def test_overwrite__two_args__true(self):
        self.assertEquals(
            self.OVERWRITTEN_DICT,
            __unit__.merge(self.BASE_DICT, self.OVERWRITING_DICT,
                           overwrite=True))

    def test_overwrite__two_args__false(self):
        self.assertEquals(
            self.NOT_OVERWRITTEN_DICT,
            __unit__.merge(self.BASE_DICT, self.OVERWRITING_DICT,
                           overwrite=False))


class Extend(_Combine):
    EXTENDED = _Combine.COMBINED
    EXTENDED_DEEP_1_2 = _Combine.COMBINED_DEEP_1_2
    EXTENDED_DEEP1_AND_NOT_DEEP = _Combine.COMBINED_DEEP1_AND_NOT_DEEP

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.extend(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.extend(object())

    def test_empty_dict__one(self):
        original = {}
        extended = __unit__.extend(original)

        self.assertIs(original, extended)
        self.assertEquals({}, extended)

    def test_empty_dict__many(self):
        original = {}
        extended = __unit__.extend(original, {}, {})

        self.assertIs(original, extended)
        self.assertEquals({}, extended)

    def test_dict__one(self):
        original = self.DICT.copy()
        extended = __unit__.extend(original)

        self.assertIs(original, extended)
        self.assertEquals(self.DICT, extended)

    def test_dict__two(self):
        original = self.DICT.copy()
        extended = __unit__.extend(original, self.OTHER_DICT)

        self.assertIs(original, extended)
        self.assertIsNot(self.DICT, extended)
        self.assertIsNot(self.OTHER_DICT, extended)

        self.assertEquals(self.EXTENDED, extended)

    def test_dict__many(self):
        original = self.MANY_DICTS[0].copy()
        extended = __unit__.extend(original, *self.MANY_DICTS[1:])

        self.assertIs(original, extended)
        for d in self.MANY_DICTS:
            self.assertIsNot(d, extended)

        self.assertEquals(self.EXTENDED, extended)

    def test_deep__none(self):
        with self.assertRaises(TypeError):
            __unit__.extend(None, deep=True)

    def test_deep__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.extend(object(), deep=True)

    def test_deep__dict__empty(self):
        original = {}
        extended = __unit__.extend(original, {}, deep=True)

        self.assertIs(original, extended)
        self.assertEquals({}, extended)

    def test_deep__dict__shallow(self):
        original = self.DICT.copy()
        extended = __unit__.extend(original, self.OTHER_DICT, deep=True)

        self.assertIs(original, extended)
        self.assertEquals(self.EXTENDED, extended)

    def test_deep__dict__both_deep(self):
        original = self.DEEP_DICT1.copy()
        extended = __unit__.extend(original, self.DEEP_DICT2, deep=True)

        self.assertIs(original, extended)
        self.assertEquals(self.EXTENDED_DEEP_1_2, extended)

    def test_deep__dict__deep_and_shallow(self):
        original = self.DEEP_DICT1.copy()
        extended = __unit__.extend(original, self.NOT_DEEP_DICT, deep=True)

        self.assertIs(original, extended)
        self.assertEquals(self.EXTENDED_DEEP1_AND_NOT_DEEP, extended)

    def test_overwrite__none(self):
        with self.assertRaises(TypeError):
            __unit__.extend(None, overwrite=False)

    def test_overwrite__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.extend(object(), overwrite=False)

    def test_overwrite__empty_dicts(self):
        original = {}
        extended = __unit__.extend(original, {}, overwrite=False)

        self.assertIs(original, extended)
        self.assertEquals({}, extended)

    def test_overwrite__true(self):
        original = self.BASE_DICT.copy()
        extended = __unit__.extend(original, self.OVERWRITING_DICT,
                                   overwrite=True)

        self.assertIs(original, extended)
        self.assertEquals(self.OVERWRITTEN_DICT, extended)

    def test_overwrite__false(self):
        original = self.BASE_DICT.copy()
        extended = __unit__.extend(original, self.OVERWRITING_DICT,
                                   overwrite=False)

        self.assertIs(original, extended)
        self.assertEquals(self.NOT_OVERWRITTEN_DICT, extended)


# Other transformation functions

class Invert(TestCase):
    INVERTIBLE_DICT = dict(zip(ALPHABET, range(1, len(ALPHABET) + 1)))
    UNINVERTIBLE_DICT = dict(zip(range(1, 2 * len(ALPHABET) + 1),
                                 ALPHABET * 2))

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.invert(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.invert(object())

    def test_empty(self):
        self.assertEquals({}, __unit__.invert({}))

    def test_invertible(self):
        inverted_dict = __unit__.invert(self.INVERTIBLE_DICT)
        self.assertItemsEqual(
            self.INVERTIBLE_DICT.values(), inverted_dict.keys())
        self.assertItemsEqual(
            self.INVERTIBLE_DICT.keys(), inverted_dict.values())

    def test_uninvertible(self):
        # a bit of misnomer, but it means dictionary has duplicate values
        inverted_dict = __unit__.invert(self.UNINVERTIBLE_DICT)
        self.assertGreater(
            set(self.UNINVERTIBLE_DICT.keys()), set(inverted_dict.values()))
