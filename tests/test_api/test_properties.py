"""
Tests for .api.properties module.
"""
from taipan.testing import TestCase

import taipan.api.properties as __unit__


class _Property(TestCase):
    VALUE = 42


class ObjectProperty(_Property):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.objectproperty(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.objectproperty(object())

    def test_class(self):
        with self.assertRaises(TypeError):
            @__unit__.objectproperty
            class Foo(object):
                pass

    def test_method__incorrectly_with_args(self):
        with self.assertRaises(TypeError):
            class Foo(object):
                @__unit__.objectproperty
                def foo(self):
                    pass

    def test_method__locals__just_get(self):
        class Foo(object):
            @__unit__.objectproperty
            def foo():
                def get(self):
                    return ObjectProperty.VALUE

        self.assertEquals(ObjectProperty.VALUE, Foo().foo)

    def test_method__locals__get_and_set(self):
        class Foo(object):
            @__unit__.objectproperty
            def foo():
                def get(self):
                    return self._foo
                def set(self, value):
                    self._foo = value

        obj = Foo()
        obj.foo = ObjectProperty.VALUE
        self.assertEquals(ObjectProperty.VALUE, obj.foo)

    def test_method__locals__get_and_del(self):
        class Foo(object):
            @__unit__.objectproperty
            def foo():
                def get(self):
                    if getattr(self, '_deleted', False):
                        raise AttributeError('foo')
                    return ObjectProperty.VALUE
                def del_(self):
                    if getattr(self, '_deleted', False):
                        raise AttributeError('foo')
                    self._deleted = True

        obj = Foo()
        self.assertEquals(ObjectProperty.VALUE, obj.foo)

        del obj.foo
        with self.assertRaises(AttributeError):
            obj.foo
        with self.assertRaises(AttributeError):
            del obj.foo

    def test_method__locals__all(self):
        class Foo(object):
            @__unit__.objectproperty
            def foo():
                def get(self):
                    return self._foo
                def set(self, value):
                    self._foo = value
                def del_(self):
                    del self._foo

        obj = Foo()
        obj.foo = ObjectProperty.VALUE
        self.assertEquals(ObjectProperty.VALUE, obj.foo)

        del obj.foo
        with self.assertRaises(AttributeError):
            obj.foo
        with self.assertRaises(AttributeError):
            del obj.foo

    def test_method__retval__same_as_locals(self):
        class Foo(object):
            @__unit__.objectproperty
            def foo():
                def get(self):
                    return self._foo
                def set(self, value):
                    self._foo = value
                return locals()

        obj = Foo()
        obj.foo = ObjectProperty.VALUE
        self.assertEquals(ObjectProperty.VALUE, obj.foo)

    def test_method__retval__different_than_locals(self):
        class Foo(object):
            def __init__(self):
                self._foo = 0
            @__unit__.objectproperty
            def foo():
                def get(self):
                    return self._foo
                def set(self, value):
                    self._foo = value
                return {'get': get}  # should take precedence over ``locals()``

        obj = Foo()
        self.assertZero(obj.foo)
        with self.assertRaises(AttributeError):
            obj.foo = ObjectProperty.VALUE


class ClassProperty(_Property):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.classproperty(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.classproperty(object())

    def test_method__no_args(self):
        class Foo(object):
            @__unit__.classproperty
            def FOO():
                return ClassProperty.VALUE

        with self.assertRaises(TypeError):
            Foo.FOO

    def test_method__just_cls_arg(self):
        class Foo(object):
            @__unit__.classproperty
            def FOO(cls):
                return ClassProperty.VALUE

        self.assertEquals(ClassProperty.VALUE, Foo.FOO)

    def test_method__too_many_args(self):
        class Foo(object):
            @__unit__.classproperty
            def FOO(cls, a):
                return ClassProperty.VALUE

        with self.assertRaises(TypeError):
            Foo.FOO
