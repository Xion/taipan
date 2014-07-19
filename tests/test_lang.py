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


# Language token classification

class HasIdentifierForm(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.has_identifier_form(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.has_identifier_form(object())

    def test_string__empty(self):
        self.assertFalse(__unit__.has_identifier_form(''))

    def test_string__number(self):
        self.assertFalse(__unit__.has_identifier_form('42'))

    def test_string__number_prefix(self):
        self.assertFalse(__unit__.has_identifier_form('42foo'))

    def test_string__underscore_prefix(self):
        self.assertTrue(__unit__.has_identifier_form('_42'))

    def test_string__letters(self):
        self.assertTrue(__unit__.has_identifier_form('foo'))

    def test_string__camel_case(self):
        self.assertTrue(__unit__.has_identifier_form('FooBar'))
        self.assertTrue(__unit__.has_identifier_form('fooBar'))

    def test_string__snake_case(self):
        self.assertTrue(__unit__.has_identifier_form('foo_bar'))


class IsIdentifier(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.is_identifier(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.is_identifier(object())

    def test_string__empty(self):
        self.assertFalse(__unit__.is_identifier(''))

    def test_string__number(self):
        self.assertFalse(__unit__.is_identifier('42'))

    def test_string__number_prefix(self):
        self.assertFalse(__unit__.is_identifier('42foo'))

    def test_string__underscore_prefix(self):
        self.assertTrue(__unit__.is_identifier('_42'))

    def test_string__letters(self):
        self.assertTrue(__unit__.is_identifier('FooBar'))
        self.assertTrue(__unit__.is_identifier('fooBar'))

    def test_string__snake_case(self):
        self.assertTrue(__unit__.is_identifier('foo_bar'))

    def test_string__keyword(self):
        self.assertFalse(__unit__.is_identifier('if'))
        self.assertFalse(__unit__.is_identifier('for'))
        self.assertFalse(__unit__.is_identifier('from'))
        self.assertFalse(__unit__.is_identifier('yield'))
        self.assertFalse(__unit__.is_identifier('return'))
        self.assertFalse(__unit__.is_identifier('finally'))

    def test_string__self(self):
        self.assertTrue(__unit__.is_identifier('self'))

    def test_string__global_constants(self):
        self.assertTrue(__unit__.is_identifier('True'))
        self.assertTrue(__unit__.is_identifier('False'))
        self.assertFalse(__unit__.is_identifier('None'))  # can't assign to it


class IsMagic(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.is_magic(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.is_magic(object())

    def test_string__empty(self):
        self.assertFalse(__unit__.is_magic(''))

    def test_string__number(self):
        self.assertFalse(__unit__.is_magic('42'))

    def test_string__just_letters(self):
        self.assertFalse(__unit__.is_magic('FooBar'))
        self.assertFalse(__unit__.is_magic('fooBar'))

    def test_string__underscore_prefix(self):
        self.assertFalse(__unit__.is_magic('_foo'))
        self.assertFalse(__unit__.is_magic('_Foo'))

    def test_string__double_underscore_prefix(self):
        self.assertFalse(__unit__.is_magic('__foo'))
        self.assertFalse(__unit__.is_magic('__Foo'))

    def test_string__underscore_suffix(self):
        self.assertFalse(__unit__.is_magic('foo_'))

    def test_string__single_underscore(self):
        self.assertFalse(__unit__.is_magic('_'))

    def test_string__two_underscores(self):
        self.assertFalse(__unit__.is_magic('__'))

    def test_string__four_underscores(self):
        self.assertFalse(__unit__.is_magic('____'))

    def test_string__magic(self):
        self.assertTrue(__unit__.is_magic('__foo__'))
        self.assertTrue(__unit__.is_magic('__FooBar__'))
