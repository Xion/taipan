"""
Tests for the .strings module.
"""
from contextlib import contextmanager
from functools import reduce
import re

from taipan._compat import IS_PY3
from taipan.collections import is_mapping
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


class IsRegex(TestCase):
    DEFAULT_STRING_RE = re.compile('foo')
    UNICODE_STRING_RE = re.compile(u'foo')
    BYTE_STRING_RE = re.compile(b'foo')

    def test_none(self):
        self.assertFalse(__unit__.is_regex(None))

    def test_some_object(self):
        self.assertFalse(__unit__.is_regex(object()))

    def test_default_string_re(self):
        self.assertTrue(__unit__.is_regex(self.DEFAULT_STRING_RE))

    def test_unicode_string_re(self):
        self.assertTrue(__unit__.is_regex(self.UNICODE_STRING_RE))

    def test_bytestirng_re(self):
        self.assertTrue(__unit__.is_regex(self.BYTE_STRING_RE))


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
            __unit__.ensure_string(self.BYTE_STRING)


class EnsureRegex(TestCase):
    DEFAULT_STRING_RE = re.compile('foo')
    UNICODE_STRING_RE = re.compile(u'foo')
    BYTE_STRING_RE = re.compile(b'foo')

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_regex(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_regex(object())

    def test_default_string_re(self):
        __unit__.ensure_regex(self.DEFAULT_STRING_RE)

    def test_unicode_string_re(self):
        __unit__.ensure_regex(self.UNICODE_STRING_RE)

    def test_bytestirng_re(self):
        __unit__.ensure_regex(self.BYTE_STRING_RE)


class Split(TestCase):
    TEXT = 'Alice has a cat'
    WORDS = ['Alice', 'has', 'a', 'cat']

    STRING = 'fooXbarXbaz'
    REGEX = 'ba.'
    SPLIT_BY_X = ['foo', 'bar', 'baz']
    SPLIT_BY_A_OR_X = ['foo', 'b', 'r', 'b', 'z']
    SPLIT_BY_REGEX = ['fooX', 'X', '']

    MAXSPLIT = 1

    def test_string__none(self):
        with self.assertRaises(TypeError):
            __unit__.split(None)

    def test_string__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.split(object())

    def test_string__empty__no_separator(self):
        # result contingent on TODO inside the ``split`` function
        self.assertEquals([], __unit__.split(''))

    def test_string__some_string__no_separator(self):
        self.assertEquals([self.STRING], __unit__.split(self.STRING))

    def test_by__none__words(self):
        self.assertEquals(self.WORDS, __unit__.split(self.TEXT, by=None))

    def test_by__none__one_word(self):
        self.assertEquals([self.STRING], __unit__.split(self.STRING, by=None))

    def test_by__empty_string(self):
        with self.assertRaises(ValueError) as r:
            __unit__.split(self.STRING, by='')
        self.assertIn("empty", str(r.exception))

    def test_by__single_string(self):
        self.assertEquals(self.SPLIT_BY_X, __unit__.split(self.STRING, by='X'))

    def test_by__empty_tuple(self):
        with self.assertRaises(ValueError) as r:
            __unit__.split(self.STRING, by=())
        self.assertIn("empty", str(r.exception))

    def test_by__invalid_tuple(self):
        with self.assertRaises(TypeError):
            __unit__.split(self.STRING, by=(42, 'a', 'X'))

    def test_by__multiple_strings(self):
        self.assertEquals(
            self.SPLIT_BY_A_OR_X, __unit__.split(self.STRING, by=('a', 'X')))

    def test_by__regex_object(self):
        self.assertEquals(
            self.SPLIT_BY_REGEX,
            __unit__.split(self.STRING, by=re.compile(self.REGEX)))

    def test_by__empty_regex(self):
        with self.assertRaises(ValueError) as r:
            __unit__.split(self.STRING, by=re.compile(''))
        self.assertIn("empty", str(r.exception))

    def test_by__allegedly_regex_string(self):
        # regex supplied as string should be treated as string,
        # (in this case, it results in no splits whatsoever)
        self.assertEquals(
            [self.STRING], __unit__.split(self.STRING, by=self.REGEX))

    def test_maxsplit__none(self):
        self.assertEquals(self.WORDS, __unit__.split(self.TEXT, maxsplit=None))
        self.assertEquals(
            self.SPLIT_BY_A_OR_X,
            __unit__.split(self.STRING, by=('a', 'X'), maxsplit=None))
        self.assertEquals(
            self.SPLIT_BY_REGEX,
            __unit__.split(self.STRING,
                           by=re.compile(self.REGEX), maxsplit=None))

    def test_maxsplit__zero(self):
        self.assertEquals(
            [self.TEXT], __unit__.split(self.TEXT, by=None, maxsplit=0))
        self.assertEquals(
            [self.STRING], __unit__.split(self.STRING, by='X', maxsplit=0))
        self.assertEquals(
            [self.STRING],
            __unit__.split(self.STRING, by=('a', 'X'), maxsplit=0))
        self.assertEquals(
            [self.STRING],
            __unit__.split(self.STRING, by=re.compile(self.REGEX), maxsplit=0))

    def test_maxsplit__non_integer(self):
        with self.assertRaises(TypeError):
            __unit__.split(self.TEXT, maxsplit=object())
        with self.assertRaises(TypeError):
            __unit__.split(self.STRING, by='X', maxsplit=object())
        with self.assertRaises(TypeError):
            __unit__.split(self.STRING, by=('a', 'X'), maxsplit=object())
        with self.assertRaises(TypeError):
            __unit__.split(
                self.STRING, by=re.compile(self.REGEX), maxsplit=object())

    def test_maxsplit__positive(self):
        maxsplit = self.MAXSPLIT  # just to make expressions fit

        self.assertEquals(
            self.WORDS[:maxsplit] + [' '.join(self.WORDS[maxsplit:])],
            __unit__.split(self.TEXT, maxsplit=maxsplit))
        self.assertEquals(
            self.SPLIT_BY_X[:maxsplit] + ['X'.join(self.SPLIT_BY_X[maxsplit:])],
            __unit__.split(self.STRING, by='X', maxsplit=maxsplit))

        # this works because the first split to perform at 'X' rather than 'a'
        self.assertEquals(
            self.SPLIT_BY_X[:maxsplit] + ['X'.join(self.SPLIT_BY_X[maxsplit:])],
            __unit__.split(self.STRING, by=('a', 'X'), maxsplit=maxsplit))

        # here, first split is at 'bar'
        sep_index = self.STRING.find('bar')
        string_sans_sep = self.STRING.replace('bar', '')
        self.assertEquals(
            [self.STRING[:sep_index], string_sans_sep[sep_index:]],
            __unit__.split(
                self.STRING, by=re.compile(self.REGEX), maxsplit=maxsplit))


class Join(TestCase):
    DELIMITER = 'X'
    STRING_REPLACEMENT = '_'
    FUNCTION_REPLACEMENT = staticmethod(lambda x: Join.STRING_REPLACEMENT)

    ITERABLE = ['foo', 'bar', 'baz']
    ITERABLE_WITH_NONES = ['foo', None, 'bar', None, 'baz']
    ITERABLE_WITH_NUMBERS = ['foo', 42, 'bar', 42, 'baz']

    JOINED = 'fooXbarXbaz'
    JOINED_WITH_CASTED_NONES = 'fooXNoneXbarXNoneXbaz'
    JOINED_WITH_CASTED_NUMBERS = 'fooX42XbarX42Xbaz'
    JOINED_WITH_REPLACEMENTS = 'fooX_XbarX_Xbaz'

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

    def test_default(self):
        joined = __unit__.join(self.DELIMITER, self.ITERABLE)
        self.assertEquals(self.JOINED, joined)

    def test_errors__unexpected(self):
        errors = 'unexpected'
        with self.assertRaises(TypeError) as r:
            __unit__.join(self.DELIMITER, self.ITERABLE, errors=errors)
        self.assertIn(repr(errors), str(r.exception))

    def test_errors__default__strings_with_nones(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NONES)

    def test_errors__default__strings_with_numbers(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NUMBERS)

    def test_errors__raise__just_strings(self):
        for errors in ('raise', True):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE,
                                   errors=errors)
            self.assertEquals(self.JOINED, joined)

    def test_errors__raise__strings_with_nones(self):
        for errors in ('raise', True):
            with self.assertRaises(TypeError):
                __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NONES,
                              errors=errors)

    def test_errors__raise__strings_with_numbers(self):
        for errors in ('raise', True):
            with self.assertRaises(TypeError):
                __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NUMBERS,
                              errors=errors)

    def test_errors__cast__just_strings(self):
        for errors in ('cast', False):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE,
                                   errors=errors)
            self.assertEquals(self.JOINED, joined)

    def test_errors__cast__strings_with_nones(self):
        for errors in ('cast', False):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NONES,
                                   errors=errors)
            self.assertEquals(self.JOINED_WITH_CASTED_NONES, joined)

    def test_errors__cast__strings_with_numbers(self):
        for errors in ('cast', False):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NUMBERS,
                                   errors=errors)
            self.assertEquals(self.JOINED_WITH_CASTED_NUMBERS, joined)

    def test_errors__ignore__just_strings(self):
        for errors in ('ignore', None):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE,
                                   errors=errors)
            self.assertEquals(self.JOINED, joined)

    def test_errors__ignore__strings_with_nones(self):
        for errors in ('ignore', None):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NONES,
                                   errors=errors)
            self.assertEquals(self.JOINED, joined)

    def test_errors__ignore__strings_with_numbers(self):
        for errors in ('ignore', None):
            joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NUMBERS,
                                   errors=errors)
            self.assertEquals(self.JOINED, joined)

    def test_errors__replace__with_none(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, self.ITERABLE,
                          errors='replace', with_=None)

    def test_errors__replace__with_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.join(self.DELIMITER, self.ITERABLE,
                          errors='replace', with_=object())

    def test_errors__replace__just_strings__no_with(self):
        with self.assertRaises(ValueError) as r:
            __unit__.join(self.DELIMITER, self.ITERABLE, errors='replace')
        self.assertIn("with_", str(r.exception))

    def test_errors__replace__just_strings__with_string(self):
        joined = __unit__.join(self.DELIMITER, self.ITERABLE,
                               errors='replace', with_=self.STRING_REPLACEMENT)
        self.assertEquals(self.JOINED, joined)

    def test_errors__replace__strings_with_nones__with_string(self):
        joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NONES,
                               errors='replace', with_=self.STRING_REPLACEMENT)
        self.assertEquals(self.JOINED_WITH_REPLACEMENTS, joined)

    def test_errors__replace__strings_with_numbers__with_string(self):
        joined = __unit__.join(self.DELIMITER, self.ITERABLE_WITH_NUMBERS,
                               errors='replace', with_=self.STRING_REPLACEMENT)
        self.assertEquals(self.JOINED_WITH_REPLACEMENTS, joined)

    def test_errors__replace__just_strings__with_function(self):
        joined = __unit__.join(
            self.DELIMITER, self.ITERABLE,
            errors='replace', with_=self.FUNCTION_REPLACEMENT)
        self.assertEquals(self.JOINED, joined)

    def test_errors__replace__strings_with_nones__with_function(self):
        joined = __unit__.join(
            self.DELIMITER, self.ITERABLE_WITH_NONES,
            errors='replace', with_=self.FUNCTION_REPLACEMENT)
        self.assertEquals(self.JOINED_WITH_REPLACEMENTS, joined)

    def test_errors__replace__strings_with_numbers__with_function(self):
        joined = __unit__.join(
            self.DELIMITER, self.ITERABLE_WITH_NUMBERS,
            errors='replace', with_=self.FUNCTION_REPLACEMENT)
        self.assertEquals(self.JOINED_WITH_REPLACEMENTS, joined)


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
    HAYSTACK = "fooXbarXbazXbar"

    SIMPLE_NEEDLE = "foo"
    SIMPLE_REPLACEMENT = "blah"
    SIMPLE_RESULT = "blahXbarXbazXbar"

    LIST_NEEDLE = ("foo", "baz")
    LIST_REPLACEMENT = "thud"
    LIST_RESULT = "thudXbarXthudXbar"

    MAP_REPLACEMENTS = {"foo": "blah", "baz": "thud"}
    MAP_RESULT = "blahXbarXthudXbar"

    def test_needle__none(self):
        with self.assertRaises(TypeError) as r:
            __unit__.replace(None)
        self.assertIn("None", str(r.exception))

    def test_needle__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.replace(object())

    def test_needle__empty_string(self):
        with self.assertRaises(ValueError) as r:
            __unit__.replace('')
        self.assertIn("empty", str(r.exception))

    def test_needle__empty_iterable(self):
        with self.assertRaises(ValueError) as r:
            __unit__.replace([])
        self.assertIn("empty", str(r.exception))

    def test_needle__some_string(self):
        replacer = __unit__.replace(self.SIMPLE_NEEDLE)
        self._assertReplacer(replacer, [self.SIMPLE_NEEDLE])

    def test_needle__list(self):
        replacer = __unit__.replace(self.LIST_NEEDLE)
        self._assertReplacer(replacer, self.LIST_NEEDLE)

    def test_needle__mapping(self):
        replacer = __unit__.replace(self.MAP_REPLACEMENTS)
        self._assertReplacer(replacer, self.MAP_REPLACEMENTS)

    def test_replacement__omitted(self):
        replacer = __unit__.replace(self.SIMPLE_NEEDLE)
        self._assertReplacer(replacer, [self.SIMPLE_NEEDLE])

    def test_replacement__param__none(self):
        replacer = __unit__.replace(self.SIMPLE_NEEDLE, with_=None)
        self._assertReplacer(replacer, [self.SIMPLE_NEEDLE])

    def test_replacement__param__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.replace(self.SIMPLE_NEEDLE, with_=object())

    def test_replacement__param__empty_string(self):
        replacer = __unit__.replace(self.SIMPLE_NEEDLE, with_="")
        self._assertReplacer(replacer, {self.SIMPLE_NEEDLE: ""})

    def test_replacement__param__some_string(self):
        replacer = __unit__.replace(
            self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT)
        self._assertReplacer(replacer,
                             {self.SIMPLE_NEEDLE: self.SIMPLE_REPLACEMENT})

    def test_replacement__fluent__none(self):
        with self.assertRaises(TypeError):
            __unit__.replace(self.SIMPLE_NEEDLE).with_(None)

    def test_replacement__fluent__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.replace(self.SIMPLE_NEEDLE).with_(object())

    def test_replacement__fluent__empty_string(self):
        replacer = __unit__.replace(self.SIMPLE_NEEDLE).with_("")
        self._assertReplacer(replacer, {self.SIMPLE_NEEDLE: ""})

    def test_replacement__fluent__some_string(self):
        replacer = __unit__.replace(
            self.SIMPLE_NEEDLE).with_(self.SIMPLE_REPLACEMENT)
        self._assertReplacer(replacer,
                             {self.SIMPLE_NEEDLE: self.SIMPLE_REPLACEMENT})

    def test_replacement__duplicate__param_and_fluent(self):
        replacer = __unit__.replace(
            self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT)
        with self.assertRaises(__unit__.ReplacementError):
            replacer.with_(self.SIMPLE_REPLACEMENT)

    def test_replacement__duplicate__double_fluent(self):
        replacer = __unit__.replace(
            self.SIMPLE_NEEDLE).with_(self.SIMPLE_REPLACEMENT)
        with self.assertRaises(__unit__.ReplacementError):
            replacer.with_(self.SIMPLE_REPLACEMENT)

    def test_haystack__param__none(self):
        replacer = __unit__.replace(
            self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT, in_=None)
        self._assertReplacer(replacer,
                             {self.SIMPLE_NEEDLE: self.SIMPLE_REPLACEMENT})

    def test_haystack__param__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.replace(self.SIMPLE_NEEDLE,
                             with_=self.SIMPLE_REPLACEMENT, in_=object())

    def test_haystack__param__empty_string(self):
        result = __unit__.replace(
            self.SIMPLE_REPLACEMENT, with_=self.SIMPLE_REPLACEMENT, in_="")
        self.assertEquals("", result)

    def test_haystack__param__some_string(self):
        result = __unit__.replace(self.SIMPLE_NEEDLE,
                                  with_=self.SIMPLE_REPLACEMENT,
                                  in_=self.HAYSTACK)
        self.assertEquals(self.SIMPLE_RESULT, result)

    def test_haystack__fluent__none(self):
        with self.assertRaises(TypeError) as r:
            __unit__.replace(
                self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT).in_(None)
        self.assertIn("None", str(r.exception))

    def test_haystack__fluent__non_string(self):
        with self.assertRaises(TypeError):
            __unit__.replace(self.SIMPLE_NEEDLE,
                             with_=self.SIMPLE_REPLACEMENT).in_(object())

    def test_haystack__fluent__empty_string(self):
        result = __unit__.replace(
            self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT).in_("")
        self.assertEquals("", result)

    def test_haystack__fluent__some_string(self):
        result = __unit__.replace(
            self.SIMPLE_NEEDLE,
            with_=self.SIMPLE_REPLACEMENT).in_(self.HAYSTACK)
        self.assertEquals(self.SIMPLE_RESULT, result)

    def test_haystack__duplicate__param_and_fluent(self):
        result = __unit__.replace(self.SIMPLE_NEEDLE,
                                  with_=self.SIMPLE_REPLACEMENT,
                                  in_=self.HAYSTACK)
        with self._assertRaisesAttributeError('in_'):
            result.in_(self.HAYSTACK)

    def test_haystack__duplicate__double_fluent(self):
        result = __unit__.replace(
            self.SIMPLE_NEEDLE, with_=self.SIMPLE_REPLACEMENT).in_(
            self.HAYSTACK)
        with self._assertRaisesAttributeError('in_'):
            result.in_(self.HAYSTACK)

    def test_replace__simple(self):
        result = __unit__.replace(
            self.SIMPLE_NEEDLE).with_(
            self.SIMPLE_REPLACEMENT).in_(self.HAYSTACK)
        self.assertEquals(self.SIMPLE_RESULT, result)

    def test_replace__list(self):
        result = __unit__.replace(
            self.LIST_NEEDLE).with_(
            self.LIST_REPLACEMENT).in_(self.HAYSTACK)
        self.assertEquals(self.LIST_RESULT, result)

    def test_replace__mapping(self):
        result = __unit__.replace(self.MAP_REPLACEMENTS).in_(self.HAYSTACK)
        self.assertEquals(self.MAP_RESULT, result)

    # Utility functions

    def _assertReplacer(self, arg, replacements=None):
        self.assertIsInstance(arg, __unit__.Replacer)
        if replacements is not None:
            if is_mapping(replacements):
                self.assertEquals(replacements, arg._replacements)
            else:
                self.assertItemsEqual(replacements, arg._replacements)
                self.assertFalse(is_mapping(arg._replacements))

    @contextmanager
    def _assertRaisesAttributeError(self, attr=None):
        with self.assertRaises(AttributeError) as r:
            yield r
        if attr is not None:
            self.assertIn("'%s'" % attr, str(r.exception))


