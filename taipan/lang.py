"""
Core Python language utilties.
"""
from __future__ import unicode_literals

import keyword
import re

from taipan._compat import IS_PY3
from taipan.strings import ensure_string


__all__ = [
    'has_identifier_form', 'is_identifier',
    'is_keyword',
    'is_magic', 'is_dunder',
]


# Language token classification

IDENTIFIER_FORM_RE = re.compile(r'(?!\d)\w\w*', re.UNICODE)


def has_identifier_form(s):
    """Check whether given string has a form of a Python identifier.

    Note that this includes Python language keywords, because they exhibit
    a general form of an identifier. See also :func:`is_identifier`.

    .. versionadded:: 0.0.2
    """
    ensure_string(s)
    return bool(IDENTIFIER_FORM_RE.match(s))


def is_identifier(s):
    """Check whether given string is a valid Python identifier.

    Note that this excludes language keywords, even though they exhibit
    a general form of an identifier. See also :func:`has_identifier_form`.

    :param s: String to check
    :return: Whether ``s`` is a valid Python identifier

    .. versionadded:: 0.0.2
    """
    ensure_string(s)

    if not IDENTIFIER_FORM_RE.match(s):
        return False
    if is_keyword(s):
        return False

    # ``None`` is not part of ``keyword.kwlist`` in Python 2.x,
    # so we need to check for it explicitly
    if s == 'None' and not IS_PY3:
        return False

    return True


#: Check whether given string is a Python keyword.
is_keyword = keyword.iskeyword


def is_magic(s):
    """Check whether given string is a __magic__ Python identifier.
    :return: Whether ``s`` is a __magic__ Python identifier
    """
    if not is_identifier(s):
        return False
    return len(s) > 4 and s.startswith('__') and s.endswith('__')


#: Alias for :func:`is_magic`.
is_dunder = is_magic
