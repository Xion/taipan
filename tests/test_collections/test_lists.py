"""
Tests for the .collections.lists module.
"""
from taipan.testing import TestCase

import taipan.collections.lists as __unit__


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
