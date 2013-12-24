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

    def test_empty(self):
        with self.assertRaises(ValueError):
            __unit__.init([])

    def test_normal(self):
        self.assertEquals(self.INIT, __unit__.init(self.LIST))
