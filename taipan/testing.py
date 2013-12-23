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

from taipan.functional import identity
from taipan.strings import BaseString


__all__ = ['TestCase']


_BaseTestCase = TestCase

class TestCase(_BaseTestCase):
    """Base test case class.

    Includes few additional, convenience assertion methods.
    """
    __missing = object()

    def assertStartsWith(self, prefix, string, msg=None):
        """Assert that ``string`` starts with given ``prefix``."""
        self.assertIsInstance(prefix, BaseString)
        self.assertIsInstance(string, BaseString)
        if not string.startswith(prefix):
            self.__fail(msg, "%s does not start with %s" % (string, prefix))

    def assertEndsWith(self, suffix, string, msg=None):
        """Assert that ``string`` ends with given ``suffix``."""
        self.assertIsInstance(suffix, BaseString)
        self.assertIsInstance(string, BaseString)
        if not string.endswith(suffix):
            self.__fail(msg, "%s does not end with %s" % (string, suffix))

    def assertThat(self, predicate, argument=__missing, msg=None):
        """Assert that a ``predicate`` applies to given ``argument``.

        Example::

            self.assertThat(is_pair, some_tuple)
        """
        if not callable(predicate):
            self.fail("%s is not a callable predicate" % predicate)

        satisfied = (
            predicate() if argument is self.__missing else predicate(argument))
        if not satisfied:
            self.__fail(
                msg, "predicate %s not satisfied for %s" % (predicate, string))

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
