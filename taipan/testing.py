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

from taipan.strings import BaseString


__all__ = ['TestCase']


_BaseTestCase = TestCase

class TestCase(_BaseTestCase):
    """Base test case class.

    Includes few additional, convenience assertion methods.
    """
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

    # Utility functions

    def __fail(self, custom_msg, standard_msg):
        self.fail(self._formatMessage(custom_msg, standard_msg))
