"""
Tests for .objective.classes module.
"""
from __future__ import division

from taipan._compat import IS_PY3
from taipan.collections import is_iterable
from taipan.collections.lists import head, init, last
from taipan.testing import TestCase, skipIf, skipUnless

import taipan.objective.classes as __unit__


class EnsureClass(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_class(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_class(object())

    def test_class__builtin(self):
        __unit__.ensure_class(object)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_class__py2__old_style(self):
        class Foo:
            pass
        __unit__.ensure_class(Foo)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_class__py2__new_style(self):
        class Foo(object):
            pass
        __unit__.ensure_class(Foo)

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_class__py3__implicit_base(self):
        class Foo:
            pass
        __unit__.ensure_class(Foo)

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_class__py3__explicit_base(self):
        class Foo(object):
            pass
        __unit__.ensure_class(Foo)


class _ClassIteration(TestCase):

    def _create_inheritance_chain(self, length):
        res = []
        class_ = None
        for i in range(length):
            class_ = self._create_class("Class%s" % i, bases=class_)
            res.append(class_)
        return res

    def _create_binary_inheritance_tree(self, depth):
        root = self._create_class("Class0")
        res = [root]  # classes ordered in level-order fashion
        if depth > 1:
            last_level = [root]
            for i in range(1, depth):
                curr_level = []
                for j in range(2 ** i):
                    class_ = self._create_class("Class%s" % len(res),
                                                bases=last_level[j // 2])
                    curr_level.append(class_)
                    res.append(class_)
                last_level = curr_level
        return res

    def _create_class(self, name, bases=None):
        if bases is None:
            bases = ()
        elif not is_iterable(bases):
            bases = (bases,)
        return type(name, bases, {})


class IterSubclasses(_ClassIteration):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.iter_subclasses(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.iter_subclasses(object())

    def test_class__no_subclasses(self):
        class_ = head(self._create_inheritance_chain(1))
        self.assertEmpty(__unit__.iter_subclasses(class_))

    def test_class__single_subclass(self):
        class_, subclass = self._create_inheritance_chain(2)
        self.assertItemsEqual([subclass], __unit__.iter_subclasses(class_))

    def test_class__flat_hierarchy(self):
        class_ = self._create_class("Foo")
        subclasses = [self._create_class("Subclass%s" % i, bases=class_)
                      for i in range(5)]
        self.assertItemsEqual(subclasses, __unit__.iter_subclasses(class_))

    def test_class__deep_hierarchy(self):
        tree = self._create_binary_inheritance_tree(4)
        class_, subclasses = tree[0], tree[1:]
        self.assertItemsEqual(subclasses, __unit__.iter_subclasses(class_))


class IterSuperclasses(_ClassIteration):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.iter_superclasses(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.iter_superclasses(object())

    def test_class__no_superclasses(self):
        self.assertEmpty(__unit__.iter_superclasses(object))

    def test_class__just_object_superclass(self):
        class_ = self._create_class("Class0")
        self.assertItemsEqual([object], __unit__.iter_superclasses(class_))

    def test_class__one_custom_superclass(self):
        superclass, class_ = self._create_inheritance_chain(2)
        self.assertItemsEqual(
            [object, superclass], __unit__.iter_superclasses(class_))

    def test_class__deep_hierarchy(self):
        chain = self._create_inheritance_chain(8)
        superclasses, class_ = init(chain), last(chain)
        self.assertItemsEqual(
            [object] + superclasses, __unit__.iter_superclasses(class_))
