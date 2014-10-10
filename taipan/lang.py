"""
Core Python language utilties.

.. versionadded:: 0.0.2
"""
from __future__ import unicode_literals

import keyword
from numbers import Number
import re

from taipan._compat import IS_PY3, metaclass
from taipan.strings import ensure_string


__all__ = [
    'ABSENT',
    'cast',

    'is_contextmanager', 'is_number',
    'ensure_boolean', 'ensure_contextmanager', 'ensure_number',

    'has_identifier_form', 'is_identifier',
    'is_keyword',
    'is_magic', 'is_dunder',
]


# Absent value

class AbsentMetaclass(type):
    """Metaclass for the absent value class."""

    def __instancecheck__(self, instance):
        return False

    def __subclasscheck__(self, subclass):
        return False


@metaclass(AbsentMetaclass)
class Absent(object):
    """Absent value class.

    Instances (the only instance, really) of this class represent the lack
    of any value or object whatsoever. As such, magic methods of this class
    return falsy result, or are just omitted altogether.
    """
    def __new__(cls):
        if 'ABSENT' in globals():
            raise RuntimeError("only one absent value object may exist")
        return super(Absent, cls).__new__(cls)

    def __nonzero__(self):
        return False
    __bool__ = __nonzero__

    def __repr__(self):
        return ''


#: Unique object that indicates an absent (missing) value.
#:
#: It can be used as default value for optional arguments, among other things.
#: See also :class:`collections.dicts.AbsentDict`.
#:
#: .. versionadded:: 0.0.3
ABSENT = Absent()

del Absent
del AbsentMetaclass


# Type casting

def cast(type_, value, default=ABSENT):
    """Cast a value to given type, optionally returning a default, if provided.

    :param type_: Type to cast the ``value`` into
    :param value: Value to cast into ``type_``

    :return: ``value`` casted to ``type_``.
             If cast was unsuccessful and ``default`` was provided,
             it is returned instead.

    :raise AssertionError: When ``type_`` is not actually a Python type
    :raise TypeError: When cast was unsuccessful and no ``default`` was given
    """
    # ``type_`` not being a type would theoretically be grounds for TypeError,
    # but since that kind of exception is a valid and expected outcome here
    # in some cases, we use the closest Python has to compilation error instead
    assert isinstance(type_, type)

    # conunterintuitively, invalid conversions to numeric types
    # would raise ValueError rather than the more appropriate TypeError,
    # so we correct this inconsistency
    to_number = issubclass(type_, Number)
    exception = ValueError if to_number else TypeError

    try:
        return type_(value)
    except exception as e:
        if default is ABSENT:
            if to_number:
                # since Python 3 chains exceptions, we can supply slightly
                # more relevant error message while still retaining
                # the original information of ValueError as the cause
                msg = ("cannot convert %r to %r" % (value, type_) if IS_PY3
                       else str(e))
                raise TypeError(msg)
            else:
                raise
        return type_(default)


# Kind checks

def is_contextmanager(obj):
    """Checks whether given object is a context manager.,
    i.e. an object suitable for use with the ``with`` statement.
    :return: ``True`` if ``obj`` is a context manager, ``False`` otherwise
    """
    return hasattr(obj, '__exit__')


def is_number(obj):
    """Checks whether given object is a number.
    :return: ``True`` if ``obj`` is a number, ``False`` otherwise
    """
    return isinstance(obj, Number)


# Assertions

def ensure_boolean(arg):
    """Checks whether given argument is a boolean value.
    :return: Argument, if it's a boolean
    :raise TypeError: When argument is not a boolean

    .. versionadded:: 0.0.3
    """
    if not isinstance(arg, bool):
        raise TypeError("expected a boolean, got %s" % type(arg).__name__)
    return arg


def ensure_contextmanager(arg):
    """Checks whether argument is a context manager.
    :return: Argument, if it's a context manager
    :raise TypeError: When argument is not a context manager
    """
    if not is_contextmanager(arg):
        raise TypeError("expected a string, got %s" % type(arg).__name__)
    return arg


def ensure_number(arg):
    """Checks whether argument is a number.
    :return: Argument, if it's a number
    :raise TypeError: When argument is not a number
    """
    if not is_number(arg):
        raise TypeError("expected a number, got %s" % type(arg).__name__)
    return arg


# Language token classification

IDENTIFIER_FORM_RE = re.compile(r'^(?!\d)\w\w*$', re.UNICODE)


def has_identifier_form(s):
    """Check whether given string has a form of a Python identifier.

    Note that this includes Python language keywords, because they exhibit
    a general form of an identifier. See also :func:`is_identifier`.
    """
    ensure_string(s)
    return bool(IDENTIFIER_FORM_RE.match(s))


def is_identifier(s):
    """Check whether given string is a valid Python identifier.

    Note that this excludes language keywords, even though they exhibit
    a general form of an identifier. See also :func:`has_identifier_form`.

    :param s: String to check
    :return: Whether ``s`` is a valid Python identifier
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
