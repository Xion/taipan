"""
Tests for the .functional.functions module.
"""
from collections import namedtuple

from taipan.testing import TestCase

import taipan.functional.functions as __unit__


# Constant functions

class _ConstantFunction(TestCase):
    EMPTY_TUPLE = ()

    EMPTY_LIST = []
    DIFFERENT_EMPTY_LIST = []
    LIST = list(range(5))
    LIST_COPY = list(LIST)

    EMPTY_DICT = {}
    DIFFERENT_EMPTY_DICT = {}
    DICT = dict(zip('abcde', range(5)))
    DICT_COPY = dict(DICT)

    OBJECT = object()
    DIFFERENT_OBJECT = object()


class Identity(_ConstantFunction):

    def test_values(self):
        identity = __unit__.identity()
        self.assertIsNone(identity(None))
        self.assertIs(0, identity(0))
        self.assertIs(self.EMPTY_TUPLE, identity(self.EMPTY_TUPLE))

    def test_empty_lists(self):
        identity = __unit__.identity()
        self.assertIs(self.EMPTY_LIST, identity(self.EMPTY_LIST))
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, identity(self.EMPTY_LIST))

    def test_lists(self):
        identity = __unit__.identity()
        self.assertIs(self.LIST, identity(self.LIST))
        self.assertIsNot(self.LIST_COPY, identity(self.LIST))

    def test_empty_dicts(self):
        identity = __unit__.identity()
        self.assertIs(self.EMPTY_DICT, identity(self.EMPTY_DICT))
        self.assertIsNot(self.DIFFERENT_EMPTY_DICT, identity(self.EMPTY_DICT))

    def test_dicts(self):
        identity = __unit__.identity()
        self.assertIs(self.DICT, identity(self.DICT))
        self.assertIsNot(self.DICT_COPY, identity(self.DICT))

    def test_object(self):
        identity = __unit__.identity()
        self.assertIs(self.OBJECT, identity(self.OBJECT))
        self.assertIsNot(self.DIFFERENT_OBJECT, identity(self.OBJECT))


class Const(_ConstantFunction):

    def test_values(self):
        self.assertIsNone(__unit__.const(None)())
        self.assertIs(0, __unit__.const(0)())
        self.assertIs(self.EMPTY_TUPLE, __unit__.const(self.EMPTY_TUPLE)())

    def test_empty_lists(self):
        empty_list = __unit__.const(self.EMPTY_LIST)
        self.assertIs(self.EMPTY_LIST, empty_list())
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, empty_list())

    def test_lists(self):
        list_ = __unit__.const(self.LIST)
        self.assertIs(self.LIST, list_())
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, list_())

    def test_empty_dicts(self):
        empty_dict = __unit__.const(self.EMPTY_DICT)
        self.assertIs(self.EMPTY_DICT, empty_dict())
        self.assertIsNot(self.DIFFERENT_EMPTY_DICT, empty_dict())

    def test_dicts(self):
        dict_ = __unit__.const(self.DICT)
        self.assertIs(self.DICT, dict_())
        self.assertIsNot(self.DICT_COPY, dict_())

    def test_object(self):
        object_ = __unit__.const(self.OBJECT)
        self.assertIs(self.OBJECT, object_())
        self.assertIsNot(self.DIFFERENT_OBJECT, object_())


class PredefinedConstantFunctions(_ConstantFunction):

    def test_true(self):
        self._assertConstantFunction(__unit__.true(), self.assertTrue)

    def test_false(self):
        self._assertConstantFunction(__unit__.false(), self.assertFalse)

    def test_none(self):
        self._assertConstantFunction(__unit__.none(), self.assertIsNone)

    def test_zero(self):
        self._assertConstantFunction(__unit__.zero(), self.assertZero)

    def test_one(self):
        self._assertConstantFunction(__unit__.one(),
                                     lambda res: self.assertEquals(1, res))

    def test_empty(self):
        self._assertConstantFunction(__unit__.empty(), self.assertEmpty)

    # Utility functions

    def _assertConstantFunction(self, func, assertion):
        assertion(func())
        assertion(func("extraneous positional argument"))
        assertion(func(foo="extraneous keyword argument"))
        assertion(func("extraneous positional argument",
                       foo="extraneous keyword argument"))


# Unary functions

