"""
Tests for .objective.base module.
"""
from contextlib import contextmanager

from taipan.objective.modifiers import final, override
from taipan.testing import TestCase

import taipan.objective.base as __unit__


class _UniversalBaseClass(TestCase):

    @contextmanager
    def _assertRaisesFinalInheritanceException(self, base):
        with self.assertRaises(__unit__.ClassError) as r:
            yield r

        msg = str(r.exception)
        self.assertIn("cannot inherit", msg)
        self.assertIn(base.__name__, msg)

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


class ObjectMetaclass(_UniversalBaseClass):
    """Test case to ensure ObjectMetaclass plays with other metaclasses
    that may inherit from it. This includes weird and obscure cases, such as:

        * diamond inheritance, where metaclass inherits from more than one
          other metaclass, which in turn inherit from ObjectMetaclass
        * branch inheritance, where metaclass inherits from ObjectMetaclass'
          subclass in addition to other metaclass that is NOT a subclass
          of ObjectMetaclass

    The latter case is disntictly more important, too, as it allows for
    ObjectMetaclass to be incorporated into existing metaclass hierarchy.
    """
    def test_noop_meta_base__empty_class(self):
        NoopMeta = self._create_noop_metaclass()
        Class = self._create_class(NoopMeta, 'Class')

        self.assertIsInstance(Class, __unit__.ObjectMetaclass)
        self.assertIsInstance(Class, NoopMeta)

    def test_noop_meta__inheritance_from_final(self):
        NoopMeta = self._create_noop_metaclass()
        FinalClass = final(self._create_class(NoopMeta, 'FinalClass'))

        with self._assertRaisesFinalInheritanceException(FinalClass):
            class Foo(FinalClass):
                pass

    def test_noop_meta__unnecessary_override(self):
        NoopMeta = self._create_noop_metaclass()
        Class = self._create_class(NoopMeta, 'Class')

        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Class):
                @override
                def florb(self):
                    pass

    def test_noop_meta__missing_override(self):
        NoopMeta = self._create_noop_metaclass()
        Class = self._create_class(NoopMeta, 'Class', {
            'florb': lambda self: None,
        })

        with self._assertRaisesMissingOverrideException():
            class Foo(Class):
                def florb(self):
                    pass

    def test_tagging_meta(self):
        TaggingMeta = self._create_tagging_metaclass('_tagged')
        Class = self._create_class(TaggingMeta, 'Class')

        self.assertIsInstance(Class, __unit__.ObjectMetaclass)
        self.assertIsInstance(Class, TaggingMeta)
        self.assertTrue(Class._tagged)

    def test_diamond_inheritance_meta__empty_class(self):
        TaggingMeta1 = self._create_tagging_metaclass('_tagged1')
        TaggingMeta2 = self._create_tagging_metaclass('_tagged2')
        class Meta(TaggingMeta1, TaggingMeta2):
            pass
        Class = self._create_class(Meta, 'Class')

        self.assertIsInstance(Class, __unit__.ObjectMetaclass)
        self.assertIsInstance(Class, TaggingMeta1)
        self.assertIsInstance(Class, TaggingMeta2)
        self.assertTrue(Class._tagged1)
        self.assertTrue(Class._tagged2)

    def test_diamond_inheritance_meta__inheritance_from_final(self):
        Meta = self._create_multitagging_metaclass('_tagged1', '_tagged2')
        FinalClass = final(self._create_class(Meta, 'FinalClass'))

        with self._assertRaisesFinalInheritanceException(FinalClass):
            class Foo(FinalClass):
                pass

    def test_diamond_inheritance_meta__unnecessary_override(self):
        Meta = self._create_multitagging_metaclass('_tagged1', '_tagged2')
        Class = self._create_class(Meta, 'Class')

        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Class):
                @override
                def florb(self):
                    pass

    def test_diamond_inheritance_meta__missing_override(self):
        Meta = self._create_multitagging_metaclass('_tagged1', '_tagged2')
        Class = self._create_class(Meta, 'Class', {
            'florb': lambda self: None,
        })

        with self._assertRaisesMissingOverrideException():
            class Foo(Class):
                def florb(self):
                    pass

    def test_branch_inheritance_meta__empty_class(self):
        RegularNoopMeta = self._create_noop_metaclass(base=type)
        ObjectiveNoopMeta = self._create_noop_metaclass()
        class Meta(RegularNoopMeta, ObjectiveNoopMeta):
            pass
        Class = self._create_class(Meta, 'Class')

        self.assertIsInstance(Class, RegularNoopMeta)
        self.assertIsInstance(Class, ObjectiveNoopMeta)
        self.assertIsInstance(Class, __unit__.ObjectMetaclass)

    def test_branch_inheritance_meta__inheritance_from_final(self):
        Meta = self._create_mixed_noop_metaclass()
        FinalClass = final(self._create_class(Meta, 'FinalClass'))

        with self._assertRaisesFinalInheritanceException(FinalClass):
            class Foo(FinalClass):
                pass

    def test_branch_inheritance_meta__unnecessary_override(self):
        Meta = self._create_mixed_noop_metaclass()
        Class = self._create_class(Meta, 'Class')

        with self._assertRaisesUnnecessaryOverrideException():
            class Foo(Class):
                @override
                def florb(self):
                    pass

    def test_branch_inheritance_meta__missing_override(self):
        Meta = self._create_mixed_noop_metaclass()
        Class = self._create_class(Meta, 'Class', {
            'florb': lambda self: None,
        })

        with self._assertRaisesMissingOverrideException():
            class Foo(Class):
                def florb(self):
                    pass

    # Utility functions

    def _create_class(self, metaclass, name, dict_=None):
        return metaclass(name, (object,), dict_ or {})

    def _create_noop_metaclass(self, base=__unit__.ObjectMetaclass):
        class NoopMeta(base):
            pass

        return NoopMeta

    def _create_tagging_metaclass(self, tagname, base=__unit__.ObjectMetaclass):
        class TaggingMeta(base):
            def __new__(meta, name, bases, dict_):
                dict_.setdefault(tagname, True)
                return super(TaggingMeta, meta).__new__(
                    meta, name, bases, dict_)

        return TaggingMeta

    def _create_multitagging_metaclass(self, *tags):
        tagging_metaclasses = map(self._create_tagging_metaclass, tags)

        # sadly, the following is syntax error:
        #
        #     class Meta(*tagging_metaclasses):
        #         pass
        return type('Meta', tuple(tagging_metaclasses), {})

    def _create_mixed_noop_metaclass(self):
        RegularNoopMeta = self._create_noop_metaclass(base=type)
        ObjectiveNoopMeta = self._create_noop_metaclass()
        class Meta(RegularNoopMeta, ObjectiveNoopMeta):
            pass

        return Meta


class Object(_UniversalBaseClass):

    def test_definition(self):
        # make sure unusual definition of ``Object`` class
        # still has necessary members intact
        self.assertGreater(len(__unit__.Object.__doc__), 0)

    def test_empty_class(self):
        class Foo(__unit__.Object):
            pass
        self.assertIsInstance(Foo, __unit__.ObjectMetaclass)
