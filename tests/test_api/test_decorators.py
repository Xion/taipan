"""
Tests for the .api.decorators module.
"""
from taipan.testing import TestCase

import taipan.api.decorators as __unit__


class _Decorator(TestCase):
    """Base class for @*decorator test cases."""
    DECORATOR_ARG = 42

    def setUp(self):
        self.fail("setUp() must be overriden in derived testcases")

    def _assertIsDecorated(self, obj, arg=None):
        self.assertHasAttr('__decorated__', obj)
        self.assertTrue(obj.__decorated__)
        if arg is not None:
            self.assertHasAttr('__decorator_arg__', obj)
            self.assertEquals(arg, obj.__decorator_arg__)

    def _create_argless_decorator_function(self):
        @self.decorator_under_test
        def decorator():
            def wrapper(f):
                f.__decorated__ = True
                return f
            return wrapper
        return decorator

    def _create_decorator_function_with_args(self):
        @self.decorator_under_test
        def decorator(arg):
            def wrapper(f):
                f.__decorated__ = True
                f.__decorator_arg__ = arg
                return f
            return wrapper
        return decorator

    def _create_argless_decorator_class(self):
        @self.decorator_under_test
        class Decorator(object):
            def __call__(self, f):
                f.__decorated__ = True
                return f
        return Decorator

    def _create_decorator_class_with_args(self):
        @self.decorator_under_test
        class Decorator(object):
            def __init__(self, arg):
                self.arg = arg
            def __call__(self, f):
                f.__decorated__ = True
                f.__decorator_arg__ = self.arg
                return f
        return Decorator


class _FunctionDecorator(_Decorator):
    """Tests for @function_decorator."""

    def setUp(self):
        self.decorator_under_test = __unit__.function_decorator

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
        self._assertIsDecorated(foo)
        self._assertIsDecorated(bar)

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
        self._assertIsDecorated(foo, self.DECORATOR_ARG)

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

    def test_decorator_class__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_class()
        @decorator
        def foo():
            pass
        @decorator()
        def bar():
            pass
        self._assertIsDecorated(foo)
        self._assertIsDecorated(bar)

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
        self._assertIsDecorated(foo, self.DECORATOR_ARG)

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


class ClassDecorator(_Decorator):
    """Tests for @class_decorator."""

    def setUp(self):
        self.decorator_under_test = __unit__.class_decorator

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.class_decorator(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.class_decorator(object())

    def test_decorator_function__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_function()
        with self.assertRaises(TypeError):
            @decorator
            def foo():
                pass
        with self.assertRaises(TypeError):
            @decorator()
            def bar():
                pass

    def test_decorator_function__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_function()
        @decorator
        class Foo(object):
            pass
        @decorator()
        class Bar(object):
            pass
        self._assertIsDecorated(Foo)
        self._assertIsDecorated(Bar)

    def test_decorator_function__with_args__apply_to_function(self):
        decorator = self._create_decorator_function_with_args()
        with self.assertRaises(TypeError):
            @decorator(self.DECORATOR_ARG)
            def foo():
                pass

    def test_decorator_function__with_args__apply_to_class(self):
        decorator = self._create_decorator_function_with_args()
        @decorator(self.DECORATOR_ARG)
        class Foo(object):
            pass
        self._assertIsDecorated(Foo, self.DECORATOR_ARG)

    def test_decorator_function__with_args__apply_to_class__badly(self):
        decorator = self._create_decorator_function_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator
            class Foo(object):
                pass

    def test_decorator_class__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_class()
        with self.assertRaises(TypeError):
            @decorator
            def foo():
                pass
        with self.assertRaises(TypeError):
            @decorator()
            def bar():
                pass

    def test_decorator_class__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_class()
        @decorator
        class Foo(object):
            pass
        @decorator()
        class Bar(object):
            pass
        self._assertIsDecorated(Foo)
        self._assertIsDecorated(Bar)

    def test_decorator_class__with_args__apply_to_function(self):
        decorator = self._create_decorator_class_with_args()
        with self.assertRaises(TypeError):
            @decorator(self.DECORATOR_ARG)
            def foo():
                pass

    def test_decorator_class__with_args__apply_to_class(self):
        decorator = self._create_decorator_class_with_args()
        @decorator(self.DECORATOR_ARG)
        class Foo(object):
            pass
        self._assertIsDecorated(Foo, self.DECORATOR_ARG)

    def test_decorator_class__with_args__apply_to_class__badly(self):
        decorator = self._create_decorator_class_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator
            class Foo(object):
                pass


class Decorator(_Decorator):
    """Tests for @decorator."""

    def setUp(self):
        self.decorator_under_test = __unit__.decorator

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.decorator(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.decorator(object())

    def test_decorator_function__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_function()
        @decorator
        def foo():
            pass
        @decorator()
        def bar():
            pass
        self._assertIsDecorated(foo)
        self._assertIsDecorated(bar)

    def test_decorator_function__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_function()
        @decorator
        class Foo(object):
            pass
        @decorator()
        class Bar(object):
            pass
        self._assertIsDecorated(Foo)
        self._assertIsDecorated(Bar)

    def test_decorator_function__with_args__apply_to_function(self):
        decorator = self._create_decorator_function_with_args()
        @decorator(self.DECORATOR_ARG)
        def foo():
            pass
        self._assertIsDecorated(foo, self.DECORATOR_ARG)

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
        @decorator(self.DECORATOR_ARG)
        class Foo(object):
            pass
        self._assertIsDecorated(Foo, self.DECORATOR_ARG)

    def test_decorator_function__with_args__apply_to_class__badly(self):
        decorator = self._create_decorator_function_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator
            class Bar(object):
                pass

    def test_decorator_class__no_args__apply_to_function(self):
        decorator = self._create_argless_decorator_class()
        @decorator
        def foo():
            pass
        @decorator()
        def bar():
            pass
        self._assertIsDecorated(foo)
        self._assertIsDecorated(bar)

    def test_decorator_class__no_args__apply_to_class(self):
        decorator = self._create_argless_decorator_class()
        @decorator
        class Foo(object):
            pass
        @decorator()
        class Bar(object):
            pass
        self._assertIsDecorated(Foo)
        self._assertIsDecorated(Bar)

    def test_decorator_class__with_args__apply_to_function(self):
        decorator = self._create_decorator_class_with_args()
        @decorator(self.DECORATOR_ARG)
        def foo():
            pass
        self._assertIsDecorated(foo)

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
        @decorator(self.DECORATOR_ARG)
        class Foo(object):
            pass
        self._assertIsDecorated(Foo, self.DECORATOR_ARG)

    def test_decorator_class__with_args__apply_to_class__badly(self):
        decorator = self._create_decorator_class_with_args()
        with self.assertRaises(TypeError):
            @decorator()
            class Foo(object):
                pass
        with self.assertRaises(TypeError):
            @decorator
            class Bar(object):
                pass
