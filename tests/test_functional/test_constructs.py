"""
Tests for .functional.constructs module.
"""
import collections
from contextlib import contextmanager

from taipan._compat import IS_PY26, IS_PY3
from taipan.testing import TestCase, skipIf, skipUnless

import taipan.functional.constructs as __unit__


# Statements

class Pass(TestCase):
    CALLS_COUNT = 10

    def test_no_args(self):
        self._iterate(__unit__.pass_)

    def test_none(self):
        self._iterate(__unit__.pass_, None)

    def test_some_object(self):
        self._iterate(__unit__.pass_, object())

    def test_number(self):
        self._iterate(__unit__.pass_, 42)

    def test_string(self):
        self._iterate(__unit__.pass_, "foo")

    def test_multiple_args(self):
        self._iterate(__unit__.pass_, 13, "bar", ())

    def test_keyword_args(self):
        self._iterate(__unit__.pass_, foo='baz', **{'class': -1})

    def test_all(self):
        self._iterate(__unit__.pass_,
                      None, 256, "foo", bar='x', baz=lambda: None)

    # Utility functions

    def _iterate(self, func, *args, **kwargs):
        for _ in range(self.CALLS_COUNT):
            func = func(*args, **kwargs)


class Raise(TestCase):
    OBJECT = Exception("foo")
    CLASS = ValueError
    ARGUMENT = 42

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_no_args__incorrect__py2(self):
        with self.assertRaises(TypeError):
            __unit__.raise_()

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_no_args__incorrect__py3(self):
        with self.assertRaises(RuntimeError):
            __unit__.raise_()

    def test_no_args__correct(self):
        try:
            raise self.OBJECT
        except:
            with self.assertRaises(self.OBJECT.__class__) as r:
                __unit__.raise_()  # should re-raise caught exception
            self.assertIs(self.OBJECT, r.exception)

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.raise_(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.raise_(object())

    def test_exception_object(self):
        with self.assertRaises(self.OBJECT.__class__) as r:
            __unit__.raise_(self.OBJECT)
        self.assertIs(self.OBJECT, r.exception)

    def test_exception_object__and_positional_arguments(self):
        with self.assertRaises(TypeError) as r:
            __unit__.raise_(self.OBJECT, self.ARGUMENT)
        self.assertIn("can't pass arguments along with exception object",
                      str(r.exception))

    def test_exception_object__and_keyword_arguments(self):
        with self.assertRaises(TypeError) as r:
            __unit__.raise_(self.OBJECT, foo=self.ARGUMENT)
        self.assertIn("can't pass arguments along with exception object",
                      str(r.exception))

    def test_exception_class(self):
        with self.assertRaises(self.CLASS) as r:
            __unit__.raise_(self.CLASS, self.ARGUMENT)
        self.assertEquals((self.ARGUMENT,), r.exception.args)


class Try(TestCase):
    EXCEPTION_CLASS = ArithmeticError
    EXCEPTION = EXCEPTION_CLASS("foo")
    DIFFERENT_EXCEPTION_CLASS = ReferenceError

    BLOCK_RETVAL = -7
    BLOCK = staticmethod(lambda: Try.BLOCK_RETVAL)

    RAISE = staticmethod(lambda: __unit__.raise_(Try.EXCEPTION))
    CATCH = staticmethod(lambda e: e)
    RERAISE = staticmethod(lambda _: __unit__.raise_())

    ELSE_RETVAL = 42
    ELSE = staticmethod(lambda: Try.ELSE_RETVAL)

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.try_()

    def test_block__none(self):
        with self.assertRaises(TypeError):
            __unit__.try_(None)

    def test_block__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.try_(object())

    def test_block__function(self):
        with self.assertRaises(TypeError) as r:
            __unit__.try_(lambda: None)

        msg = str(r.exception)
        self.assertIn("at least one of", msg)
        self.assertIn("except_", msg)
        self.assertIn("else_", msg)
        self.assertIn("finally_", msg)

    def test_except__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.try_(self.RAISE, except_=object())

    def test_except__pass(self):
        __unit__.try_(self.RAISE, except_=__unit__.pass_)

    def test_except__catch__exception_raised(self):
        self.assertIs(self.EXCEPTION,
                      __unit__.try_(self.RAISE, except_=self.CATCH))

    def test_except__catch__no_exception(self):
        retval = __unit__.try_(self.BLOCK, except_=self.CATCH)
        self.assertEquals(self.BLOCK_RETVAL, retval)

    def test_except__reraise(self):
        with self.assertRaises(self.EXCEPTION_CLASS) as r:
            __unit__.try_(self.RAISE, except_=self.RERAISE)
        self.assertIs(self.EXCEPTION, r.exception)

    def test_except__unordered_dict(self):
        with self.assertRaises(TypeError):
            __unit__.try_(self.BLOCK, except_={Exception: self.CATCH})

    @skipIf(IS_PY26, "requires Python 2.7+")
    def test_except__ordered_dict(self):
        retval = __unit__.try_(self.RAISE, except_=collections.OrderedDict([
            (self.EXCEPTION_CLASS, self.CATCH)
        ]))
        self.assertIs(self.EXCEPTION, retval)

    def test_except__handler_list__empty(self):
        with self.assertRaises(TypeError):
            __unit__.try_(self.RAISE, except_=[])

    def test_except__handler_list__singleton(self):
        retval = __unit__.try_(self.RAISE,
                               except_=[(self.EXCEPTION_CLASS, self.CATCH)])
        self.assertIs(self.EXCEPTION, retval)

    def test_except__handler_list__match_first__exact(self):
        retval = __unit__.try_(self.RAISE, except_=[
            (self.EXCEPTION_CLASS, self.CATCH),
            (Exception, self.RAISE),
        ])
        self.assertIs(self.EXCEPTION, retval)

    def test_except__handler_list__match_first__superclass(self):
        retval = __unit__.try_(self.RAISE, except_=[
            (Exception, self.CATCH),
            (self.EXCEPTION_CLASS, self.RERAISE),
        ])
        self.assertIs(self.EXCEPTION, retval)

    def test_except__handler_list__bypass_first(self):
        with self.assertRaises(self.EXCEPTION_CLASS):
            __unit__.try_(self.RAISE, except_=[
                (self.DIFFERENT_EXCEPTION_CLASS, self.CATCH),
                (self.EXCEPTION_CLASS, self.RERAISE),
            ])

    def test_else__without_except(self):
        with self.assertRaises(TypeError) as r:
            __unit__.try_(self.RAISE, else_=self.ELSE)

        msg = str(r.exception)
        self.assertIn("else_", msg)
        self.assertIn("except_", msg)

    def test_else__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.try_(self.RAISE, except_=self.CATCH, else_=object())

    def test_else__function__exception_raised(self):
        retval = __unit__.try_(self.RAISE, except_=self.CATCH, else_=self.ELSE)
        self.assertNotEqual(self.ELSE_RETVAL, retval)

    def test_else__function__no_exception(self):
        retval = __unit__.try_(self.BLOCK, except_=self.CATCH, else_=self.ELSE)
        self.assertEquals(self.ELSE_RETVAL, retval)

    def test_finally__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.try_(self.BLOCK, finally_=object())

    def test_finally__function__exception_raised__uncaught(self):
        finally_ = self._create_finally_clause()

        with self.assertRaises(self.EXCEPTION_CLASS) as r:
            __unit__.try_(self.RAISE, finally_=finally_)

        self.assertIs(self.EXCEPTION, r.exception)
        self.assertTrue(finally_._called)

    def test_finally__function__exception_raised__caught(self):
        finally_ = self._create_finally_clause()

        retval = __unit__.try_(self.RAISE,
                               except_=self.CATCH, finally_=finally_)

        self.assertIs(self.EXCEPTION, retval)
        self.assertTrue(finally_._called)

    def test_finally__function__no_exception(self):
        finally_ = self._create_finally_clause()

        retval = __unit__.try_(self.BLOCK, finally_=finally_)

        self.assertEquals(self.BLOCK_RETVAL, retval)
        self.assertTrue(finally_._called)

    def test_full_form__exception_raised(self):
        finally_ = self._create_finally_clause()

        retval = __unit__.try_(
            self.RAISE,
            except_=self.CATCH, else_=self.ELSE, finally_=finally_)

        self.assertIs(self.EXCEPTION, retval)
        self.assertTrue(finally_._called)

    def test_full_form__no_exception(self):
        finally_ = self._create_finally_clause()

        retval = __unit__.try_(
            self.BLOCK,
            except_=self.CATCH, else_=self.ELSE, finally_=finally_)

        self.assertEquals(self.ELSE_RETVAL, retval)
        self.assertTrue(finally_._called)

    # Utility functions

    def _create_finally_clause(self):
        def finally_():
            finally_._called = True

        finally_.called = False
        return finally_


class With(TestCase):
    RETURN = staticmethod(lambda x: x)
    VALUE = 42

    def test_contextmanager__none(self):
        with self.assertRaises(TypeError):
            __unit__.with_(None, self.RETURN)

    def test_contextmanager__invalid_object(self):
        with self.assertRaises(TypeError):
            __unit__.with_(object(), self.RETURN)

    def test_do__none(self):
        with self.assertRaises(TypeError):
            __unit__.with_(self._contextmanager(), None)

    def test_do__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.with_(self._contextmanager(), object())

    def test_do__pass(self):
        __unit__.with_(self._contextmanager(), do=__unit__.pass_())

    def test_do__function(self):
        retval = __unit__.with_(self._contextmanager(self.VALUE),
                                do=self.RETURN)
        self.assertEquals(self.VALUE, retval)

    # Utility functions

    @contextmanager
    def _contextmanager(self, value=None):
        yield value


# Variable wrapper

class Var(TestCase):
    INTEGER = 42
    STRING = 'foo'

    SIMPLE_VALUE = INTEGER
    COMPOUND_VALUE = {STRING: 'bar', INTEGER: -1}
    VALUES = [None, SIMPLE_VALUE, COMPOUND_VALUE]

    DELTA = 5

    def test_ctor__argless(self):
        var = __unit__.Var()
        self.assertIs(__unit__.Var.ABSENT, var.value)

    def test_ctor__none(self):
        var = __unit__.Var(None)
        self.assertIsNone(var.value)

    def test_ctor__simple_value(self):
        var = __unit__.Var(self.SIMPLE_VALUE)
        self.assertEquals(self.SIMPLE_VALUE, var.value)

    def test_ctor__compound_value(self):
        var = __unit__.Var(self.COMPOUND_VALUE)
        self.assertEquals(self.COMPOUND_VALUE, var.value)

    # Tests for normal methods

    def test_clear__absent(self):
        var = __unit__.Var()
        var.clear()
        self._assertIsAbsent(var)

    def test_clear__present(self):
        var = __unit__.Var(self.SIMPLE_VALUE)
        var.clear()
        self._assertIsAbsent(var)

    def test_dec__absent(self):
        var = __unit__.Var()
        with self._assertRaisesValueAbsent():
            var.dec()

    def test_dec__incompatible(self):
        var = __unit__.Var(self.STRING)
        with self.assertRaises(TypeError):
            var.dec()

    def test_dec__integer__argless(self):
        var = __unit__.Var(self.INTEGER)
        var.dec()
        self.assertEquals(self.INTEGER - 1, var.value)

    def test_dec__integer__delta(self):
        var = __unit__.Var(self.INTEGER)
        var.dec(self.DELTA)
        self.assertEquals(self.INTEGER - self.DELTA, var.value)

    def test_get__absent(self):
        var = __unit__.Var()
        with self._assertRaisesValueAbsent():
            var.get()

    def test_get__present(self):
        self.assertIsNone(__unit__.Var(None).get())
        self.assertEquals(
            self.SIMPLE_VALUE, __unit__.Var(self.SIMPLE_VALUE).get())
        self.assertEquals(
            self.COMPOUND_VALUE, __unit__.Var(self.COMPOUND_VALUE).get())

    def test_has_value__absent(self):
        var = __unit__.Var()
        self.assertFalse(var.has_value())

    def test_has_value__present(self):
        for value in self.VALUES:
            self.assertTrue(__unit__.Var(value).has_value())

    def test_inc__absent(self):
        var = __unit__.Var()
        with self._assertRaisesValueAbsent():
            var.inc()

    def test_inc__incompatible(self):
        var = __unit__.Var(self.STRING)
        with self.assertRaises(TypeError):
            var.inc()

    def test_inc__integer__argless(self):
        var = __unit__.Var(self.INTEGER)
        var.inc()
        self.assertEquals(self.INTEGER + 1, var.value)

    def test_inc__integer__delta(self):
        var = __unit__.Var(self.INTEGER)
        var.inc(self.DELTA)
        self.assertEquals(self.INTEGER + self.DELTA, var.value)

    def test_set__from_absent__to_absent(self):
        var = __unit__.Var()
        var.set(__unit__.Var.ABSENT)
        self._assertIsAbsent(var)

    def test_set__from_absent__to_present(self):
        var = __unit__.Var()
        var.set(self.SIMPLE_VALUE)
        self.assertEquals(self.SIMPLE_VALUE, var.value)

    def test_set__from_present__to_present__noop(self):
        var = __unit__.Var(self.SIMPLE_VALUE)
        var.set(self.SIMPLE_VALUE)
        self.assertEquals(self.SIMPLE_VALUE, var.value)

    def test_set__from_present__to_present__different(self):
        var = __unit__.Var(self.SIMPLE_VALUE)
        var.set(self.COMPOUND_VALUE)
        self.assertEquals(self.COMPOUND_VALUE, var.value)

    def test_set__from_present__to_absent(self):
        var = __unit__.Var(self.SIMPLE_VALUE)
        var.set(__unit__.Var.ABSENT)
        self._assertIsAbsent(var)

    # Tests for magic methods

    def test_call__absent(self):
        var = __unit__.Var()
        with self._assertRaisesValueAbsent():
            var()

    def test_call__present(self):
        self.assertIsNone(__unit__.Var(None)())
        self.assertEquals(
            self.SIMPLE_VALUE, __unit__.Var(self.SIMPLE_VALUE)())
        self.assertEquals(
            self.COMPOUND_VALUE, __unit__.Var(self.COMPOUND_VALUE)())

    def test_contains__absent(self):
        var = __unit__.Var()
        for value in self.VALUES:
            self.assertNotIn(value, var)

    def test_contains__present(self):
        for i, value in enumerate(self.VALUES):
            var = __unit__.Var(value)
            self.assertIn(value, var)
            for other_value in self.VALUES[0:i] + self.VALUES[(i + 1):]:
                self.assertNotIn(other_value, var)

    def test_enter_and_exit(self):
        with __unit__.Var() as var:
            self._assertIsAbsent(var)
            var.set(None)
            self.assertTrue(var.has_value())

    def test_iter__absent(self):
        var = __unit__.Var()
        self.assertEmpty(var)

    def test_iter__present(self):
        for value in self.VALUES:
            self.assertItemsEqual([value], __unit__.Var(value))

    def test_len__absent(self):
        var = __unit__.Var()
        self.assertZero(len(var))

    def test_len__present(self):
        for value in self.VALUES:
            var = __unit__.Var(value)
            self.assertEquals(1, len(var))

    # Utility functions

    def _assertIsAbsent(self, var):
        # intentionally bypass Var.has_value(), as this tests it indirectly
        self.assertIs(__unit__.Var.ABSENT, var.value)

    @contextmanager
    def _assertRaisesValueAbsent(self):
        with self.assertRaises(__unit__.ValueAbsentError) as r:
            yield r
