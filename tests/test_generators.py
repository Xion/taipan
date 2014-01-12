"""
Tests for .generators module.
"""
from taipan._compat import izip, xrange
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

        self.assertEquals(
            int(len(self.WITHOUT_LEFTOVERS) / self.N), len(batched))
        for i, batch in enumerate(batched):
            self._assertTuple(batch)
            self.assertEquals(self.N, len(batch))
            self.assertItemsEqual(
                self.WITHOUT_LEFTOVERS[i * self.N:(i + 1) * self.N], batch)

    def test_iterable__with_leftovers__trimmed(self):
        batched = __unit__.batch(self.WITH_LEFTOVERS, self.N)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(
            int(len(self.WITH_LEFTOVERS) / self.N) + 1, len(batched))
        for i, batch in enumerate(batched):
            self._assertTuple(batch)
            self.assertGreaterEqual(self.N, len(batch))
            self.assertItemsEqual(
                self.WITH_LEFTOVERS[i * self.N:(i + 1) * self.N], batch)

    def test_iterable__with_leftovers__padded(self):
        batched = __unit__.batch(self.WITH_LEFTOVERS, self.N, self.FILLVALUE)

        self._assertGenerator(batched)
        batched = list(batched)

        self.assertEquals(
            int(len(self.WITH_LEFTOVERS) / self.N) + 1, len(batched))
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


class Cycle(_GeneratorsTestCase):
    LENGTH = 10
    ITERABLE = list(xrange(LENGTH))
    CYCLES_COUNT = 64

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.cycle(None)

    def test_iterable__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.cycle(object())

    def test_iterable__empty(self):
        cycled = __unit__.cycle(())
        for _ in cycled:
            self.fail("cycled empty iterable expected to be also empty")

    def test_n__none(self):
        cycled = __unit__.cycle(self.ITERABLE)

        # iterate for a few cycles and check if elements match
        for i, elem in izip(xrange(self.LENGTH * self.CYCLES_COUNT), cycled):
            self.assertEquals(self.ITERABLE[i % self.LENGTH], elem)

        # make sure there is still some more
        for _ in xrange(self.CYCLES_COUNT):
            next(cycled)

    def test_n__zero(self):
        cycled = __unit__.cycle(self.ITERABLE, 0)
        for _ in cycled:
            self.fail("iterable cycled 0 times expected to be empty")

    def test_n__negative(self):
        with self.assertRaises(ValueError):
            __unit__.cycle(self.ITERABLE, -1)

    def test_n__positive(self):
        cycled = __unit__.cycle(self.ITERABLE, self.CYCLES_COUNT)

        # iterate for a exactly the expected number of elements
        for i, elem in izip(xrange(self.LENGTH * self.CYCLES_COUNT), cycled):
            self.assertEquals(self.ITERABLE[i % self.LENGTH], elem)

        # make sure the cycled iterable has been exhausted this way
        with self.assertRaises(StopIteration):
            next(cycled)


class Intertwine(_GeneratorsTestCase):
    pass


class Iterate(_GeneratorsTestCase):
    MAX = 10
    FEW = MAX / 2

    class Counter(object):
        """Simplest iterable that can tell how much it's been iterated over."""
        def __init__(self, max_count=None):
            self.max_count = max_count
            self.current_count = 0

        def __iter__(self):
            return self

        def next(self):
            if self.max_count is not None:
                if self.current_count >= self.max_count:
                    raise StopIteration()
            self.current_count += 1
            return self.current_count

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.iterate(None)

    def test_iterable__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.iterate(object())

    def test_iterable__finite__few_iterations(self):
        counter = self.Counter(self.MAX)
        __unit__.iterate(counter, self.FEW)
        self.assertEquals(self.FEW, counter.current_count)

    def test_iterable__finite__to_the_end(self):
        counter = self.Counter(self.MAX)
        __unit__.iterate(counter)
        self.assertEquals(self.MAX, counter.current_count)

    def test_iterable__finite__past_the_end(self):
        counter = self.Counter(self.MAX)
        __unit__.iterate(counter, self.MAX * 2)
        self.assertEquals(self.MAX, counter.current_count)

    def test_iterable__finite__multiple_calls(self):
        counter = self.Counter(self.MAX)
        for i in xrange(1, self.FEW):
            __unit__.iterate(counter, self.FEW)
            self.assertEquals(
                min(self.MAX, i * self.FEW), counter.current_count)

    def test_iterable__infinite__few_iterations(self):
        counter = self.Counter()
        __unit__.iterate(counter, self.FEW)
        self.assertEquals(self.FEW, counter.current_count)

    def test_iterable__infinite__multiple_calls(self):
        counter = self.Counter()
        for i in xrange(1, self.FEW):
            __unit__.iterate(counter, self.FEW)
            self.assertEquals(i * self.FEW, counter.current_count)


