"""
Tests for the .collections.tuples module.
"""
from taipan.testing import TestCase

import taipan.collections.tuples as __unit__


class IsTuple(TestCase):
    EMPTY_TUPLE = ()
    TUPLE = ('foo', 'bar', 42)
    TUPLE_SIZE = 3

    def test_arg__none(self):
        self.assertFalse(__unit__.is_tuple(None))

    def test_arg__some_object(self):
        self.assertFalse(__unit__.is_tuple(object()))

    def test__arg__empty_tuple(self):
        self.assertTrue(__unit__.is_tuple(self.EMPTY_TUPLE))

    def test_arg__nonempty_tuple(self):
        self.assertTrue(__unit__.is_tuple(self.TUPLE))

    def test_len__none(self):
        self.assertFalse(__unit__.is_tuple(None, len_=None))
        self.assertFalse(__unit__.is_tuple(object()))
        self.assertTrue(__unit__.is_tuple(self.EMPTY_TUPLE, len_=None))
        self.assertTrue(__unit__.is_tuple(self.TUPLE, len_=None))

    def test_len__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.is_tuple(self.TUPLE, len_=object())

    def test_len__string(self):
        with self.assertRaises(TypeError):
            __unit__.is_tuple(self.TUPLE, len_="42")

    def test_len__zero(self):
        self.assertTrue(__unit__.is_tuple(self.EMPTY_TUPLE, len_=0))
        self.assertFalse(__unit__.is_tuple(self.TUPLE, len_=0))

    def test_len__negative(self):
        with self.assertRaises(ValueError):
            __unit__.is_tuple(self.TUPLE, len_=-1)

    def test_len__positive(self):
        self.assertFalse(
            __unit__.is_tuple(self.EMPTY_TUPLE, len_=self.TUPLE_SIZE))
        self.assertTrue(__unit__.is_tuple(self.TUPLE, len_=self.TUPLE_SIZE))
        self.assertFalse(
            __unit__.is_tuple(self.TUPLE, len_=self.TUPLE_SIZE + 1))


class AccessFunctions(TestCase):
    EMPTY = ()
    SINGLE = (1,)
    PAIR = (1, 2)
    TRIPLE = (1, 2, 3)
    QUADRUPLE = (1, 2, 3, 4)
    QUINTUPLE = (1, 2, 3, 4, 5)

    TUPLES = [EMPTY, SINGLE, PAIR, TRIPLE, QUADRUPLE, QUINTUPLE]

    def test_first(self):
        self._assertTupleAccessFunction(__unit__.first, 1)

    def test_second(self):
        self._assertTupleAccessFunction(__unit__.second, 2)

    def test_third(self):
        self._assertTupleAccessFunction(__unit__.third, 3)

    def test_fourth(self):
        self._assertTupleAccessFunction(__unit__.fourth, 4)

    def test_fifth(self):
        self._assertTupleAccessFunction(__unit__.fifth, 5)

    # Utility functions

    def _assertTupleAccessFunction(self, func, index):
        for t in self.TUPLES[:index]:
            with self.assertRaises(IndexError):
                func(t)
        for t in self.TUPLES[index:]:
            self.assertEquals(index, func(t))


class Select(TestCase):
    TUPLE = tuple(range(5))

    STRICT_INDICES = (1, 2)
    EXTRANEOUS_INDEX = 5
    NONSTRICT_INDICES = (3, 4, EXTRANEOUS_INDEX)

    SELECTED_BY_STRICT_INDICES = (1, 2)
    SELECTED_BY_NONSTRICT_INDICES = (3, 4)

    def test_indices__none(self):
        with self.assertRaises(TypeError):
            __unit__.select(None, self.TUPLE)

    def test_indices__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.select(object(), self.TUPLE)

    def test_indices__empty(self):
        self.assertEquals((), __unit__.select((), self.TUPLE))

    def test_from__none(self):
        with self.assertRaises(TypeError):
            __unit__.select(self.STRICT_INDICES, None)

    def test_from__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.select(self.STRICT_INDICES, object())

    def test_from__empty(self):
        with self.assertRaises(IndexError):
            __unit__.select(self.STRICT_INDICES, (), strict=True)
        self.assertEquals(
            (), __unit__.select(self.NONSTRICT_INDICES, (), strict=False))

    def test_strict__true(self):
        self.assertEquals(
            self.SELECTED_BY_STRICT_INDICES,
            __unit__.select(self.STRICT_INDICES, self.TUPLE, strict=True))
        with self.assertRaises(IndexError):
            __unit__.select(self.NONSTRICT_INDICES, self.TUPLE, strict=True)

    def test_strict__false(self):
        self.assertEquals(
            self.SELECTED_BY_STRICT_INDICES,
            __unit__.select(self.STRICT_INDICES, self.TUPLE, strict=False))
        self.assertEquals(
            self.SELECTED_BY_NONSTRICT_INDICES,
            __unit__.select(self.NONSTRICT_INDICES, self.TUPLE, strict=False))
