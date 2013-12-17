# ~*~ coding: utf-8 ~*~
"""
String-related functions and classes.
"""
import re

from taipan._compat import IS_PY3, imap
from taipan.collections import ensure_iterable, is_mapping
from taipan.collections.tuples import is_pair


__all__ = [
    'BaseString', 'UnicodeString', 'is_string', 'ensure_string',
    'join',
    'camel_case',
    'replace', 'ReplacementError',
]


#: Base string class used by this Python interpreter.
#:
#: For every string class X, the ``isubclass(X, BaseString)`` is always true.
#: (This includes the :class:`BaseString` itself.)
BaseString = str if IS_PY3 else basestring

#: Unicode string class used by this Python interpreter.
UnicodeString = str if IS_PY3 else unicode


def is_string(s):
    """Checks whether given object ``s`` is a string of characters.
    :return: ``True`` if ``s`` is a string, ``False`` otherwise
    """
    return isinstance(s, BaseString)


def ensure_string(s):
    """Checks whether ``s`` is a string of characters.
    :return: ``s`` if it is a string of characters
    :raises TypeError: When ``s` is not a string of characters
    """
    if not is_string(s):
        raise TypeError("expected a string, got %s" % type(s).__name__)
    return s


# Splitting and joining

def join(delimiter, iterable):
    """"Returns a string which is a concatenation of strings in ``iterable``,
    separated by given ``delimiter``.
    """
    # TODO(xion): add arg(s) that control handling Nones (skip/replace/error)
    ensure_string(delimiter)
    ensure_iterable(iterable)

    string_class = delimiter.__class__
    return delimiter.join(imap(string_class, iterable))


# Case conversion

def camel_case(arg, capitalize=None):
    """Converts given text with whitespaces between words
    into equivalent camel-cased one.

    :param capitalize: Whether result will have first letter upper case (True),
                       lower case (False), or left as is (None, default).

    :return: String turned into camel-case "equivalent"
    """
    if not arg:
        return arg
    ensure_string(arg)

    words = arg.split()
    first_word = words[0] if len(words) > 0 else None

    words = [word.capitalize() for word in words]
    if first_word is not None:
        if capitalize is True:
            first_word = first_word.capitalize()
        elif capitalize is False:
            first_word = first_word[0].lower() + first_word[1:]
        words[0] = first_word

    return join(arg, words)


# String replacement

def replace(needle, with_=None):
    """Replace occurrences of string(s) with other string(s) in (a) string(s).

    Unlike the built in :meth:`str.replace` method, this function provides
    clean API that clearly distinguishes the "needle" (string to replace),
    the replacement string, and the target string to perform replacement in
    (the "haystack").

    Additionally, a simultaneous replacement of several needles is possible.
    Note that this is different from performing multiple separate replacements
    one after another.

    Examples::

       replace('foo', 'bar').in_(text)
       replace('foo', with_='bar').in_(long_text)
       replace('foo').with_('bar').in_(long_text)
       replace(['foo', 'bar']).with_('baz').in_(long_text)
       replace({'foo': 'bar', 'baz': 'qud'}).in_(even_longer_text)

    :param needle: String to replace, iterable thereof,
                   or a mapping from needles to corresponding replacements
    :param with_: Replacement string, if ``needle`` was not a mapping
    """
    # TODO(xion): allow for regex needles
    if is_string(needle):
        replacer = Replacer((needle,))
    else:
        ensure_iterable(needle)
        if not is_mapping(needle):
            if all(imap(is_pair, needle)):
                needle = dict(needle)
            else:
                raise TypeError("invalid replacement needle")
        replacer = Replacer(needle)

    if with_ is not None:
        ensure_string(with_)
        replacer = replacer.with_(with_)

    # TODO(xion): add ``in_`` parameter for performing replacement immediately
    return replacer


class ReplacementError(Exception):
    """Exception raised when string replacement error occurrs."""


class Replacer(object):
    """Replaces occurrences of string(s) with some other string(s),
    within given string(s).

    This class handles both simple, single-pass replacements,
    as well as multiple replacement pair mappings.
    """
    def __init__(self, replacements):
        """Constructor.

        :param replacements: Iterable of needles, or mapping of replacements.

                             If this is not a mapping, a :meth:`with_` method
                             must be called to provide target replacement(s)
                             before :meth:`in_` is called
        """
        self._replacements = ensure_iterable(replacements)

    def with_(self, replacement):
        """Provide replacement for string "needles".

        :param replacement: Target replacement for needles given in constructor

        :raise TypeError: If ``replacement`` is not a string
        :raise ReplacementError: If replacement has been already given
        """
        ensure_string(replacement)
        if is_mapping(self._replacements):
            raise ReplacementError("string replacements already provided")

        self._replacements = dict.fromkeys(self._replacements, replacement)
        return self

    def in_(self, haystack):
        """Perform replacement in given string.

        :param haystack: String to perform replacements in

        :return: ``haystack`` after the replacements

        :raise TypeError: If ``haystack`` if not a string
        :raise ReplacementError: If no replacement(s) have been provided yet
        """
        ensure_string(haystack)
        if not is_mapping(self._replacements):
            raise ReplacementError("string replacements not provided")

        # handle special cases
        if not self._replacements:
            return haystack
        if len(self._replacements) == 1:
            return haystack.replace(*self._replacements.popitem())

        # construct a regex matching any of the needles in the order
        # of descending length (to prevent issues if they contain each other)
        or_ = haystack.__class__('|')
        regex = join(or_, imap(
            re.escape, sorted(self._replacements, key=len, reverse=True)))
        # TODO(xion): cache the regex & ``do_replace`` to speed up
        # multiple invocations of ``in_`` on the same replacer

        # do the substituion, looking up the replacement for every match
        do_replace = lambda match: self._replacements[match.group()]
        return re.sub(regex, do_replace, haystack)
