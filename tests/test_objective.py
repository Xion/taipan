"""
Tests for the .objective module.
"""
from contextlib import contextmanager
import inspect
import re

from taipan._compat import IS_PY3
from taipan.collections.lists import head, tail
from taipan.testing import TestCase

import taipan.objective as __unit__


# Method-related functions

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

    def test_function_attached_to_object(self):
        class Foo(object):
            pass
        def foo(self):
            pass

        obj = Foo()
        obj.foo = foo
        self.assertTrue(__unit__.is_method(obj.foo))


class EnsureMethod(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_method(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_method(object())

    def test_lambda(self):
        foo = lambda: None
        with self.assertRaises(TypeError):
            __unit__.ensure_method(foo)

    def test_regular_function(self):
        def foo():
            pass
        with self.assertRaises(TypeError):
            __unit__.ensure_method(foo)

    def test_staticmethod(self):
        class Foo(object):
            @staticmethod
            def foo():
                pass
        with self.assertRaises(TypeError):
            __unit__.ensure_method(Foo.foo)

    def test_classmethod__of_class(self):
        class Foo(object):
            @classmethod
            def foo(cls):
                pass
        __unit__.ensure_method(Foo.foo)

    def test_classmethod__of_instance(self):
        class Foo(object):
            @classmethod
            def foo(cls):
                pass
        __unit__.ensure_method(Foo().foo)

    def test_regular_method__of_class(self):
        class Foo(object):
            def foo(self):
                pass
        __unit__.ensure_method(Foo.foo)

    def test_regular_method__of_instance(self):
        class Foo(object):
            def foo(self):
                pass
        __unit__.ensure_method(Foo().foo)

    def test_classmethod_attached_to_class(self):
        class Foo(object):
            pass
        @classmethod
        def foo(cls):
            pass
        Foo.foo = foo

        __unit__.ensure_method(Foo.foo)

    def test_regular_method_attached_to_class__of_class(self):
        class Foo(object):
            pass
        def foo(self):
            pass
        Foo.foo = foo

        __unit__.ensure_method(Foo.foo)

    def test_regular_method_attached_to_class__of_instance(self):
        class Foo(object):
            pass
        def foo(self):
            pass
        Foo.foo = foo

        __unit__.ensure_method(Foo().foo)

    def test_function_attached_to_object(self):
        class Foo(object):
            pass
        def foo(self):
            pass

        obj = Foo()
        obj.foo = foo
        __unit__.ensure_method(obj.foo)


class GetMethods(TestCase):
    """Tests for ``get_methods`` would be only a repetition of what is
    already verified by tests for ``is_method``, so we don't provide any.

    We ensure, however, that this fact doesn't suddenly cease to hold
    by maintaining few spots checks of the properties of ``get_methods``
    _implementation_.
    """
    FUNC = __unit__.get_methods
    CODE = FUNC.__code__

    def test_no_local_variables(self):
        # count the new locals introduced inside function's body, not args
        local_vars_count = self.CODE.co_nlocals - self.CODE.co_argcount
        self.assertZero(local_vars_count)

    def test_no_literal_constants(self):
        # make sure docstring is the only literal constant used in the code
        self.assertEquals(
            __unit__.get_methods.__doc__, head(self.CODE.co_consts))
        self.assertEmpty(tail(self.CODE.co_consts))

    def test_no_nesting(self):
        """Make sure function's code uses no nested control structures."""
        # retrieve the source lines and determine where the docstring ends
        source_lines, _ = inspect.getsourcelines(self.FUNC)
        last_docstring_line_index = next(
            idx for idx, line in enumerate(source_lines)
            if line.rstrip().endswith('"""'))
        code_lines = source_lines[last_docstring_line_index + 1:]
        self.assertGreater(len(code_lines), 0)

        # make sure no code line is indented any further than the first one
        initial_indent = re.search(r'^\s+', source_lines[1]).group(0)
        for line in code_lines:
            self.assertStartsWith(initial_indent, line)
            self.assertIsNone(re.search(r'^\s+', line[len(initial_indent):]))


# Class member checks

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


# Universal base class

# TODO(xion): test how ObjectMetaclass plays with possible other metaclasses
# in the same inheritance chain

class Object(TestCase):

    def test_definition(self):
        # make sure unusual definition of ``Object`` class
        # still has necessary members intact
        self.assertGreater(len(__unit__.Object.__doc__), 0)

    def test_empty_class(self):
        class Foo(__unit__.Object):
            pass
        self.assertIsInstance(Foo, __unit__.ObjectMetaclass)


class Final(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.final(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.final(object())

    def test_function(self):
        with self.assertRaises(TypeError):
            @__unit__.final
            def foo():
                pass

    def test_class__incompatible(self):
        with self.assertRaises(ValueError):
            @__unit__.final
            class Foo(object):
                pass

    def test_class__compatible(self):
        self._create_final_class()

    def test_class__inherit_from_final__single_inheritance(self):
        Foo = self._create_final_class()

        with self._assertRaisesFinalInheritanceException(base=Foo):
            class Bar(Foo):
                pass

    def test_class_inherit_from_final__multiple_inheritance(self):
        FinalBase = self._create_final_class()
        class Foo(object):
            pass

        with self._assertRaisesFinalInheritanceException(base=FinalBase):
            class Bar(Foo, FinalBase):
                pass

    # Utility functions

    def _create_final_class(self):
        @__unit__.final
        class Foo(__unit__.Object):
            pass
        return Foo

    @contextmanager
    def _assertRaisesFinalInheritanceException(self, base):
        with self.assertRaises(__unit__.ClassError) as r:
            yield r

        msg = str(r.exception)
        self.assertIn("cannot inherit", msg)
        self.assertIn(base.__name__, msg)


class Override(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.override(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.override(object())

    def test_class(self):
        with self.assertRaises(TypeError):
            @__unit__.override
            class Foo(object):
                pass

    def test_regular_function(self):
        with self.assertRaises(TypeError):
            @__unit__.override
            def foo():
                pass

    def test_instance_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(__unit__.Object):
                @__unit__.override
                def foo(self):
                    pass

    def test_instance_method__missing(self):
        Base = self._create_objective_class()

        with self._assertRaisesMissingOverrideException():
            class Bar(Base):
                def florb(self):
                    pass

    def test_instance_method__missing__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        # even though the improperly overridden method comes from
        # non-Object-inheriting base class, the presence of
        # other Object-inherting base class should ellicit the error
        with self._assertRaisesMissingOverrideException():
            class Bar(Base, __unit__.Object):
                def florb(self):
                    pass

    def test_instance_method__present(self):
        Base = self._create_objective_class()

        class Bar(Base):
            @__unit__.override
            def florb(self):
                pass

    def test_instance_method__present__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        class Bar(Base, __unit__.Object):
            @__unit__.override
            def florb(self):
                pass

    def test_class_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(__unit__.Object):
                @__unit__.override
                @classmethod
                def class_florb(cls):
                    pass

    def test_class_method__missing(self):
        Base = self._create_objective_class()

        with self._assertRaisesMissingOverrideException():
            class Foo(Base):
                @classmethod
                def class_florb(cls):
                    pass

    def test_class_method__missing__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        # see comment in analogous test case for instance methods
        with self._assertRaisesMissingOverrideException():
            class Foo(Base, __unit__.Object):
                @classmethod
                def class_florb(cls):
                    pass

    def test_class_method__present(self):
        Base = self._create_objective_class()

        class Foo(Base):
            @__unit__.override
            @classmethod
            def class_florb(cls):
                pass

    def test_class_method__present__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        class Foo(Base, __unit__.Object):
            @__unit__.override
            @classmethod
            def class_florb(cls):
                pass

    def test_class_method__present__but_below_classmethod_decorator(self):
        Base = self._create_objective_class()

        with self.assertRaises(TypeError) as r:
            class Foo(Base):
                @classmethod
                @__unit__.override
                def class_florb(cls):
                    pass
        self.assertIn("@classmethod", str(r.exception))

    def test_static_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Baz(__unit__.Object):
                @__unit__.override
                @staticmethod
                def static_florb():
                    pass

    def test_static_method__missing(self):
        Base = self._create_objective_class()

        with self._assertRaisesMissingOverrideException():
            class Baz(Base):
                @staticmethod
                def static_florb():
                    pass

    def test_static_method__missing__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        with self._assertRaisesMissingOverrideException():
            class Baz(Base, __unit__.Object):
                @staticmethod
                def static_florb():
                    pass

    def test_static_method__present(self):
        Base = self._create_objective_class()

        class Baz(Base):
            @__unit__.override
            @staticmethod
            def static_florb():
                pass

    def test_static_method__present__hiding_method_from_regular_base(self):
        Base = self._create_regular_class()

        class Baz(Base, __unit__.Object):
            @__unit__.override
            @staticmethod
            def static_florb():
                pass

    # Utility functions

    def _create_regular_class(self):
        return self._create_class(base=object)

    def _create_objective_class(self):
        return self._create_class(base=__unit__.Object)

    def _create_class(self, base):
        class Class(base):
            def florb(self):
                pass
            @classmethod
            def class_florb(cls):
                pass
            @staticmethod
            def static_florb():
                pass

        return Class

    @contextmanager
    def _assertRaisesUnnecessaryOverrideException(self):
        with self.assertRaises(__unit__.ClassError) as r:
            yield r
        self.assertIn("unnecessary", str(r.exception))

    @contextmanager
    def _assertRaisesMissingOverrideException(self):
        with self.assertRaises(__unit__.ClassError) as r:
            yield r
        self.assertIn("must be marked", str(r.exception))
