"""
Tests for the .strings module.
"""
from taipan._compat import IS_PY3
from taipan.testing import skipIf, skipUnless, TestCase

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
    DEFAULT_STRING = 'foo'
    UNICODE_STRING = u'foo'
    BYTE_STRING = b'foo'

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_string(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_string(object())

    def test_default_string(self):
        __unit__.ensure_string(self.DEFAULT_STRING)

    def test_unicode_string(self):
        __unit__.ensure_string(self.UNICODE_STRING)

    @skipIf(IS_PY3, "requires Python 2.x")
    def test_bytestring__py2(self):
        __unit__.ensure_string(self.BYTE_STRING)

    @skipUnless(IS_PY3, "requires Python 3.x")
    def test_bytestring__py3(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_string(self.DEFAULT_STRING)


class Join(TestCase):
    pass


class CamelCase(TestCase):
    pass


class Replace(TestCase):
    pass