class AttrFunc(TestCase):
    CLASS = namedtuple('Foo', ['foo', 'bar'])

    SINGLE_NESTED_OBJECT = CLASS(foo=1, bar='baz')
    DOUBLY_NESTED_OBJECT = CLASS(foo=CLASS(foo=1, bar=2), bar='a')

    DEFAULT = 42

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func(object())

    def test_single_attr__good(self):
        func = __unit__.attr_func('foo')
        self.assertEquals(
            self.SINGLE_NESTED_OBJECT.foo, func(self.SINGLE_NESTED_OBJECT))
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo, func(self.DOUBLY_NESTED_OBJECT))

    def test_single_attr__bad(self):
        func = __unit__.attr_func('doesnt_exist')
        with self.assertRaises(AttributeError):
            func(self.SINGLE_NESTED_OBJECT)
        with self.assertRaises(AttributeError):
            func(self.DOUBLY_NESTED_OBJECT)

    def test_single_attr__with_dot(self):
        func = __unit__.attr_func('foo.bar')
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo.bar, func(self.DOUBLY_NESTED_OBJECT))

    def test_two_attrs__good(self):
        func = __unit__.attr_func('foo', 'bar')
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo.bar, func(self.DOUBLY_NESTED_OBJECT))

    def test_two_attrs__bad(self):
        func = __unit__.attr_func('doesnt_exist', 'foo')
        with self.assertRaises(AttributeError):
            func(self.DOUBLY_NESTED_OBJECT)

    def test_single_attr__good__with_default(self):
        func = __unit__.attr_func('foo', default=self.DEFAULT)
        self.assertEquals(
            self.SINGLE_NESTED_OBJECT.foo, func(self.SINGLE_NESTED_OBJECT))
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo, func(self.DOUBLY_NESTED_OBJECT))

    def test_single_attr__bad__with_default(self):
        func = __unit__.attr_func('doesnt_exist', default=self.DEFAULT)
        self.assertEquals(self.DEFAULT, func(self.SINGLE_NESTED_OBJECT))
        self.assertEquals(self.DEFAULT, func(self.DOUBLY_NESTED_OBJECT))

    def test_two_attrs__good__with_default(self):
        func = __unit__.attr_func('foo', 'bar', default=self.DEFAULT)
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo.bar, func(self.DOUBLY_NESTED_OBJECT))

    def test_two_attrs__bad__with_default(self):
        func = __unit__.attr_func('foo', 'doesnt_exist', default=self.DEFAULT)
        self.assertEquals(self.DEFAULT, func(self.DOUBLY_NESTED_OBJECT))


class KeyFunc(TestCase):
    SINGLY_NESTED_DICT = dict(foo=1, bar='baz')
    DOUBLY_NESTED_DICT = dict(foo=dict(foo=1, bar=2), bar='a')

    DEFAULT = 42

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.key_func()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.key_func(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.key_func(object())

    def test_single_key__good(self):
        func = __unit__.key_func('foo')
        self.assertEquals(
            self.SINGLY_NESTED_DICT['foo'], func(self.SINGLY_NESTED_DICT))
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo'], func(self.DOUBLY_NESTED_DICT))

    def test_single_key__bad(self):
        func = __unit__.key_func('doesnt_exist')
        with self.assertRaises(LookupError):
            func(self.SINGLY_NESTED_DICT)
        with self.assertRaises(LookupError):
            func(self.DOUBLY_NESTED_DICT)

    def test_two_keys__good(self):
        func = __unit__.key_func('foo', 'bar')
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo']['bar'],
            func(self.DOUBLY_NESTED_DICT))

    def test_two_keys__bad(self):
        func = __unit__.key_func('doesnt_exist', 'foo')
        with self.assertRaises(LookupError):
            func(self.DOUBLY_NESTED_DICT)

    def test_single_key__good__with_default(self):
        func = __unit__.key_func('foo', default=self.DEFAULT)
        self.assertEquals(
            self.SINGLY_NESTED_DICT['foo'], func(self.SINGLY_NESTED_DICT))
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo'], func(self.DOUBLY_NESTED_DICT))

    def test_single_key__bad__with_default(self):
        func = __unit__.key_func('doesnt_exist', default=self.DEFAULT)
        self.assertEquals(self.DEFAULT, func(self.SINGLY_NESTED_DICT))
        self.assertEquals(self.DEFAULT, func(self.DOUBLY_NESTED_DICT))

    def test_two_keys__good__with_default(self):
        func = __unit__.key_func('foo', 'bar', default=self.DEFAULT)
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo']['bar'],
            func(self.DOUBLY_NESTED_DICT))

    def test_two_keys__bad__with_default(self):
        func = __unit__.key_func('foo', 'doesnt_exist', default=self.DEFAULT)
        self.assertEquals(self.DEFAULT, func(self.DOUBLY_NESTED_DICT))


class Dotcall(TestCase):
    INSTANCE_RETURN_VALUE = 42
    CLASS_RETURN_VALUE = 13

    ARGUMENT = 'foobar'

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.dotcall()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.dotcall(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.dotcall(object())

    def test_string__no_args__class_instance(self):
        call = __unit__.dotcall('foo')
        instance = self._create_class_instance()
        self.assertEquals(Dotcall.INSTANCE_RETURN_VALUE, call(instance))

    def test_string__no_args__class(self):
        call = __unit__.dotcall('bar')
        class_ = self._create_class()
        self.assertEquals(Dotcall.CLASS_RETURN_VALUE, call(class_))

    def test_string__no_args__module(self):
        call = __unit__.dotcall(__unit__.true.__name__)
        self.assertResultsEqual(__unit__.true(), call(__unit__))

    def test_string__with_args__class_instance(self):
        call = __unit__.dotcall('baz', self.ARGUMENT)
        instance = self._create_class_instance()
        self.assertEquals(self.ARGUMENT, call(instance))

    def test_string__with_args__class(self):
        call = __unit__.dotcall('qux', self.ARGUMENT)
        class_ = self._create_class()
        self.assertEquals(self.ARGUMENT, call(class_))

    def test_string__with_args__module(self):
        call = __unit__.dotcall(__unit__.const.__name__, self.ARGUMENT)
        self.assertResultsEqual(__unit__.const(self.ARGUMENT), call(__unit__))

    # Utility function

    def _create_class(self):
        class Class(object):
            def foo(self):
                return Dotcall.INSTANCE_RETURN_VALUE
            @classmethod
            def bar(cls):
                return Dotcall.CLASS_RETURN_VALUE
            def baz(self, arg):
                return arg
            @classmethod
            def qux(cls, arg):
                return arg

        return Class

    def _create_class_instance(self):
        Class = self._create_class()
        return Class()
