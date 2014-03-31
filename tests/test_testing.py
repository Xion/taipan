"""
Tests for the .testing module (yep).

.. note::

    Unlike other tests, these cannot use :class:`TestCase` from ``.testing``
    module, for the simple and obvious reason that it is among the very things
    that we're trying to test here!
"""
try:
    from unittest2 import TestCase, skipIf
except ImportError:
    from unittest import TestCase, skipIf

import operator

from taipan._compat import IS_PY3

import taipan.testing as __unit__


class _Assertion(TestCase):
    """Base class for test cases testing assert* methods."""

    class _DummyTestCase(__unit__.TestCase):
        """"Dummy object of the tested :class:`TestCase`.
        It is required to invoke assertion methods that we want to test.
        """
        def runTest(self):
            pass

    _TESTCASE = _DummyTestCase()

    def _assertFailure(self):
        return self.assertRaises(self._TESTCASE.failureException)


class AssertZero(_Assertion):

    def test_none(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(None)

    def test_empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertZero("")

    def test_empty_list(self):
        with self._assertFailure():
            self._TESTCASE.assertZero([])

    def test_empty_tuple(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(())

    def test_empty_dict(self):
        with self._assertFailure():
            self._TESTCASE.assertZero({})

    def test_some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(object())

    def test_positive_integer(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(42)

    def test_negative_integer(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(-69)

    def test_positive_float(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(3.14)

    def test_negative_float(self):
        with self._assertFailure():
            self._TESTCASE.assertZero(-2.73)

    def test_integer_zero(self):
        self._TESTCASE.assertZero(0)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_long_zero(self):
        self._TESTCASE.assertZero(eval('0L'))

    def test_float_zero(self):
        self._TESTCASE.assertZero(0.0)


class AssertEmpty(_Assertion):

    def test_none(self):
        with self._assertFailure():
            self._TESTCASE.assertEmpty(None)

    def test_false(self):
        with self._assertFailure():
            self._TESTCASE.assertEmpty(False)

    def test_zero(self):
        with self._assertFailure():
            self._TESTCASE.assertEmpty(0)
        with self._assertFailure():
            self._TESTCASE.assertEmpty(0.0)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_zero__py2(self):
        with self._assertFailure():
            self._TESTCASE.assertEmpty(eval('0L'))

    def test_empty_string(self):
        self._TESTCASE.assertEmpty("")

    def test_empty_tuple(self):
        self._TESTCASE.assertEmpty(())

    def test_empty_list(self):
        self._TESTCASE.assertEmpty([])

    def test_empty_dict(self):
        self._TESTCASE.assertEmpty({})

    def test_empty_set(self):
        self._TESTCASE.assertEmpty(set())
        self._TESTCASE.assertEmpty(frozenset())


class AssertStartsWith(_Assertion):
    PREFIX = "foo"
    PREFIXES_WITH_ACTUAL = (PREFIX, "baz")
    PREFIXES_SANS_ACTUAL = ("bar", "baz")

    STRING = "foobar"

    def test_prefix__none(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(None, self.STRING)

    def test_prefix__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(object(), self.STRING)

    def test_string__none(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, None)

    def test_string__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, object())

    def test_string__empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, "")

    def test_success__empty_prefix(self):
        self._TESTCASE.assertStartsWith("", self.STRING)

    def test_success__nonempty_prefix(self):
        self._TESTCASE.assertStartsWith(self.PREFIX, self.STRING)

    def test_success__prefix_tuple(self):
        self._TESTCASE.assertStartsWith(self.PREFIXES_WITH_ACTUAL, self.STRING)

    def test_failure__prefix_tuple(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(
                self.PREFIXES_SANS_ACTUAL, self.STRING)


class AssertEndsWith(_Assertion):
    SUFFIX = "bar"
    SUFFIXES_WITH_ACTUAL = (SUFFIX, "baz")
    SUFFIXES_SANS_ACTUAL = ("foo", "baz")

    STRING = "foobar"

    def test_suffix__none(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(None, self.STRING)

    def test_suffix__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(object(), self.STRING)

    def test_string__none(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, None)

    def test_string__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, object())

    def test_string__empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, "")

    def test_success__empty_suffix(self):
        self._TESTCASE.assertEndsWith("", self.STRING)

    def test_success__nonempty_suffix(self):
        self._TESTCASE.assertEndsWith(self.SUFFIX, self.STRING)

    def test_success__suffix_tuple(self):
        self._TESTCASE.assertEndsWith(self.SUFFIXES_WITH_ACTUAL, self.STRING)

    def test_failure__suffix_tuple(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(
                self.SUFFIXES_SANS_ACTUAL, self.STRING)


class AssertHasAttr(_Assertion):

    class Object(object):
        """Helper class of objects that can have attributes set easily."""
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    NO_ATTRS = Object()

    ATTR = 'foo'
    OBJECT_WITH_THE_ATTR = Object(**{ATTR: 42})
    OBJECT_SANS_THE_ATTR = Object(bar=1)

    def test_attr__none(self):
        with self._assertFailure():
            self._TESTCASE.assertHasAttr(None, self.NO_ATTRS)

    def test_attr__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertHasAttr(object(), self.NO_ATTRS)

    def test_attr__empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertHasAttr('', self.NO_ATTRS)

    def test_obj__none(self):
        with self._assertFailure():
            self._TESTCASE.assertHasAttr(self.ATTR, None)

    def test_obj__has_the_attr(self):
        self._TESTCASE.assertHasAttr(self.ATTR, self.OBJECT_WITH_THE_ATTR)

    def test_obj__does_not_have_the_attr(self):
        with self._assertFailure():
            self._TESTCASE.assertHasAttr(self.ATTR, self.OBJECT_SANS_THE_ATTR)


class AssertThat(_Assertion):
    IDENTITY = staticmethod(lambda x: x)
    NOT = staticmethod(lambda x: not x)

    def test_predicate__none(self):
        with self._assertFailure():
            self._TESTCASE.assertThat(None)

    def test_predicate__non_callable(self):
        with self._assertFailure():
            self._TESTCASE.assertThat(object())

    def test_predicate__truth(self):
        self._TESTCASE.assertThat(lambda: True)

    def test_predicate__falsity(self):
        with self._assertFailure():
            self._TESTCASE.assertThat(lambda: False)

    def test_predicate__expected_argument(self):
        with self.assertRaises(TypeError):
            self._TESTCASE.assertThat(self.IDENTITY)

    def test_argument__none(self):
        with self._assertFailure():
            self._TESTCASE.assertThat(AssertThat.IDENTITY, None)
        self._TESTCASE.assertThat(AssertThat.NOT, None)

    def test_argument__some_object(self):
        self._TESTCASE.assertThat(AssertThat.IDENTITY, object())
        with self._assertFailure():
            self._TESTCASE.assertThat(AssertThat.NOT, object())


class _IterableAssertion(_Assertion):
    LENGTH = 10

    ALL_TRUE = [True] * LENGTH
    ALL_FALSE = [False] * LENGTH
    ONE_TRUE = [True] + [False] * (LENGTH - 1)
    ONE_FALSE = [False] + [True] * (LENGTH - 1)

    IS_POSITIVE = staticmethod(lambda x: x > 0)
    IS_NEGATIVE = staticmethod(lambda x: x < 0)

    POSITIVES = list(range(1, LENGTH))
    NEGATIVES = list(map(operator.neg, POSITIVES))
    ALMOST_ALL_POSITIVES = [-1] + POSITIVES[1:]
    ALMOST_ALL_NEGATIVES = NEGATIVES[1:] + [1]


class AssertAll(_IterableAssertion):

    def test_iterable__none(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(None)

    def test_iterable__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(object())

    def test_iterable__empty(self):
        self._TESTCASE.assertAll(())

    def test_iterable__all_true(self):
        self._TESTCASE.assertAll(self.ALL_TRUE)

    def test_iterable__one_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(self.ONE_FALSE)

    def test_iterable__one_true(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(self.ONE_TRUE)

    def test_iterable__all_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(self.ALL_FALSE)

    def test_predicate__empty_iterable(self):
        self._TESTCASE.assertAll(self.IS_POSITIVE, ())
        self._TESTCASE.assertAll(self.IS_NEGATIVE, ())

    def test_predicate__all_true(self):
        self._TESTCASE.assertAll(self.IS_POSITIVE, self.POSITIVES)
        self._TESTCASE.assertAll(self.IS_NEGATIVE, self.NEGATIVES)

    def test_predicate__one_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(
                self.IS_POSITIVE, self.ALMOST_ALL_POSITIVES)
        with self._assertFailure():
            self._TESTCASE.assertAll(
                self.IS_NEGATIVE, self.ALMOST_ALL_NEGATIVES)

    def test_predicate__one_true(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(
                self.IS_POSITIVE, self.ALMOST_ALL_NEGATIVES)
        with self._assertFailure():
            self._TESTCASE.assertAll(
                self.IS_NEGATIVE, self.ALMOST_ALL_POSITIVES)

    def test_predicate__all_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAll(self.IS_POSITIVE, self.NEGATIVES)
        with self._assertFailure():
            self._TESTCASE.assertAll(self.IS_NEGATIVE, self.POSITIVES)


class AssertAny(_IterableAssertion):

    def test_iterable__none(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(None)

    def test_iterable__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(object())

    def test_iterable__empty(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(())

    def test_iterable__all_true(self):
        self._TESTCASE.assertAny(self.ALL_TRUE)

    def test_iterable__one_false(self):
        self._TESTCASE.assertAny(self.ONE_FALSE)

    def test_iterable__one_true(self):
        self._TESTCASE.assertAny(self.ONE_TRUE)

    def test_iterable__all_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(self.ALL_FALSE)

    def test_predicate__empty_iterable(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(self.IS_POSITIVE, ())
        with self._assertFailure():
            self._TESTCASE.assertAny(self.IS_NEGATIVE, ())

    def test_predicate__all_true(self):
        self._TESTCASE.assertAny(self.IS_POSITIVE, self.POSITIVES)
        self._TESTCASE.assertAny(self.IS_NEGATIVE, self.NEGATIVES)

    def test_predicate__one_false(self):
        self._TESTCASE.assertAny(self.IS_POSITIVE, self.ALMOST_ALL_POSITIVES)
        self._TESTCASE.assertAny(self.IS_NEGATIVE, self.ALMOST_ALL_NEGATIVES)

    def test_predicate__one_true(self):
        self._TESTCASE.assertAny(self.IS_POSITIVE, self.ALMOST_ALL_NEGATIVES)
        self._TESTCASE.assertAny(self.IS_NEGATIVE, self.ALMOST_ALL_POSITIVES)

    def test_predicate__all_false(self):
        with self._assertFailure():
            self._TESTCASE.assertAny(self.IS_POSITIVE, self.NEGATIVES)
        with self._assertFailure():
            self._TESTCASE.assertAny(self.IS_NEGATIVE, self.POSITIVES)


class AssertNoop(_Assertion):
    NOOP = staticmethod(lambda x: x)
    EFFECTIVE = staticmethod(lambda x: not x)

    ARGUMENT = 42

    def test_function__none(self):
        with self._assertFailure():
            self._TESTCASE.assertNoop(None, self.ARGUMENT)

    def test_function__non_callable(self):
        with self._assertFailure():
            self._TESTCASE.assertNoop(object(), self.ARGUMENT)

    def test_function__noop(self):
        self._TESTCASE.assertNoop(self.NOOP, self.ARGUMENT)

    def test__function__effective(self):
        with self._assertFailure():
            self._TESTCASE.assertNoop(self.EFFECTIVE, self.ARGUMENT)


class AssertResultsEqual(_Assertion):
    CONSTANT = staticmethod(lambda: -42)

    @staticmethod
    def VARIABLE():
        AssertResultsEqual.variable_result += 1
        return AssertResultsEqual.variable_result
    variable_result = 0

    def test_none(self):
        with self._assertFailure():
            self._TESTCASE.assertResultsEqual(None, self.CONSTANT)
        with self._assertFailure():
            self._TESTCASE.assertResultsEqual(self.CONSTANT, None)

    def test_non_callable(self):
        with self._assertFailure():
            self._TESTCASE.assertResultsEqual(object(), self.CONSTANT)
        with self._assertFailure():
            self._TESTCASE.assertResultsEqual(self.CONSTANT, object())

    def test_constant_functions(self):
        self._TESTCASE.assertResultsEqual(self.CONSTANT, self.CONSTANT)

    def test_variable_functions(self):
        with self._assertFailure():
            self._TESTCASE.assertResultsEqual(self.VARIABLE, self.VARIABLE)
