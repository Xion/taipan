"""
Tests for .generators module.
"""
from taipan.collections import is_iterable, is_sequence
from taipan.collections.tuples import is_tuple
from taipan.testing import TestCase

import taipan.generators as __unit__


class _GeneratorsTestCase(TestCase):

    def _assertGenerator(self, obj):
        # objects returned by itertools functions are not "generators"
        # in the strict sense of the word (i.e. results of functions with
        # ``yield`` or comprehensions) but they behave functionally as such,
        # so we check for a more general condition: iterable w/o ``__len__``
        self.assertTrue(is_iterable(obj) and not is_sequence(obj),
                        msg="%r is not a generator" % (obj,))


class Batch(_GeneratorsTestCase):
    N = 3

    WITHOUT_LEFTOVERS = [1, 2, 3, 4, 5, 6]
    WITH_LEFTOVERS = [1, 2, 3, 4, 5]
    FILLVALUE = object()

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.batch(None, 1)

    def test_iterable__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.batch(object(), 1)

    def test_iterable__without_leftovers(self):
        batched = __unit__.batch(self.WITHOUT_LEFTOVERS, self.N)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(len(self.WITHOUT_LEFTOVERS) / self.N, len(batched))
        for i, batch in enumerate(batched):
            self._assertTuple(batch)
            self.assertEquals(self.N, len(batch))
            self.assertItemsEqual(
                self.WITHOUT_LEFTOVERS[i * self.N:(i + 1) * self.N], batch)

    def test_iterable__with_leftovers__trimmed(self):
        batched = __unit__.batch(self.WITH_LEFTOVERS, self.N)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(len(self.WITH_LEFTOVERS) / self.N + 1, len(batched))
        for i, batch in enumerate(batched):
            self._assertTuple(batch)
            self.assertGreaterEqual(self.N, len(batch))
            self.assertItemsEqual(
                self.WITH_LEFTOVERS[i * self.N:(i + 1) * self.N], batch)

    def test_iterable__with_leftovers__padded(self):
        batched = __unit__.batch(self.WITH_LEFTOVERS, self.N, self.FILLVALUE)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(len(self.WITH_LEFTOVERS) / self.N + 1, len(batched))
        for i, batch in enumerate(batched):
            self._assertTuple(batch)
            self.assertEquals(self.N, len(batch))
            for j, elem in enumerate(batch):
                index = i * self.N + j
                if index < len(self.WITH_LEFTOVERS):
                    self.assertEquals(self.WITH_LEFTOVERS[index], elem)
                else:
                    self.assertIs(self.FILLVALUE, elem)

    def test_n__none(self):
        with self.assertRaises(TypeError):
            __unit__.batch(self.WITH_LEFTOVERS, None)

    def test_n__zero(self):
        with self.assertRaises(ValueError):
            __unit__.batch(self.WITH_LEFTOVERS, 0)

    def test_n__negative(self):
        with self.assertRaises(ValueError):
            __unit__.batch(self.WITH_LEFTOVERS, -1)

    def test_n__greater_than_iterable_length(self):
        batched = __unit__.batch(
            self.WITHOUT_LEFTOVERS, len(self.WITHOUT_LEFTOVERS) + self.N)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(1, len(batched))
        self.assertItemsEqual(self.WITHOUT_LEFTOVERS, batched[0])

    # Assertions

    def _assertTuple(self, obj):
        self.assertTrue(is_tuple(obj), msg="%r is not a tuple" % (obj,))
