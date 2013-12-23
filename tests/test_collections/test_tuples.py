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
