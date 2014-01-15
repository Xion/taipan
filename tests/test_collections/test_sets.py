"""
Tests for .collections.sets module.
"""
from taipan._compat import xrange
from taipan.collections import is_set
from taipan.collections.tuples import is_tuple
from taipan.testing import TestCase

import taipan.collections.sets as __unit__


class Power(TestCase):
    TWO_ELEMS_TUPLE = (1, 2)
    POWERSET_OF_TWO_ELEMS_TUPLE = [(), (1,), (2,), (1, 2)]

    TWO_ELEMS_SET = set([1, 2])
    POWERSET_OF_TWO_ELEMS_SET = [set(), set([1]), set([2]), set([1, 2])]

    EIGHT_ELEMS_TUPLE = tuple(xrange(8))
    EIGHT_ELEMS_SET = set(xrange(8))

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.power(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.power(object())

    def test_empty_iterable(self):
        self.assertItemsEqual([()], __unit__.power([]))

    def test_singleton_iterable(self):
        self.assertItemsEqual([(), (42,)], __unit__.power([42]))

    def test_empty_set(self):
        self.assertItemsEqual([set()], __unit__.power(set()))

    def test_singleton_set(self):
        set_ = set([42])
        self.assertItemsEqual([set(), set_], __unit__.power(set_))

    def test_cardinality2_iterable(self):
        self.assertItemsEqual(
            self.POWERSET_OF_TWO_ELEMS_TUPLE,
            __unit__.power(self.TWO_ELEMS_TUPLE))

    def test_cardinality2_set(self):
        self.assertItemsEqual(
            self.POWERSET_OF_TWO_ELEMS_SET, __unit__.power(self.TWO_ELEMS_SET))

    def test_cardinality8_iterable__just_count(self):
        powerset = list(__unit__.power(self.EIGHT_ELEMS_TUPLE))
        self.assertAll(is_tuple, powerset)
        self.assertEquals(2 ** len(self.EIGHT_ELEMS_TUPLE), len(powerset))

    def test_cardinality8_set__just_count(self):
        powerset = list(__unit__.power(self.EIGHT_ELEMS_SET))
        self.assertAll(is_set, powerset)
        self.assertEquals(2 ** len(self.EIGHT_ELEMS_SET), len(powerset))
