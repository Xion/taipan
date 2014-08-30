"""
Tests for .collections.sets module.
"""
from contextlib import contextmanager

from taipan._compat import xrange
from taipan.collections import is_set
from taipan.collections.tuples import is_tuple
from taipan.testing import TestCase

import taipan.collections.sets as __unit__


class Peek(TestCase):
    SET = set(xrange(3))

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.peek(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.peek(object())

    def test_non_set_iterable(self):
        with self.assertRaises(TypeError):
            __unit__.peek([42])

    def test_set__empty(self):
        with self.assertRaises(KeyError):
            __unit__.peek(set())

    def test_set__normal(self):
        element = __unit__.peek(self.SET)
        self.assertIn(element, self.SET)


class RemoveSubset(TestCase):
    SINGLETON = set(['foo'])
    SET = set('foo bar baz'.split())
    DIFFERENCE = SET - SINGLETON

    def test_set__none(self):
        with self.assertRaises(TypeError):
            __unit__.remove_subset(None, set())

    def test_set__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.remove_subset(object(), set())

    def test_subset__none(self):
        with self.assertRaises(TypeError):
            __unit__.remove_subset(set(), None)

    def test_subset__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.remove_subset(set(), object())

    def test_empty_sets(self):
        s = set()
        __unit__.remove_subset(s, set())
        self.assertEmpty(s)

    def test_empty_set__empty_iterable_subset(self):
        s = set()
        __unit__.remove_subset(s, ())
        self.assertEmpty(s)

    def test_empty_set__nonempty_subset(self):
        s = set()
        with self._assertKeyError(*self.SINGLETON):
            __unit__.remove_subset(s, self.SINGLETON)

    def test_singleton_set__empty_subset(self):
        s = self.SINGLETON.copy()
        __unit__.remove_subset(s, set())
        self.assertEquals(self.SINGLETON, s)

    def test_singleton_set__singleton_subset(self):
        s = self.SINGLETON.copy()
        __unit__.remove_subset(s, self.SINGLETON)
        self.assertEmpty(s)

    def test_singleton_set__too_big_a_subset(self):
        s = self.SINGLETON.copy()
        with self._assertKeyError(*self.DIFFERENCE):
            __unit__.remove_subset(s, self.SET)

    def test_set__empty_subset(self):
        s = self.SET.copy()
        __unit__.remove_subset(s, set())
        self.assertEquals(self.SET, s)

    def test_set__singleton_subset(self):
        s = self.SET.copy()
        __unit__.remove_subset(s, self.SINGLETON)
        self.assertEquals(self.DIFFERENCE, s)

    def test_set__same_one_as_subset(self):
        s = self.SET.copy()
        __unit__.remove_subset(s, self.SET)
        self.assertEmpty(s)

    # Utility finctions

    @contextmanager
    def _assertKeyError(self, *keys):
        """Assert that code raises KeyError with one of given keys."""
        with self.assertRaises(KeyError) as r:
            yield r

        msg = str(r.exception)
        self.assertAny(
            lambda key: repr(key) == msg, keys,
            msg="expected KeyError not raised; got %s instead of one of %s" % (
                msg, list(map(repr, keys))))


# Subset generation

class _SubsetGeneration(TestCase):
    TWO_ELEMS_TUPLE = (1, 2)
    TWO_ELEMS_SET = set([1, 2])


class KSubsets(_SubsetGeneration):

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


class Power(_SubsetGeneration):
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


class TrivialPartition(_SubsetGeneration):
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
