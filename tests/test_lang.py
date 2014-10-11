"""
Tests for .lang module.
"""
from contextlib import contextmanager

from taipan._compat import IS_PY3
from taipan.testing import TestCase, skipIf, skipUnless

import taipan.lang as __unit__


class Cast(TestCase):
    NUMBER_TYPE = int

    VALID_NUMBER_VALUE = '42'
    CASTED_NUMBER_VALUE = 42

    INVALID_NUMBER_VALUE = 'foo'
    DEFAULT_NUMBER_VALUE =  0

    INVALID_COLLECTION = 42

    def test_type__none(self):
        with self.assertRaises(AssertionError):
            __unit__.cast(None, self.VALID_NUMBER_VALUE)

    def test_type__some_object(self):
        with self.assertRaises(AssertionError):
            __unit__.cast(object(), self.VALID_NUMBER_VALUE)

    def test_type__numeric__valid_cast(self):
        self.assertEquals(
            self.CASTED_NUMBER_VALUE,
            __unit__.cast(self.NUMBER_TYPE, self.VALID_NUMBER_VALUE))

    def test_type__numeric__invalid_cast__sans_default(self):
        with self.assertRaises(TypeError):
            __unit__.cast(self.NUMBER_TYPE, self.INVALID_NUMBER_VALUE)

    def test_type__numeric__invalid_cast__with_default__positional(self):
        self.assertEquals(
            self.DEFAULT_NUMBER_VALUE,
            __unit__.cast(self.NUMBER_TYPE, self.INVALID_NUMBER_VALUE,
                          self.DEFAULT_NUMBER_VALUE))

    def test_type__numeric__invalid_cast__with_default__keyword(self):
        self.assertEquals(
            self.CASTED_NUMBER_VALUE,
            __unit__.cast(self.NUMBER_TYPE, self.VALID_NUMBER_VALUE,
                          default=self.DEFAULT_NUMBER_VALUE))

    def test_type__collections__invalid_cast__with_default(self):
        self.assertEquals((), __unit__.cast(tuple, self.INVALID_COLLECTION, ()))
        self.assertEquals([], __unit__.cast(list, self.INVALID_COLLECTION, []))
        self.assertEquals({}, __unit__.cast(dict, self.INVALID_COLLECTION, {}))


# Kind checks and assertion

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


class IsNumber(TestCase):

    def test_none(self):
        self.assertFalse(__unit__.is_number(None))

    def test_some_object(self):
        self.assertFalse(__unit__.is_number(object()))

    def test_string(self):
        self.assertFalse(__unit__.is_number(''))

    def test_int__ctor(self):
        self.assertTrue(__unit__.is_number(int()))

    def test_int__literal(self):
        self.assertTrue(__unit__.is_number(42))

    def test_int__type(self):
        self.assertFalse(__unit__.is_number(int))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__ctor(self):
        self.assertTrue(__unit__.is_number(long()))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__literal(self):
        self.assertTrue(__unit__.is_number(eval('42L')))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__type(self):
        self.assertFalse(__unit__.is_number(long))

    def test_float__ctor(self):
        self.assertTrue(__unit__.is_number(float()))

    def test_float__literal(self):
        self.assertTrue(__unit__.is_number(42.0))

    def test_float__type(self):
        self.assertFalse(__unit__.is_number(float))

    def test_complex__ctor(self):
        self.assertTrue(__unit__.is_number(complex()))

    def test_complex__type(self):
        self.assertFalse(__unit__.is_number(complex))


class EnsureBoolean(TestCase):
    # These will be always True/False, even if True, False or even bool
    # symbols have been overwritten
    SAFE_TRUE = 0 == 0
    SAFE_FALSE = 0 == 1

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_boolean(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_boolean(object())

    def test_true(self):
        __unit__.ensure_boolean(self.SAFE_TRUE)
        __unit__.ensure_boolean(not bool())
        __unit__.ensure_boolean(True)

    def test_false(self):
        __unit__.ensure_boolean(self.SAFE_FALSE)
        __unit__.ensure_boolean(bool())
        __unit__.ensure_boolean(False)

    def test_bool_type(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_boolean(bool)

    def test_truthy(self):
        for val in (1, 'True', (42,)):
            with self.assertRaises(TypeError):
                __unit__.ensure_boolean(val)

    def test_falsy(self):
        for val in (0, '', (), [], {}):
            with self.assertRaises(TypeError):
                __unit__.ensure_boolean(val)


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


class EnsureNumber(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(object())

    def test_string(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number('')

    def test_int__ctor(self):
        __unit__.ensure_number(int())

    def test_int__literal(self):
        __unit__.ensure_number(42)

    def test_int__type(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(int)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__ctor(self):
        __unit__.ensure_number(long())

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__literal(self):
        __unit__.ensure_number(eval('42L'))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long__type(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(long)

    def test_float__ctor(self):
        __unit__.ensure_number(float())

    def test_float__literal(self):
        __unit__.ensure_number(42.0)

    def test_float__type(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(float)

    def test_complex__ctor(self):
        __unit__.ensure_number(complex())

    def test_complex__type(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_number(complex)


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

    def test_string__with_whitespace(self):
        self.assertFalse(__unit__.has_identifier_form('foo bar'))
        self.assertFalse(__unit__.has_identifier_form('foo\tbar'))

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

    def test_string__with_whitespace(self):
        self.assertFalse(__unit__.is_identifier('foo bar'))
        self.assertFalse(__unit__.is_identifier('foo\tbar'))

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

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_string__global_constants__py2(self):
        self.assertTrue(__unit__.is_identifier('True'))
        self.assertTrue(__unit__.is_identifier('False'))
        self.assertFalse(__unit__.is_identifier('None'))  # can't assign to it

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_string__global_constants__py3(self):
        self.assertFalse(__unit__.is_identifier('True'))  # keyword in py3
        self.assertFalse(__unit__.is_identifier('False'))  # keyword in py3
        self.assertFalse(__unit__.is_identifier('None'))  # keyword in py3


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
