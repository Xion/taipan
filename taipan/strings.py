# ~*~ coding: utf-8 ~*~
"""
String-related functions and classes.
"""
from __future__ import absolute_import  # for importing standard `collections`

import collections

from taipan._compat import IS_PY3, imap


__all__ = [
    'BaseString', 'UnicodeString', 'is_string', 'ensure_string',
    'join',
    'camel_case',
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
    :raises TypeError: When ``s` is not a string of characters
    """
    if not is_string(s):
        raise TypeError("expected a string, got %s" % type(s).__name__)


# Splitting and joining

def join(delimiter, iterable):
    """"Returns a string which is a concatenation of strings in ``iterable``,
    separated by given ``delimiter``.
    """
    ensure_string(delimiter)

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