class Random(TestCase):
    LENGTH = 16
    MIN_LENGTH = 4
    MAX_LENGTH = 12
    LENGTH_RANGE = (MIN_LENGTH, MAX_LENGTH)
    NEGATIVE_LENGTH = -42

    CHARSET = 'foxjumps'

    def test_length__none(self):
        with self.assertRaises(TypeError):
            __unit__.random(None)

    def test_length__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.random(object())

    def test_length__negative(self):
        with self.assertRaises(ValueError) as r:
            __unit__.random(self.NEGATIVE_LENGTH)
        self.assertIn(str(self.NEGATIVE_LENGTH), str(r.exception))

    def test_length__invalid_tuple(self):
        with self.assertRaises(TypeError):
            __unit__.random((1, 2, 3))

    def test_length__constant(self):
        result = __unit__.random(self.LENGTH)
        self.assertEquals(self.LENGTH, len(result))

    def test_length__range(self):
        result = __unit__.random(self.LENGTH_RANGE)
        self.assertGreaterEqual(len(result), self.MIN_LENGTH)
        self.assertLessEqual(len(result), self.MAX_LENGTH)

    def test_chars__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.random(self.LENGTH, object())

    def test_chars__non_string_iterable(self):
        with self.assertRaises(TypeError):
            __unit__.random(self.LENGTH, ('a', 'b'))

    def test_chars__empty_string(self):
        with self.assertRaises(ValueError) as r:
            __unit__.random(self.LENGTH, '')
        self.assertIn("empty", str(r.exception))

    def test_chars__string(self):
        result = __unit__.random(self.LENGTH, self.CHARSET)
        for char in result:
            self.assertIn(char, self.CHARSET)
