"""
Functions and classes related to testing.

This package is inteded to replace the standard :module:`unittest`.
Test code should import all required :module:`unittest` symbols from here::

    from taipan.testing import skipIf, TestCase  # etc.
"""
from taipan._compat import IS_PY3
from taipan.testing._unittest import *
from taipan.testing.asserts import AssertsMixin


__all__ = ['TestCase']


_BaseTestCase = TestCase


class TestCase(_BaseTestCase, AssertsMixin):
    """Augmented test case class.

    Includes few additional, convenience assertion methods.
    """
    # Python 3 changes name of the following assert function,
    # so we provide backward and forward synonyms for compatibility
    if IS_PY3:
        assertItemsEqual = _BaseTestCase.assertCountEqual
    else:
        assertCountEqual = _BaseTestCase.assertItemsEqual


from taipan.testing.skips import *
