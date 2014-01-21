"""
Tests for the .objective module.
"""
from taipan._compat import IS_PY3
from taipan.testing import TestCase, skipIf, skipUnless

import taipan.objective as __unit__


class IsMethod(TestCase):

    def test_none(self):
        self.assertFalse(__unit__.is_method(None))

    def test_some_object(self):
        self.assertFalse(__unit__.is_method(object()))

    def test_lambda(self):
        foo = lambda: None
        self.assertFalse(__unit__.is_method(foo))

    def test_regular_function(self):
        def foo():
            pass
        self.assertFalse(__unit__.is_method(foo))

    def test_staticmethod(self):
        class Foo(object):
            @staticmethod
            def foo():
                pass
        self.assertFalse(__unit__.is_method(Foo.foo))

    def test_classmethod__of_class(self):
        class Foo(object):
            @classmethod
            def foo(cls):
                pass
        self.assertTrue(__unit__.is_method(Foo.foo))

    def test_classmethod__of_instance(self):
        class Foo(object):
            @classmethod
            def foo(cls):
                pass
        self.assertTrue(__unit__.is_method(Foo().foo))

    def test_regular_method__of_class(self):
        class Foo(object):
            def foo(self):
                pass
        self.assertTrue(__unit__.is_method(Foo.foo))

    def test_regular_method__of_instance(self):
        class Foo(object):
            def foo(self):
                pass
        self.assertTrue(__unit__.is_method(Foo().foo))

    def test_classmethod_attached_to_class(self):
        class Foo(object):
            pass
        @classmethod
        def foo(cls):
            pass
        Foo.foo = foo

        self.assertTrue(__unit__.is_method(Foo.foo))

    def test_regular_method_attached_to_class__of_class(self):
        class Foo(object):
            pass
        def foo(self):
            pass
        Foo.foo = foo

        self.assertTrue(__unit__.is_method(Foo.foo))

    def test_regular_method_attached_to_class__of_instance(self):
        class Foo(object):
            pass
        def foo(self):
            pass
        Foo.foo = foo

        self.assertTrue(__unit__.is_method(Foo().foo))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_function_attached_to_object__py2(self):
        class Foo(object):
            pass
        def foo(self):
            pass

        obj = Foo()
        obj.foo = foo
        self.assertFalse(__unit__.is_method(obj.foo))

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_function_attached_to_object__py3(self):
        class Foo(object):
            pass
        def foo(self):
            pass

        obj = Foo()
        obj.foo = foo
        self.assertTrue(__unit__.is_method(obj.foo))
