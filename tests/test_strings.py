"""
Tests for the .strings module.
"""
from unittest import skipIf, skipUnless, TestCase  # TODO: shim skips for 2.6

from taipan._compat import IS_PY3
import taipan.strings as __unit__


class IsString(TestCase):
    DEFAULT_STRING = 'foo'
    UNICODE_STRING = u'foo'
    BYTE_STRING = b'foo'

    def test_none(self):
        self.assertFalse(__unit__.is_string(None))

    def test_some_object(self):
        self.assertFalse(__unit__.is_string(object()))

    def test_default_string(self):
        self.assertTrue(__unit__.is_string(self.DEFAULT_STRING))

    def test_unicode_string(self):
        self.assertTrue(__unit__.is_string(self.UNICODE_STRING))

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_bytestring__py2(self):
        self.assertTrue(__unit__.is_string(self.BYTE_STRING))

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_bytestring__py3(self):
        self.assertFalse(__unit__.is_string(self.BYTE_STRING))


class EnsureString(TestCase):
    pass
