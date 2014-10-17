"""
Test case class with additional enhancements.
"""
from taipan._compat import IS_PY3, metaclass
from taipan.testing._unittest import TestCase as _TestCase
from taipan.testing.asserts import AssertsMixin


__all__ = ['TestCase']


class TestCaseMetaclass(type):
    pass


@metaclass(TestCaseMetaclass)
class TestCase(_TestCase, AssertsMixin):
    """Augmented test case class.

    Includes few additional, convenience assertion methods,
    as well as the capability to use test stage decorators,
    such as :func:`setUp` and :func:`tearDown`.
    """
    # Python 3 changes name of the following assert function,
    # so we provide backward and forward synonyms for compatibility
    if IS_PY3:
        assertItemsEqual = _TestCase.assertCountEqual
    else:
        assertCountEqual = _TestCase.assertItemsEqual