class Pad(_GeneratorsTestCase):
    LENGTH = 10
    ITERABLE = list(xrange(LENGTH))

    MUCH_MORE_THAN_LENGTH = 100 * LENGTH
    PADDING = object()

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.pad(None)

    def test_iterable__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.pad(object())

    def test_iterable__empty(self):
        padded = __unit__.pad([])

        self._assertGenerator(padded)
        for _, elem in izip(xrange(self.MUCH_MORE_THAN_LENGTH), padded):
            self.assertIsNone(elem)

    def test_pad__default(self):
        padded = __unit__.pad(self.ITERABLE)

        self._assertGenerator(padded)
        for i, elem in izip(xrange(self.MUCH_MORE_THAN_LENGTH), padded):
            if i < self.LENGTH:
                self.assertIs(self.ITERABLE[i], elem)
            else:
                self.assertIsNone(elem)

    def test_pad__custom(self):
        padded = __unit__.pad(self.ITERABLE, with_=self.PADDING)

        self._assertGenerator(padded)
        for i, elem in izip(xrange(self.MUCH_MORE_THAN_LENGTH), padded):
            if i < self.LENGTH:
                self.assertIs(self.ITERABLE[i], elem)
            else:
                self.assertIs(self.PADDING, elem)


class Unique(_GeneratorsTestCase):
    NORMAL_WITHOUT_DUPLICATES = [1, 2, 3, 4, 5]
    NORMAL_WITH_DUPLICATES = [1, 2, 2, 3, 4, 5, 1]

    STRLEN_WITHOUT_DUPLICATES = "Alice has a parrot".split()
    STRLEN_WITH_DUPLICATES = "Alice has a cat and a dog and a parrot".split()

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.unique(None)

    def test_iterable__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.unique(object())

    def test_iterable__empty(self):
        uniqued = __unit__.unique([])

        self._assertGenerator(uniqued)
        uniqued = list(uniqued)

        self.assertZero(len(uniqued))

    def test_iterable__without_duplicates(self):
        uniqued = __unit__.unique(self.NORMAL_WITHOUT_DUPLICATES)

        self._assertGenerator(uniqued)
        uniqued = list(uniqued)

        self.assertItemsEqual(self.NORMAL_WITHOUT_DUPLICATES, uniqued)

    def test_iterable__with_duplicates(self):
        uniqued = __unit__.unique(self.NORMAL_WITH_DUPLICATES)

        self._assertGenerator(uniqued)
        uniqued = list(uniqued)

        self.assertItemsEqual(self.NORMAL_WITHOUT_DUPLICATES, uniqued)

    def test_key__non_function(self):
        with self.assertRaises(TypeError):
            __unit__.unique((), object())

    def test_key__strlen__without_duplicates(self):
        uniqued = __unit__.unique(self.STRLEN_WITHOUT_DUPLICATES, key=len)

        self._assertGenerator(uniqued)
        uniqued = list(uniqued)

        self.assertItemsEqual(self.STRLEN_WITHOUT_DUPLICATES, uniqued)

    def test_key__strlen__with_duplicates(self):
        uniqued = __unit__.unique(self.STRLEN_WITH_DUPLICATES, key=len)

        self._assertGenerator(uniqued)
        uniqued = list(uniqued)

        self.assertItemsEqual(self.STRLEN_WITHOUT_DUPLICATES, uniqued)
