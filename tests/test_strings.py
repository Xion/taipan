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
    ITERABLE = ['foo', 'bar', 'baz']
    DELIMITER = 'X'
    JOINED = 'fooXbarXbaz'

    def test_delimiter__none(self):
        with self.assertRaises(TypeError):
            __unit__.join(None, self.ITERABLE)

    def test_delimiter__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.join(object(), self.ITERABLE)

    def test_delimiter__empty(self):
        expected = reduce(str.__add__, self.ITERABLE, '')
        joined = __unit__.join('', self.ITERABLE)
        self.assertEquals(expected, joined)

    def test_iterable__none(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, None)

    def test_iterable__non_iterable(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, object())

    def test_iterable__empty(self):
        expected = ""
        joined = __unit__.join(self.DELIMITER, ())
        self.assertEquals(expected, joined)

    def test_normal(self):
        joined = __unit__.join(self.DELIMITER, self.ITERABLE)
        self.assertEquals(self.JOINED, joined)


class CamelCase(TestCase):
    LOWERCASE = "alice has a cat"
    CAPITALIZED = "Alice has a cat"
    LOWERCASE_CC = "aliceHasACat"
    CAPITALIZED_CC = "AliceHasACat"

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.camel_case(None)

    def test_non_string(self):
        with self.assertRaises(TypeError):
            __unit__.camel_case(object())

    def test_empty(self):
        self.assertEquals('', __unit__.camel_case(''))

    def test_capitalize__none(self):
        self.assertEquals(
            self.LOWERCASE_CC,
            __unit__.camel_case(self.LOWERCASE, capitalize=None))
        self.assertEquals(
            self.CAPITALIZED_CC,
            __unit__.camel_case(self.CAPITALIZED, capitalize=None))

    def test_capitalize__true(self):
        self.assertEquals(
            self.CAPITALIZED_CC,
            __unit__.camel_case(self.LOWERCASE, capitalize=True))
        self.assertEquals(
            self.CAPITALIZED_CC,
            __unit__.camel_case(self.CAPITALIZED, capitalize=True))

    def test_capitalize__false(self):
        self.assertEquals(
            self.LOWERCASE_CC,
            __unit__.camel_case(self.LOWERCASE, capitalize=False))
        self.assertEquals(
            self.LOWERCASE_CC,
            __unit__.camel_case(self.CAPITALIZED, capitalize=False))


class Replace(TestCase):
    pass
