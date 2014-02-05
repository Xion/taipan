"""
Tests for the .functional.__init__ module.
"""
from contextlib import contextmanager

from taipan.testing import TestCase

import taipan.functional as __unit__


class EnsureCallable(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(object())

    def test_number(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(42)

    def test_string(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable("foo")

    def test_few_builtins(self):
        __unit__.ensure_callable(open)
        __unit__.ensure_callable(min)
        __unit__.ensure_callable(sum)
        __unit__.ensure_callable(str.__add__)

    def test_lambda(self):
        func = lambda : self.fail("lambda must not be actually called")
        __unit__.ensure_callable(func)

    def test_function(self):
        def func():
            self.fail("function must not be actually called")
        __unit__.ensure_callable(func)

    def test_class(self):
        class Foo(object):
            def __init__(self_):
                self.fail("class must not be actually instantiated")
        __unit__.ensure_callable(Foo)

    def test_callable_object(self):
        class Foo(object):
            def __call__(self_):
                self.fail("object must not be actually called")
        __unit__.ensure_callable(Foo())


class EnsureArgcount(TestCase):
    FEW_ARGS = ["foo", 'bar']
    MANY_ARGS = ["foo", 'bar', 1.41, False, None, (1,)]

    FEW = len(FEW_ARGS)
    MANY = len(MANY_ARGS)
    MORE_THAN_FEW = FEW + 1
    LESS_THAN_MANY = MANY - 1

    def test_no_limits(self):
        with self.assertRaises(ValueError):
            __unit__.ensure_argcount(self.FEW_ARGS)

    def test_invalid_limits(self):
        with self.assertRaises(ValueError) as r:
            __unit__.ensure_argcount(self.FEW_ARGS, min_=2, max_=1)
        self.assertIn("greater", str(r.exception))

    def test_args__none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount(None, min_=1, max_=1)

    def test_args__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount(object(), min_=1, max_=1)

    def test_args__empty(self):
        __unit__.ensure_argcount([], min_=0, max_=0)
        __unit__.ensure_argcount([], min_=0, max_=self.MANY)
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount([], min_=self.FEW)

    def test_args__less_than_min(self):
        with self.assertRaises(TypeError) as r:
            __unit__.ensure_argcount(self.FEW_ARGS, min_=self.MORE_THAN_FEW)
        self.assertIn("expected at least", str(r.exception))

    def test_args__more_than_max(self):
        with self.assertRaises(TypeError) as r:
            __unit__.ensure_argcount(self.MANY_ARGS, max_=self.LESS_THAN_MANY)
        self.assertIn("expected at most", str(r.exception))

    def test_args__exactly_min(self):
        __unit__.ensure_argcount(self.FEW_ARGS,
                                 min_=self.FEW, max_=self.MORE_THAN_FEW)

    def test_args__exactly_max(self):
        __unit__.ensure_argcount(self.MANY_ARGS,
                                 min_=self.LESS_THAN_MANY, max_=self.MANY)

    def test_args__exact(self):
        __unit__.ensure_argcount(self.FEW_ARGS, min_=self.FEW, max_=self.FEW)
        __unit__.ensure_argcount(self.MANY_ARGS, min_=self.MANY, max_=self.MANY)


class EnsureKeywordArgs(TestCase):
    MANDATORY = ('foo',)
    OPTIONAL = ('bar',)

    JUST_MANDATORY = {'foo': 1}
    JUST_OPTIONAL = {'bar': 2}
    ALL_KWARGS = {'foo': 1, 'bar': 2}

    def test_no_specs(self):
        with self.assertRaises(ValueError):
            __unit__.ensure_keyword_args(self.ALL_KWARGS)

    def test_kwargs__none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(None)

    def test_kwargs__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(object())

    def test_kwargs__empty(self):
        __unit__.ensure_keyword_args({}, optional=self.OPTIONAL)
        with self._assertMissingKwargsException(self.MANDATORY):
            __unit__.ensure_keyword_args({}, mandatory=self.MANDATORY)
        with self._assertMissingKwargsException(self.MANDATORY):
            __unit__.ensure_keyword_args(
                {}, mandatory=self.MANDATORY, optional=self.OPTIONAL)

    def test_kwargs__just_mandatory(self):
        __unit__.ensure_keyword_args(
            self.JUST_MANDATORY, mandatory=self.MANDATORY)
        with self._assertUnexpectedKwargsException(self.MANDATORY):
            __unit__.ensure_keyword_args(
                self.JUST_MANDATORY, optional=self.OPTIONAL)
        __unit__.ensure_keyword_args(self.JUST_MANDATORY,
                                     mandatory=self.MANDATORY,
                                     optional=self.OPTIONAL)

    def test_kwargs__just_optional(self):
        with self._assertMissingKwargsException(self.MANDATORY):
            __unit__.ensure_keyword_args(
                self.JUST_OPTIONAL, mandatory=self.MANDATORY)
        __unit__.ensure_keyword_args(
            self.JUST_OPTIONAL, optional=self.OPTIONAL)
        with self._assertMissingKwargsException(self.MANDATORY):
            __unit__.ensure_keyword_args(self.JUST_OPTIONAL,
                                         mandatory=self.MANDATORY,
                                         optional=self.OPTIONAL)

    def test_kwargs__mandatory_and_optional(self):
        with self._assertUnexpectedKwargsException(self.OPTIONAL):
            __unit__.ensure_keyword_args(
                self.ALL_KWARGS, mandatory=self.MANDATORY)
        __unit__.ensure_keyword_args(
            self.ALL_KWARGS, mandatory=self.MANDATORY, optional=self.OPTIONAL)

    def test_mandatory__none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(self.ALL_KWARGS, mandatory=None)

    def test_mandatory__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(self.ALL_KWARGS, mandatory=object())

    def test_optional__none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(self.ALL_KWARGS, optional=None)

    def test_optional__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_keyword_args(self.ALL_KWARGS, optional=object())

    # Utility functions

    @contextmanager
    def _assertMissingKwargsException(self, names):
        with self.assertRaises(TypeError) as r:
            yield r

        msg = str(r.exception)
        self.assertIn("mandatory", msg)
        for name in names:
            self.assertIn("'%s'" % name, msg)

    @contextmanager
    def _assertUnexpectedKwargsException(self, names):
        with self.assertRaises(TypeError) as r:
            yield r

        msg = str(r.exception)
        self.assertIn("unexpected", msg)
        for name in names:
            self.assertIn("'%s'" % name, msg)
