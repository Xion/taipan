"""
Tests for .api.fluency module.
"""
from functools import reduce
import operator

from taipan.testing import TestCase

import taipan.api.fluency as __unit__


class Fluent(TestCase):
    SIMPLE_RESULT = object()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.fluent(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.fluent(object())

    def test_empty_class(self):
        @__unit__.fluent
        class Foo(object):
            pass

    def test_class__fluentized_method(self):
        @__unit__.fluent
        class Foo(object):
            def florbed(self):
                pass  # no ``return self``

        foo = Foo()
        self.assertEquals(foo, foo.florbed())

    def test_class__already_fluent_method(self):
        @__unit__.fluent
        class Foo(object):
            def florbed(self):
                return self

        foo = Foo()
        self.assertEquals(foo, foo.florbed())

    def test_class__invalid_method_result(self):
        @__unit__.fluent
        class Foo(object):
            def florbed(self):
                return 42

        foo = Foo()
        with self.assertRaises(__unit__.FluentError):
            foo.florbed()

    def test_class__just_terminator(self):
        @__unit__.fluent(terminators=['blurbicate'])
        class Foo(object):
            def blurbicate(self):
                return Fluent.SIMPLE_RESULT

        foo = Foo()
        self.assertEquals(Fluent.SIMPLE_RESULT, foo.blurbicate())

    def test_class__one_fluent_and_terminator(self):
        @__unit__.fluent(terminators=['compute'])
        class Sum(object):
            def __init__(self):
                self._result = 0
            def add(self, x):
                self._result += x
            def compute(self):
                return self._result

        self.assertEquals(21, Sum()
            .add(1).add(2).add(3).add(4).add(5).add(6)
            .compute())

    def test_class__few_fluents_and_terminator(self):
        @__unit__.fluent(terminators=['build'])
        class DictBuilder(object):
            def __init__(self):
                self._result = {}
            def set(self, key, value):
                self._result[key] = value
            def update(self, dict_):
                self._result.update(dict_)
            def build(self):
                return self._result.copy()

        # talk about overkill!
        self.assertEquals(dict(foo=1), DictBuilder().set('foo', 1).build())
        self.assertEquals(dict(foo=1, bar=2),
                          DictBuilder().update(dict(foo=1, bar=2)).build())
        self.assertEquals(dict(foo=1, bar=2),
                          DictBuilder().set('foo', 1).set('bar', 2).build())
        self.assertEquals(
            dict(foo=1, bar=2),
            DictBuilder().update(dict(foo=1)).update(dict(bar=2)).build())
        self.assertEquals(
            dict(foo=1, bar=2),
            DictBuilder().set('foo', 1).update(dict(bar=2)).build())
        self.assertEquals(
            dict(foo=1, bar=2),
            DictBuilder().update(dict(foo=1)).set('bar', 2).build())

    def test_class__multiple_terminators(self):
        @__unit__.fluent(terminators=['sum', 'product'])
        class Accumulator(object):
            def __init__(self):
                self._items = []
            def put(self, item):
                self._items.append(item)
            def sum(self):
                return reduce(operator.add, self._items[1:], self._items[0]) \
                    if self._items else None
            def product(self):
                return reduce(operator.mul, self._items[1:], self._items[0]) \
                    if self._items else None

        accum = Accumulator().put(1).put(2).put(3).put(4).put(5).put(6)
        self.assertEquals(21, accum.sum())
        self.assertEquals(720, accum.product())


class Terminator(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.terminator(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.terminator(object())

    def test_fluent__just_terminator(self):
        @__unit__.fluent
        class Foo(object):
            @__unit__.terminator
            def blurbicate(self):
                return Fluent.SIMPLE_RESULT

        foo = Foo()
        self.assertEquals(Fluent.SIMPLE_RESULT, foo.blurbicate())

    def test_fluent__one_fluent_and_terminator(self):
        @__unit__.fluent
        class Sum(object):
            def __init__(self):
                self._result = 0
            def add(self, x):
                self._result += x
            @__unit__.terminator
            def compute(self):
                return self._result

        self.assertEquals(21, Sum()
            .add(1).add(2).add(3).add(4).add(5).add(6)
            .compute())

    def test_fluent__multiple_terminators(self):
        @__unit__.fluent
        class Accumulator(object):
            def __init__(self):
                self._items = []
            def put(self, item):
                self._items.append(item)
            @__unit__.terminator
            def sum(self):
                return reduce(operator.add, self._items[1:], self._items[0]) \
                    if self._items else None
            @__unit__.terminator
            def product(self):
                return reduce(operator.mul, self._items[1:], self._items[0]) \
                    if self._items else None

        accum = Accumulator().put(1).put(2).put(3).put(4).put(5).put(6)
        self.assertEquals(21, accum.sum())
        self.assertEquals(720, accum.product())

    def test_alias(self):
        @__unit__.fluent
        class Foo(object):
            @__unit__.fluent.terminator
            def blurbicate(self):
                return Fluent.SIMPLE_RESULT

        foo = Foo()
        self.assertEquals(Fluent.SIMPLE_RESULT, foo.blurbicate())
