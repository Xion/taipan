"""
Tests for .algorithms module.
"""
from collections import namedtuple

from taipan._compat import IS_PY3, izip, xrange
from taipan.collections import is_iterable, is_sequence
from taipan.collections.tuples import is_tuple
from taipan.functional import functions ; attr_func = functions.attr_func
from taipan.testing import TestCase

import taipan.algorithms as __unit__


class _Algorithm(TestCase):

    def _assertGenerator(self, obj):
        # objects returned by itertools functions are not "generators"
        # in the strict sense of the word (i.e. results of functions with
        # ``yield`` or comprehensions) but they behave functionally as such,
        # so we check for a more general condition: iterable w/o ``__len__``
        self.assertTrue(is_iterable(obj) and not is_sequence(obj),
                        msg="%r is not a generator" % (obj,))


class Batch(_Algorithm):
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


class Cycle(_Algorithm):
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
        self.assertEmpty(
            cycled, msg="cycled empty iterable expected to be also empty")

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
        self.assertEmpty(
            cycled, msg="iterable cycled 0 times expected to be empty")

    def test_n__negative(self):
        with self.assertRaises(ValueError):
            __unit__.cycle(self.ITERABLE, -1)

    def test_n__positive(self):
        cycled = __unit__.cycle(self.ITERABLE, self.CYCLES_COUNT)

        # iterate for an exactly the expected number of elements
        for i, elem in izip(xrange(self.LENGTH * self.CYCLES_COUNT), cycled):
            self.assertEquals(self.ITERABLE[i % self.LENGTH], elem)

        # make sure the cycled iterable has been exhausted this way
        with self.assertRaises(StopIteration):
            next(cycled)


class Intertwine(_Algorithm):
    FIRST = [1, 2, 3]
    SECOND = ['a', 'b', 'c']
    FIRST_AND_SECOND = [1, 'a', 2, 'b', 3, 'c']

    LONGER = [13, 21, 34, 55, 89]
    SHORTER = ['foo', 'bar', 'baz']
    LONGER_AND_SHORTER = [13, 'foo', 21, 'bar', 34, 'baz', 55, 89]

    def test_no_args(self):
        intertwined = __unit__.intertwine()
        self.assertEmpty(intertwined)

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.intertwine(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.intertwine(object())

    def test_single_iterable(self):
        self.assertItemsEqual(self.FIRST, __unit__.intertwine(self.FIRST))
        self.assertItemsEqual(self.SECOND, __unit__.intertwine(self.SECOND))

    def test_single_iterable__passed_twice(self):
        self.assertItemsEqual(
            self.FIRST * 2, __unit__.intertwine(self.FIRST, self.FIRST))
        self.assertItemsEqual(
            self.SECOND * 2, __unit__.intertwine(self.SECOND, self.SECOND))

    def test_two_iterables__one_empty(self):
        self.assertItemsEqual(self.FIRST, __unit__.intertwine(self.FIRST, ()))
        self.assertItemsEqual(self.SECOND, __unit__.intertwine(self.SECOND, ()))

    def test_two_iterables__equal_lengths(self):
        self.assertItemsEqual(self.FIRST_AND_SECOND,
                              __unit__.intertwine(self.FIRST, self.SECOND))

    def test_two_iterables__inequal_lengths(self):
        self.assertItemsEqual(
            self.LONGER_AND_SHORTER,
            __unit__.intertwine(self.LONGER, self.SHORTER))


class Iterate(_Algorithm):
    MAX = 10
    FEW = int(MAX / 2)

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

        if IS_PY3:
            __next__ = next

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


class Pad(_Algorithm):
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


class Unique(_Algorithm):
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


# Traversal

class _Traversal(_Algorithm):
    Node = namedtuple('Node', ['value', 'children'])
    CHILDREN_FUNC = attr_func('children')

    def _create_node(self, value=None, children=None):
        return self.Node(value=value, children=list(children or []))

    def _create_path(self, length, start=0):
        if length > 0:
            node = self._create_node(start + length - 1)
            for i in range(start + length - 2, start - 1, -1):
                node = self._create_node(i, [node])
            return node


class BreadthFirst(_Traversal):

    def test_start__none(self):
        bfs = __unit__.breadth_first(None, expand=functions.empty())
        self.assertItemsEqual([None], bfs)

    def test_start__some_object(self):
        obj = object()
        bfs = __unit__.breadth_first(obj, expand=functions.empty())
        self.assertItemsEqual([obj], bfs)

    def test_start__single_node(self):
        bfs = __unit__.breadth_first(self._create_node(), self.CHILDREN_FUNC)
        next(bfs)
        self.assertEmpty(bfs)

    def test_start__path(self):
        graph = self._create_path(10)
        bfs = __unit__.breadth_first(graph, self.CHILDREN_FUNC)
        for i, node in enumerate(bfs, 0):
            self.assertEquals(i, node.value)

    def test_start__flat_graph(self):
        nodes = list(map(self._create_node, range(1, 5 + 1)))
        graph = self._create_node(0, nodes)

        bfs = __unit__.breadth_first(graph, self.CHILDREN_FUNC)
        for i, node in enumerate(bfs, 0):
            self.assertEquals(i, node.value)

    def test_expand__none(self):
        with self.assertRaises(TypeError):
            __unit__.breadth_first(self._create_node(), expand=None)

    def test_expand__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.breadth_first(self._create_node(), expand=object())


class DepthFirst(_Traversal):

    def test_start__none(self):
        dfs = __unit__.depth_first(None, descend=functions.empty())
        self.assertItemsEqual([None], dfs)

    def test_start__some_object(self):
        obj = object()
        dfs = __unit__.depth_first(obj, descend=functions.empty())
        self.assertItemsEqual([obj], dfs)

    def test_start__single_node(self):
        dfs = __unit__.depth_first(self._create_node(), self.CHILDREN_FUNC)
        next(dfs)
        self.assertEmpty(dfs)

    def test_start__path(self):
        graph = self._create_path(10)
        dfs = __unit__.depth_first(graph, self.CHILDREN_FUNC)
        for i, node in enumerate(dfs, 0):
            self.assertEquals(i, node.value)

    def test_start__flat_graph(self):
        child_values = range(1, 5 + 1)
        nodes = list(map(self._create_node, child_values))
        graph = self._create_node(0, nodes)

        dfs = __unit__.depth_first(graph, self.CHILDREN_FUNC)
        expected_values_order = [0] + list(reversed(child_values))
        for i, node in zip(expected_values_order, dfs):
            self.assertEquals(i, node.value)

    def test_descend__none(self):
        with self.assertRaises(TypeError):
            __unit__.depth_first(self._create_node(), descend=None)

    def test_descend__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.depth_first(self._create_node(), descend=object())
