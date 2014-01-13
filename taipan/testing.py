"""
Functions and classes related to testing.

This module is inteded to replace the standard :module:`unittest`.
Test code should import all required :module:`unittest` symbols from here::

    from taipan.testing import skipIf, TestCase  # etc.
"""
try:
    from unittest2 import *
except ImportError:
    from unittest import *

from taipan._compat import IS_PY3
from taipan.collections import is_countable
from taipan.functional import identity
from taipan.strings import BaseString


__all__ = ['TestCase']


_BaseTestCase = TestCase

class TestCase(_BaseTestCase):
    """Base test case class.

    Includes few additional, convenience assertion methods.
    """
    __missing = object()

    def assertZero(self, argument, msg=None):
        """Assert that ``argument`` is equal to zero."""
        if msg is None:
            msg = "%r is not equal to zero" % (argument,)
        self.assertEqual(0, argument, msg=msg)

    def assertEmpty(self, argument, msg=None):
        """Assert that ``argument`` is an empty collection."""
        if not is_countable(argument):
            self.__fail(msg, "%r is not a countable collection" % argument)
        if argument:
            self.__fail(msg, "%r is not empty" % argument)

    # Python 3 changes name of the following assert function,
    # so we provide backward and forward synonyms for compatibility
    if IS_PY3:
        assertItemsEqual = _BaseTestCase.assertCountEqual
    else:
        assertCountEqual = _BaseTestCase.assertItemsEqual

    def assertStartsWith(self, prefix, string, msg=None):
        """Assert that ``string`` starts with given ``prefix``."""
        self.assertIsInstance(prefix, BaseString)
        self.assertIsInstance(string, BaseString)
        if not string.startswith(prefix):
            self.__fail(msg, "%r does not start with %r" % (string, prefix))

    def assertEndsWith(self, suffix, string, msg=None):
        """Assert that ``string`` ends with given ``suffix``."""
        self.assertIsInstance(suffix, BaseString)
        self.assertIsInstance(string, BaseString)
        if not string.endswith(suffix):
            self.__fail(msg, "%r does not end with %r" % (string, suffix))

    def assertHasAttr(self, attr, obj, msg=None):
        """Assert that ``obj``\ ect has given ``attr``\ ibute."""
        self.assertIsInstance(attr, BaseString)
        if not attr:
            self.fail("attribute name is empty")

        if not hasattr(obj, attr):
            self.__fail(msg, "%r does not have attribute %r" % (obj, attr))

    def assertThat(self, predicate, argument=__missing, msg=None):
        """Assert that a ``predicate`` applies to given ``argument``.

        Example::

            self.assertThat(is_pair, some_tuple)
        """
        if not callable(predicate):
            self.fail("%r is not a callable predicate" % predicate)

        satisfied = (predicate()
                     if argument is self.__missing
                     else predicate(argument))

        if not satisfied:
            predicate_part = (getattr(predicate, '__doc__', None)
                              or repr(predicate))
            argument_part = ("" if argument is self.__missing
                             else " for %r" % argument)
            self.__fail(msg, "predicate %r not satisfied%s" % (
                predicate_part, argument_part))

    def assertNoop(self, function, argument, msg=None):
        """Assert that ``function`` returns given ``argument`` verbatim
        when applied to it.

        Example::

            self.assertNoop(str.upper, "WAT")
        """
        if not callable(function):
            self.fail("%r is not a callable function" % function)

        result = function(argument)
        if result != argument:
            self.__fail(
                msg, "result %r of function %r differs from argument %r" % (
                    result, function, argument))

    # Utility functions

    def __fail(self, custom_msg, standard_msg):
        self.fail(self._formatMessage(custom_msg, standard_msg))


# Skip decorators

# TODO(xion): come up with better name
def skipIfReturnsTrue(predicate):
    """Decorator that will cause a test to be skipped
    if given ``predicate`` callable evaluates to true.
    """
    if predicate():
        desc = getattr(predicate, '__doc__', None) or repr(predicate)
        return skip("predicate evaluated to true: %s", desc)
    return identity()


def skipUnlessReturnsTrue(predicate):
    """Decorator that will cause a test to be skipped
    unless given ``predicate`` callable evaluates to true.
    """
    if not predicate():
        desc = getattr(predicate, '__doc__', None) or repr(predicate)
        return skip("predicate evaluated to false: %s", desc)
    return identity()

# TODO(xion): seriously weigh pros & cons of having those
skipIfReturnsFalse = skipUnlessReturnsTrue
skipUnlessReturnsFalse = skipIfReturnsTrue


def skipIfHasattr(obj, attr):
    """Decorator that will cause a test to be skipped
    if given ``object`` contains given ``attr``\ ibute.
    """
    if hasattr(obj, attr):
        return skip("%r has attribute %r" % (obj, attr))
    return identity()


def skipUnlessHasattr(obj, attr):
    """Decorator that will cause a test to be skipped
    unless given ``object`` contains given ``attr``\ ibute.
    """
    if not hasattr(obj, attr):
        return skip("%r does not have attribute %r" % (obj, attr))
    return identity()
