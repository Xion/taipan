"""
Tests for .objective.modifiers module.
"""
import abc

from taipan.objective.base import Object
from taipan.testing import TestCase

from tests.test_objective.test_base import _UniversalBaseClass
import taipan.objective.modifiers as __unit__


class Abstract(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.abstract(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.abstract(object())

    def test_function(self):
        with self.assertRaises(TypeError):
            @__unit__.abstract
            def foo():
                pass

    def test_class__empty(self):
        @__unit__.abstract
        class Foo(object):
            pass

        self._assertIsABC(Foo)

    def test_class__with_abstract_method(self):
        Foo = self._create_abstract_method_class()

        self._assertIsABC(Foo)
        self._assertCantInstantiate(Foo)

    def test_class__with_abstract_property(self):
        @__unit__.abstract
        class Foo(object):
            @__unit__.abstract.property
            def foo(self):
                pass

        self._assertIsABC(Foo)
        self._assertCantInstantiate(Foo)

    def test_inheritance__without_override(self):
        Foo = self._create_abstract_method_class()
        class Bar(Foo):
            pass

        self._assertCantInstantiate(Bar)

    def test_inheritance__with_override(self):
        Foo = self._create_abstract_method_class()
        class Bar(Foo):
            def foo(self):
                pass

        Bar().foo()

    def test__inheritance__with_override__and_super_call(self):
        Foo = self._create_abstract_method_class()
        class Bar(Foo):
            def foo(self):
                super(Bar, self).foo()

        Bar().foo()

    # Utility functions

    def _assertIsABC(self, class_):
        self.assertIs(type(class_), abc.ABCMeta)

    def _assertCantInstantiate(self, class_, *args, **kwargs):
        with self.assertRaises(TypeError) as r:
            class_(*args, **kwargs)

        msg = str(r.exception)
        self.assertIn("instantiate", msg)
        self.assertIn(class_.__name__, msg)

    def _create_abstract_method_class(self):
        @__unit__.abstract
        class Foo(object):
            @__unit__.abstract.method
            def foo(self):
                pass

        return Foo


class Final(_UniversalBaseClass):

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
        class Foo(Object):
            pass
        return Foo


class _Override(_UniversalBaseClass):

    def _create_regular_class(self):
        return self._create_class(base=object)

    def _create_objective_class(self):
        return self._create_class(base=Object)

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


class Override_Basics(_Override):

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


class Override_InstanceMethods(_Override):

    def test_instance_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Object):
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
            class Bar(Base, Object):
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

        class Bar(Base, Object):
            @__unit__.override
            def florb(self):
                pass


class Override_ClassMethods(_Override):

    def test_class_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Object):
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
            class Foo(Base, Object):
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

        class Foo(Base, Object):
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


class Override_StaticMethods(_Override):

    def test_static_method__unnecessary(self):
        with self._assertRaisesUnnecessaryOverrideException():
            class Baz(Object):
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
            class Baz(Base, Object):
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

        class Baz(Base, Object):
            @__unit__.override
            @staticmethod
            def static_florb():
                pass
