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


__all__ = ['TestCase']


_BaseTestCase = TestCase

class TestCase(_BaseTestCase):
    pass
