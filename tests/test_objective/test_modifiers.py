"""
Tests for .objective.modifiers module.
"""
import abc

from taipan.objective.base import Object
from taipan.functional.functions import const

from tests.test_objective.test_base import _UniversalBaseClass
import taipan.objective.modifiers as __unit__


# @abstract

class _Abstract(_UniversalBaseClass):

    def _assertIsABC(self, class_):
        self.assertIsSubclass(type(class_), abc.ABCMeta)

    def _assertCantInstantiate(self, class_, *args, **kwargs):
        with self.assertRaises(TypeError) as r:
            class_(*args, **kwargs)

        msg = str(r.exception)
        self.assertIn("instantiate", msg)
        self.assertIn(class_.__name__, msg)

    def _create_abstract_method_class(self, base, method=None):
        method = method or (lambda self: None)

        @__unit__.abstract
        class Foo(base):
            @__unit__.abstract.method
            def foo(self):
                return method(self)

        return Foo


class Abstract(_Abstract):

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


class Abstract_StandardClasses(_Abstract):
    """Tests for @abstract modifier as applied to standard Python classes."""

    def test_class__empty(self):
        @__unit__.abstract
        class Foo(object):
            pass

        self._assertIsABC(Foo)
        self._assertCantInstantiate(Foo)

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

    def test_inheritance__with_override__and_super_call(self):
        retval = 42
        Foo = self._create_abstract_method_class(method=const(retval))

        class Bar(Foo):
            def foo(self):
                return super(Bar, self).foo()

        self.assertEquals(retval, Bar().foo())

    # Utility functions

    def _create_abstract_method_class(self, method=None):
        return super(Abstract_StandardClasses, self) \
            ._create_abstract_method_class(base=object, method=method)


class Abstract_ObjectiveClasses(_Abstract):
    """Tests for @abstract modifier as applied to our 'objective' classes
    (descendants of :class:`taipan.objective.base.Object`).
    """
    def test_class__empty(self):
        @__unit__.abstract
        class Foo(Object):
            pass

        self._assertIsABC(Foo)
        self._assertCantInstantiate(Foo)

    def test_class__with_abstract_method(self):
        Foo = self._create_abstract_method_class()

        self._assertIsABC(Foo)
        self._assertCantInstantiate(Foo)

    def test_class__with_abstract_property(self):
        @__unit__.abstract
        class Foo(Object):
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

    def test_inheritance__with_override__but_no_modifier(self):
        Foo = self._create_abstract_method_class()

        with self._assertRaisesMissingOverrideException():
            class Bar(Foo):
                def foo(self):  # no ``@override``
                    pass

    def test_inheritance__with_override(self):
        Foo = self._create_abstract_method_class()
        class Bar(Foo):
            @__unit__.override
            def foo(self):
                pass

        Bar().foo()

    def test_inheritance__with_override__and_super_call(self):
        retval = 42
        Foo = self._create_abstract_method_class(method=const(retval))

        class Bar(Foo):
            @__unit__.override
            def foo(self):
                return super(Bar, self).foo()

        self.assertEquals(retval, Bar().foo())

    # Utility functions

    def _create_abstract_method_class(self, method=None):
        return super(Abstract_ObjectiveClasses, self) \
            ._create_abstract_method_class(base=Object, method=method)


# @final

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


class Final_Classes(_UniversalBaseClass):

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


class Final_Methods(_UniversalBaseClass):

    def test_method__normal__attempt_override(self):
        Base = self._create_class_with_final_method()

        with self._assertRaisesOverrideFinalException():
            class Foo(Base):
                @__unit__.override
                def florb(self):
                    pass

    def test_method__normal__attempt_hiding(self):
        Base = self._create_class_with_final_method()

        with self._assertRaisesHideFinalException():
            class Foo(Base):
                def florb(self):
                    pass

    def test_method__override__attempt_further_override(self):
        Foo = self._create_class_with_final_override_method()

        with self._assertRaisesOverrideFinalException():
            class Bar(Foo):
                @__unit__.override
                def florb(self):
                    pass

    def test_method__override__attempt_hiding(self):
        Foo = self._create_class_with_final_override_method()

        with self._assertRaisesHideFinalException():
            class Bar(Foo):
                def florb(self):
                    pass

    def test_method__reversed_final_and_override(self):
        """Test for 'reversed' application of @override and @final
        on a single method.

        This is 'reversed' in contrast to the recommended and more readable
        way of placing @final before @override, as mentioned by docs
        of the former. Nevertheless, the reversed way should still work.
        """
        class Base(Object):
            def florb(self):
                pass

        class Foo(Base):
            @__unit__.override
            @__unit__.final
            def florb(self):
                pass

        with self._assertRaisesOverrideFinalException():
            class Bar(Foo):
                @__unit__.override
                def florb(self):
                    pass
        with self._assertRaisesHideFinalException():
            class Bar(Foo):
                def florb(self):
                    pass

    # Utility functions

    def _create_class_with_final_method(self):
        class Base(Object):
            @__unit__.final
            def florb(self):
                pass

        return Base

    def _create_class_with_final_override_method(self):
        class Base(Object):
            def florb(self):
                pass

        class Foo(Base):
            @__unit__.final
            @__unit__.override
            def florb(self):
                pass

        return Foo


# @override

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


class Override_InstanceMethods_WithExplicitBase(_Override):
    OBJECT_CLASSNAME = 'taipan.objective.base.Object'

    class InnerClass(object):
        def florb(self):
            pass

    def test_override_base__class_object__correct(self):
        Base = self._create_objective_class()

        class Bar(Base):
            @__unit__.override(Base)
            def florb(self):
                pass

    def test_override_base__class_object__incorrect(self):
        Base = self._create_objective_class()

        with self._assertRaisesIncorrectOverrideBase(Object, correct=Base):
            class Bar(Base):
                @__unit__.override(Object)
                def florb(self):
                    pass

    def test_override_base__class_name(self):
        # we can use the universal base Object class itself to avoid
        # introducing another class in the global scope
        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Object):
                @__unit__.override(self.OBJECT_CLASSNAME)
                def foo(self):
                    pass

    def test_override_base__class_name__incorrect(self):
        Base = self._create_objective_class()

        with self._assertRaisesIncorrectOverrideBase(Object, correct=Base):
            class Bar(Base):
                @__unit__.override(self.OBJECT_CLASSNAME)
                def florb(self):
                    pass

    def test_override_base__class_name__inner_class(self):
        Base = self.InnerClass
        classname = '.'.join([
            __name__, self.__class__.__name__, Base.__name__])

        class Bar(Base):
            @__unit__.override(classname)
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
