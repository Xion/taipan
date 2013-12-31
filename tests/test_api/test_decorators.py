"""
Tests for the .api.decorators module.
"""
import functools
import inspect

from taipan.testing import TestCase

import taipan.api.decorators as __unit__


class _FunctionDecorator(TestCase):
    DECORATOR_ARG = 42

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.function_decorator(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.function_decorator(object())

    def test_decorator_function__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_function()
        @decorator
        def foo():
            pass
        @decorator()
        def bar():
            pass
        self.assertTrue(foo.__decorated__)
        self.assertTrue(bar.__decorated__)

    def test_decorator_function__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_function()
        with self.assertRaises(TypeError):
            @decorator
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator()
            class Bar(object):
                pass

    def test_decorator_function__with_args__apply_to_function(self):
        decorator = self._create_decorator_function_with_args()
        @decorator(self.DECORATOR_ARG)
        def foo():
            pass
        self.assertTrue(foo.__decorated__)
        self.assertEquals(self.DECORATOR_ARG, foo.__decorator_arg__)

    def test_decorator_function__with_args__apply_to_function__badly(self):
        decorator = self._create_decorator_function_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            def foo():
                pass
        with self.assertRaises(TypeError):
            @decorator
            def bar():
                pass

    def test_decorator_function__with_args__apply_to_class(self):
        decorator = self._create_decorator_function_with_args()
        with self.assertRaises(TypeError):
            @decorator(self.DECORATOR_ARG)
            class Foo(object):
                pass

    def test_decorator_class__no_args(self):
        decorator = self._create_argless_decorator_class()
        @decorator
        def foo():
            pass
        @decorator()
        def bar():
            pass
        self.assertTrue(foo.__decorated__)
        self.assertTrue(bar.__decorated__)

    def test_deorator_class__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_class()
        with self.assertRaises(TypeError):
            @decorator
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator()
            class Bar(object):
                pass

    def test_decorator_class__with_args__apply_to_function(self):
        decorator = self._create_decorator_class_with_args()
        @decorator(self.DECORATOR_ARG)
        def foo():
            pass
        self.assertTrue(foo.__decorated__)
        self.assertEquals(self.DECORATOR_ARG, foo.__decorator_arg__)

    def test_decorator_class__with_args__apply_to_function__badly(self):
        decorator = self._create_decorator_class_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            def foo():
                pass
        with self.assertRaises(TypeError):
            @decorator
            def bar():
                pass

    def test_decorator_class__with_args__apply_to_class(self):
        decorator = self._create_decorator_class_with_args()
        with self.assertRaises(TypeError):
            @decorator(self.DECORATOR_ARG)
            class Foo(object):
                pass

    # Utility functions

    def _create_argless_decorator_function(self):
        @__unit__.function_decorator
        def decorator():
            def wrapper(f):
                self.assertTrue(inspect.isfunction(f))
                f.__decorated__ = True
                return f
            return wrapper
        return decorator

    def _create_decorator_function_with_args(self):
        @__unit__.function_decorator
        def decorator(arg):
            def wrapper(f):
                self.assertTrue(inspect.isfunction(f))
                f.__decorated__ = True
                f.__decorator_arg__ = arg
                return f
            return wrapper
        return decorator

    def _create_argless_decorator_class(self):
        testcase = self  # because shadowing
        @__unit__.function_decorator
        class Decorator(object):
            def __call__(self, f):
                testcase.assertTrue(inspect.isfunction(f))
                f.__decorated__ = True
                return f
        return Decorator

    def _create_decorator_class_with_args(self):
        testcase = self  # because shadowing
        @__unit__.function_decorator
        class Decorator(object):
            def __init__(self, arg):
                self.arg = arg
            def __call__(self, f):
                testcase.assertTrue(inspect.isfunction(f))
                f.__decorated__ = True
                f.__decorator_arg__ = self.arg
                return f
        return Decorator
