"""
Tests for .lang module.
"""
from contextlib import contextmanager

from taipan.testing import TestCase

import taipan.lang as __unit__


class IsContextmanager(TestCase):

    def test_none(self):
        self.assertFalse(__unit__.is_contextmanager(None))

    def test_some_object(self):
        self.assertFalse(__unit__.is_contextmanager(object()))

    def test_manual(self):
        class ContextManager(object):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        cm = ContextManager()
        self.assertTrue(__unit__.is_contextmanager(cm))

    def test_contextlib(self):
        @contextmanager
        def func():
            yield

        cm = func()
        self.assertTrue(__unit__.is_contextmanager(cm))


class EnsureContextmanager(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_contextmanager(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_contextmanager(object())

    def test_manual(self):
        class ContextManager(object):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass

        cm = ContextManager()
        __unit__.ensure_contextmanager(cm)

    def test_contextlib(self):
        @contextmanager
        def func():
            yield

        cm = func()
        __unit__.ensure_contextmanager(cm)

