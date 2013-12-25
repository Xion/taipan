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
        self._TESTCASE.assertZero(0L)

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
            self._TESTCASE.assertEmpty(0L)

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
    STRING = "foobar"

    def test_prefix__none(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(None, self.STRING)

    def test_prefix__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(object(), self.STRING)

    def test_prefix__empty_string(self):
        self._TESTCASE.assertStartsWith("", self.STRING)

    def test_string__none(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, None)

    def test_string__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, object())

    def test_string__empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertStartsWith(self.PREFIX, "")

    def test_success(self):
        self._TESTCASE.assertStartsWith(self.PREFIX, self.STRING)


class AssertEndsWith(_Assertion):
    SUFFIX = "bar"
    STRING = "foobar"

    def test_suffix__none(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(None, self.STRING)

    def test_suffix__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(object(), self.STRING)

    def test_suffix__empty_string(self):
        self._TESTCASE.assertEndsWith("", self.STRING)

    def test_string__none(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, None)

    def test_string__some_object(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, object())

    def test_string__empty_string(self):
        with self._assertFailure():
            self._TESTCASE.assertEndsWith(self.SUFFIX, "")

    def test_success(self):
        self._TESTCASE.assertEndsWith(self.SUFFIX, self.STRING)


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
