"""
Tests for the .collections.lists module.
"""
from contextlib import contextmanager

from taipan.testing import TestCase

import taipan.collections.lists as __unit__


# Element access

class Head(TestCase):
    HEAD = 1
    SINGLETON_LIST = [HEAD]
    NORMAL_LIST = [HEAD, 2.0, "three"]

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.head(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.head(object())

    def test_empty(self):
        with self.assertRaises(IndexError):
            __unit__.head([])

    def test_singleton(self):
        self.assertEquals(self.HEAD, __unit__.head(self.SINGLETON_LIST))

    def test_normal(self):
        self.assertEquals(self.HEAD, __unit__.head(self.NORMAL_LIST))


class Last(TestCase):
    LAST = "three"
    SINGLETON_LIST = [LAST]
    NORMAL_LIST = [1, 2.0, LAST]

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.last(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.last(object())

    def test_empty(self):
        with self.assertRaises(IndexError):
            __unit__.last([])

    def test_singleton(self):
        self.assertEquals(self.LAST, __unit__.last(self.SINGLETON_LIST))

    def test_normal(self):
        self.assertEquals(self.LAST, __unit__.last(self.NORMAL_LIST))


class Tail(TestCase):
    TAIL = [2.0, "three"]
    LIST = [1] + TAIL

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.tail(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.tail(object())

    def test_empty(self):
        with self.assertRaises(ValueError):
            __unit__.tail([])

    def test_normal(self):
        self.assertEquals(self.TAIL, __unit__.tail(self.LIST))


class Init(TestCase):
    INIT = [1, 2.0]
    LIST = INIT + ["three"]

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.init(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.init(object())

    def test_empty(self):
        with self.assertRaises(ValueError):
            __unit__.init([])

    def test_normal(self):
        self.assertEquals(self.INIT, __unit__.init(self.LIST))


# Searching for elements

class _Search(TestCase):
    LIST = [0, 1, 2, 1, 0]

    EVEN = staticmethod(lambda x: x % 2 == 0)
    ODD = staticmethod(lambda x: x % 2 == 1)
    NEGATIVE = staticmethod(lambda x: x < 0)


class _Find(_Search):

    @contextmanager
    def assertNotFound(self):
        with self.assertRaises(IndexError) as r:
            yield r
        self.assertIn("not found", str(r.exception))


class Find(_Find):
    FIRST_EVEN = 0
    FIRST_ODD = 1

    def test_positional__list__none(self):
        with self.assertRaises(TypeError):
            __unit__.find(None, None)

    def test_positional__list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.find(None, object())

    def test_positional__list__empty(self):
        with self.assertNotFound():
            __unit__.find(None, [])
        for elem in self.LIST:
            with self.assertNotFound():
                __unit__.find(elem, [])

    def test_positional__list__normal(self):
        for elem in self.LIST:
            self.assertEquals(elem, __unit__.find(elem, self.LIST))

    def test_keyword__only_list(self):
        with self.assertRaises(TypeError):
            __unit__.find(in_=self.LIST)

    def test_keyword__of__absent(self):
        with self.assertNotFound():
            __unit__.find(of=None, in_=self.LIST)

    def test_keyword__of__present(self):
        for elem in self.LIST:
            self.assertEquals(elem, __unit__.find(of=elem, in_=self.LIST))

    def test_keyword__where__absent(self):
        with self.assertNotFound():
            __unit__.find(where=self.NEGATIVE, in_=self.LIST)

    def test_keyword__where__present(self):
        self.assertEquals(
            self.FIRST_EVEN, __unit__.find(where=self.EVEN, in_=self.LIST))
        self.assertEquals(
            self.FIRST_ODD, __unit__.find(where=self.ODD, in_=self.LIST))

    def test_keyword__both(self):
        with self.assertRaises(TypeError):
            __unit__.find(of=None, where=self.EVEN, in_=self.LIST)


class FindLast(_Find):
    LAST_EVEN = 0
    LAST_ODD = 1

    def test_positional__list__none(self):
        with self.assertRaises(TypeError):
            __unit__.findlast(None, None)

    def test_positional__list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.findlast(None, object())

    def test_positional__list__empty(self):
        with self.assertNotFound():
            __unit__.findlast(None, [])
        for elem in self.LIST:
            with self.assertNotFound():
                __unit__.findlast(elem, [])

    def test_positional__list__normal(self):
        for elem in self.LIST:
            self.assertEquals(elem, __unit__.findlast(elem, self.LIST))

    def test_keyword__only_list(self):
        with self.assertRaises(TypeError):
            __unit__.findlast(in_=self.LIST)

    def test_keyword__of__absent(self):
        with self.assertNotFound():
            __unit__.findlast(of=None, in_=self.LIST)

    def test_keyword__of__present(self):
        for elem in self.LIST:
            self.assertEquals(elem, __unit__.findlast(of=elem, in_=self.LIST))

    def test_keyword__where__absent(self):
        with self.assertNotFound():
            __unit__.findlast(where=self.NEGATIVE, in_=self.LIST)

    def test_keyword__where__present(self):
        self.assertEquals(
            self.LAST_EVEN, __unit__.findlast(where=self.EVEN, in_=self.LIST))
        self.assertEquals(
            self.LAST_ODD, __unit__.findlast(where=self.ODD, in_=self.LIST))

    def test_keyword__both(self):
        with self.assertRaises(TypeError):
            __unit__.findlast(of=None, where=self.EVEN, in_=self.LIST)


class Index(_Search):
    INDICES = [0, 1, 2]

    EVEN_INDEX = 0
    ODD_INDEX = 1

    def test_positional__list__none(self):
        with self.assertRaises(TypeError):
            __unit__.index(None, None)

    def test_positional__list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.index(None, object())

    def test_positional__list__empty(self):
        self.assertEquals(-1, __unit__.index(None, []))
        for elem in self.LIST:
            self.assertEquals(-1, __unit__.index(elem, []))

    def test_positional__list__normal(self):
        for elem in self.LIST:
            self.assertEquals(
                self.INDICES[elem], __unit__.index(elem, self.LIST))

    def test_keyword__only_list(self):
        with self.assertRaises(TypeError):
            __unit__.index(in_=self.LIST)

    def test_keyword__of__absent(self):
        self.assertEquals(-1, __unit__.index(of=None, in_=self.LIST))

    def test_keyword__of__present(self):
        for elem in self.LIST:
            self.assertEquals(
                self.INDICES[elem], __unit__.index(of=elem, in_=self.LIST))

    def test_keyword__where__absent(self):
        self.assertEquals(
            -1, __unit__.index(where=self.NEGATIVE, in_=self.LIST))

    def test_keyword__where__present(self):
        self.assertEquals(
            self.EVEN_INDEX, __unit__.index(where=self.EVEN, in_=self.LIST))
        self.assertEquals(
            self.ODD_INDEX, __unit__.index(where=self.ODD, in_=self.LIST))

    def test_keyword__both(self):
        with self.assertRaises(TypeError):
            __unit__.index(of=None, where=self.EVEN, in_=self.LIST)


class LastIndex(_Search):
    LAST_INDICES = [4, 3, 2]

    EVEN_LAST_INDEX = 4
    ODD_LAST_INDEX = 3

    def test_positional__list__none(self):
        with self.assertRaises(TypeError):
            __unit__.lastindex(None, None)

    def test_positional__list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.lastindex(None, object())

    def test_positional__list__empty(self):
        self.assertEquals(-1, __unit__.lastindex(None, []))
        for elem in self.LIST:
            self.assertEquals(-1, __unit__.lastindex(elem, []))

    def test_positional__list__normal(self):
        for elem in self.LIST:
            self.assertEquals(
                self.LAST_INDICES[elem], __unit__.lastindex(elem, self.LIST))

    def test_keyword__only_list(self):
        with self.assertRaises(TypeError):
            __unit__.lastindex(in_=self.LIST)

    def test_keyword__of__absent(self):
        self.assertEquals(-1, __unit__.lastindex(of=None, in_=self.LIST))

    def test_keyword__of__present(self):
        for elem in self.LIST:
            self.assertEquals(self.LAST_INDICES[elem],
                              __unit__.lastindex(of=elem, in_=self.LIST))

    def test_keyword__where__absent(self):
        self.assertEquals(
            -1, __unit__.lastindex(where=self.NEGATIVE, in_=self.LIST))

    def test_keyword__where__present(self):
        self.assertEquals(self.EVEN_LAST_INDEX,
                          __unit__.lastindex(where=self.EVEN, in_=self.LIST))
        self.assertEquals(self.ODD_LAST_INDEX,
                          __unit__.lastindex(where=self.ODD, in_=self.LIST))

    def test_keyword__both(self):
        with self.assertRaises(TypeError):
            __unit__.lastindex(of=None, where=self.EVEN, in_=self.LIST)


# List manipulation

class Intersperse(TestCase):
    ELEMENT = 0

    SINGLETON_LIST = [42]
    LIST = [1, 2.0, "three"]
    INTERSPERSED = [1, 0, 2.0, 0, "three"]

    def test_list__none(self):
        with self.assertRaises(TypeError):
            __unit__.intersperse(self.ELEMENT, None)

    def test_list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.intersperse(self.ELEMENT, object())

    def test_list__empty(self):
        self.assertEquals([], __unit__.intersperse(self.ELEMENT, []))

    def test_list__singleton(self):
        self.assertEquals(
            self.SINGLETON_LIST,
            __unit__.intersperse(self.ELEMENT, self.SINGLETON_LIST))

    def test_list__normal(self):
        self.assertEquals(
            self.INTERSPERSED, __unit__.intersperse(self.ELEMENT, self.LIST))


class Intercalate(TestCase):
    ELEMENTS = [-1, -2]

    SINGLETON_LIST = [42]
    LIST = [1, 2.0, "three"]
    INTERCALATED = [1, -1, -2, 2.0, -1, -2, "three"]

    def test_elems__none(self):
        with self.assertRaises(TypeError):
            __unit__.intercalate(None, self.LIST)

    def test_elems__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.intercalate(object(), self.LIST)

    def test_elems__empty(self):
        self.assertEquals(self.LIST, __unit__.intercalate([], self.LIST))

    def test_list__none(self):
        with self.assertRaises(TypeError):
            __unit__.intercalate(self.ELEMENTS, None)

    def test_list__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.intercalate(self.ELEMENTS, object())

    def test_list__empty(self):
        self.assertEquals([], __unit__.intercalate(self.ELEMENTS, []))

    def test__list__singleton(self):
        self.assertEquals(
            self.SINGLETON_LIST,
            __unit__.intercalate(self.ELEMENTS, self.SINGLETON_LIST))

    def test_list__normal(self):
        self.assertEquals(
            self.INTERCALATED, __unit__.intercalate(self.ELEMENTS, self.LIST))


class Concat(TestCase):
    INVALID_WITH_NUMBER = [range(3), 1]
    INVALID_WITH_STRING = [range(3), "baz"]

    LISTS = [[1, 2.0, "three"], ["foo", "bar"]]
    CONCATENATED = [1, 2.0, "three", "foo", "bar"]

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.concat(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.concat(object())

    def test_empty(self):
        self.assertNoop(__unit__.concat, [])

    def test_invalid__with_number(self):
        with self.assertRaises(TypeError):
            __unit__.concat(self.INVALID_WITH_NUMBER)

    def test_invalid__with_string(self):
        # string is theoretially also a sequence, but making it suddenly
        # behave like a list here would be prone to produce nasty bugs
        with self.assertRaises(TypeError):
            __unit__.concat(self.INVALID_WITH_STRING)

    def test_correct(self):
        self.assertEquals(self.CONCATENATED, __unit__.concat(self.LISTS))
