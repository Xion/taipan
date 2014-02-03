"""
Tests for .objective.__init__ module.
"""
from taipan.testing import TestCase

import taipan.objective as __unit__


class IsInternal(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.is_internal(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.is_internal(object())

    def test_string__empty(self):
        self.assertFalse(__unit__.is_internal(''))

    def test_string__public_identifiers(self):
        self.assertFalse(__unit__.is_internal('foo'))
        self.assertFalse(__unit__.is_internal('Bar'))
        self.assertFalse(__unit__.is_internal('foo_bar'))
        self.assertFalse(__unit__.is_internal('FooBar'))

    def test_string__internal_identifiers(self):
        self.assertTrue(__unit__.is_internal('_foo'))
        self.assertTrue(__unit__.is_internal('_Bar'))
        self.assertTrue(__unit__.is_internal('_foo_bar'))
        self.assertTrue(__unit__.is_internal('_FooBar'))

    def test_string__magic_identifiers(self):
        self.assertFalse(__unit__.is_internal('__foo__'))
        self.assertFalse(__unit__.is_internal('__Bar__'))
        self.assertFalse(__unit__.is_internal('__foo_bar__'))
        self.assertFalse(__unit__.is_internal('__FooBar__'))

    def test_method__public(self):
        class Class(object):
            def foo(self):
                pass
            def Bar(self):
                pass
            def foo_bar(self):
                pass
            def FooBar(self):
                pass
        self.assertFalse(__unit__.is_internal(Class.foo))
        self.assertFalse(__unit__.is_internal(Class.Bar))
        self.assertFalse(__unit__.is_internal(Class.foo_bar))
        self.assertFalse(__unit__.is_internal(Class.FooBar))

    def test_method__internal(self):
        class Class(object):
            def _foo(self):
                pass
            def _Bar(self):
                pass
            def _foo_bar(self):
                pass
            def _FooBar(self):
                pass
        self.assertTrue(__unit__.is_internal(Class._foo))
        self.assertTrue(__unit__.is_internal(Class._Bar))
        self.assertTrue(__unit__.is_internal(Class._foo_bar))
        self.assertTrue(__unit__.is_internal(Class._FooBar))

    def test_method__magic(self):
        class Class(object):
            def __foo__(self):
                pass
            def __Bar__(self):
                pass
            def __foo_bar__(self):
                pass
            def __FooBar__(self):
                pass
        self.assertFalse(__unit__.is_internal(Class.__foo__))
        self.assertFalse(__unit__.is_internal(Class.__Bar__))
        self.assertFalse(__unit__.is_internal(Class.__foo_bar__))
        self.assertFalse(__unit__.is_internal(Class.__FooBar__))


class IsMagic(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.is_magic(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.is_magic(object())

    def test_string__empty(self):
        self.assertFalse(__unit__.is_magic(''))

    def test_string__public_identifiers(self):
        self.assertFalse(__unit__.is_magic('foo'))
        self.assertFalse(__unit__.is_magic('Bar'))
        self.assertFalse(__unit__.is_magic('foo_bar'))
        self.assertFalse(__unit__.is_magic('FooBar'))

    def test_string__internal_identifiers(self):
        self.assertFalse(__unit__.is_magic('_foo'))
        self.assertFalse(__unit__.is_magic('_Bar'))
        self.assertFalse(__unit__.is_magic('_foo_bar'))
        self.assertFalse(__unit__.is_magic('_FooBar'))

    def test_string__magic_identifiers(self):
        self.assertTrue(__unit__.is_magic('__foo__'))
        self.assertTrue(__unit__.is_magic('__Bar__'))
        self.assertTrue(__unit__.is_magic('__foo_bar__'))
        self.assertTrue(__unit__.is_magic('__FooBar__'))

    def test_method__public(self):
        class Class(object):
            def foo(self):
                pass
            def Bar(self):
                pass
            def foo_bar(self):
                pass
            def FooBar(self):
                pass
        self.assertFalse(__unit__.is_magic(Class.foo))
        self.assertFalse(__unit__.is_magic(Class.Bar))
        self.assertFalse(__unit__.is_magic(Class.foo_bar))
        self.assertFalse(__unit__.is_magic(Class.FooBar))

    def test_method__internal(self):
        class Class(object):
            def _foo(self):
                pass
            def _Bar(self):
                pass
            def _foo_bar(self):
                pass
            def _FooBar(self):
                pass
        self.assertFalse(__unit__.is_magic(Class._foo))
        self.assertFalse(__unit__.is_magic(Class._Bar))
        self.assertFalse(__unit__.is_magic(Class._foo_bar))
        self.assertFalse(__unit__.is_magic(Class._FooBar))

    def test_method__magic(self):
        class Class(object):
            def __foo__(self):
                pass
            def __Bar__(self):
                pass
            def __foo_bar__(self):
                pass
            def __FooBar__(self):
                pass
        self.assertTrue(__unit__.is_magic(Class.__foo__))
        self.assertTrue(__unit__.is_magic(Class.__Bar__))
        self.assertTrue(__unit__.is_magic(Class.__foo_bar__))
        self.assertTrue(__unit__.is_magic(Class.__FooBar__))


# TODO(xion): write tests for utility functions defined in objective.__init__
