"""
Tests for .collections.sets module.
"""
from taipan._compat import xrange
from taipan.collections import is_set
from taipan.collections.tuples import is_tuple
from taipan.testing import TestCase

import taipan.collections.sets as __unit__


class _SubsetOperation(TestCase):
    TWO_ELEMS_TUPLE = (1, 2)
    TWO_ELEMS_SET = set([1, 2])


class KSubsets(_SubsetOperation):

    def test_set__none(self):
        with self.assertRaises(TypeError):
            __unit__.k_subsets(None, 1)

    def test_set__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.k_subsets(object(), 1)

    def test_set__empty_iterable(self):
        self.assertItemsEqual([()], __unit__.k_subsets([], 0))

    def test_set__singleton_iterable(self):
        self.assertItemsEqual([(42,)], __unit__.k_subsets([42], 1))

    def test_set__singleton_set(self):
        set_ = set([42])
        self.assertItemsEqual([set_], __unit__.k_subsets(set_, 1))

    def test_k__none(self):
        with self.assertRaises(TypeError):
            __unit__.k_subsets(self.TWO_ELEMS_SET, None)

    def test_k__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.k_subsets(self.TWO_ELEMS_SET, object())

    def test_k__negative(self):
        with self.assertRaises(ValueError):
            __unit__.k_subsets(self.TWO_ELEMS_SET, -1)

    def test_k__zero(self):
        self.assertItemsEqual([set()], __unit__.k_subsets(set(), 0))
        self.assertItemsEqual(
            [set()], __unit__.k_subsets(self.TWO_ELEMS_SET, 0))

    def test_k__one(self):
        self.assertItemsEqual(
            [set((x,)) for x in self.TWO_ELEMS_SET],
            __unit__.k_subsets(self.TWO_ELEMS_SET, 1))

    def test_k__positive(self):
        self.assertItemsEqual(
            [self.TWO_ELEMS_SET], __unit__.k_subsets(self.TWO_ELEMS_SET, 2))

    def test_k__too_big(self):
        with self.assertRaises(ValueError):
            __unit__.k_subsets(self.TWO_ELEMS_SET, len(self.TWO_ELEMS_SET) + 1)


class Power(_SubsetOperation):
    POWERSET_OF_TWO_ELEMS_TUPLE = [(), (1,), (2,), (1, 2)]
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


class TrivialPartition(_SubsetOperation):
    TRIVIAL_PARTITION_OF_TWO_ELEMS_TUPLE = [(1,), (2,)]
    TRIVIAL_PARTITION_OF_TWO_ELEMS_SET = [set((1,)), set((2,))]

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.trivial_partition(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.trivial_partition(object())

    def test_empty_iterable(self):
        self.assertEmpty(__unit__.trivial_partition([]))

    def test_singleton_iterable(self):
        self.assertItemsEqual([(42,)], __unit__.trivial_partition([42]))

    def test_empty_set(self):
        self.assertEmpty(__unit__.trivial_partition(set()))

    def test_singleton_set(self):
        set_ = set([42])
        self.assertItemsEqual([set_], __unit__.trivial_partition(set_))

    def test_cardinality2_iterable(self):
        self.assertItemsEqual(
            self.TRIVIAL_PARTITION_OF_TWO_ELEMS_TUPLE,
            __unit__.trivial_partition(self.TWO_ELEMS_TUPLE))

    def test_cardinality2_set(self):
        self.assertItemsEqual(
            self.TRIVIAL_PARTITION_OF_TWO_ELEMS_SET,
            __unit__.trivial_partition(self.TWO_ELEMS_SET))
