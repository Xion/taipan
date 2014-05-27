"""
Tuple-related functions.

The functions handle tuples up to the length of five, as this is approximately
the point at which referring to elements by number ceases to be readable.

(There are only few quintuples in the Python standard library, for example,
with ``sys.version_info`` being perhaps the most well known one).
"""
from numbers import Integral

from taipan.collections import ensure_iterable, ensure_sequence


__all__ = [
    'is_tuple',
    'is_single', 'is_triple', 'is_quadruple', 'is_quintuple',
    'ensure_tuple',
    'ensure_single', 'ensure_triple', 'ensure_quadruple', 'ensure_quintuple',

    'first', 'second', 'third', 'fourth', 'fifth',
    'select',
]


# Tuple checks

def is_tuple(obj, len_=None):
    """Checks whether given object is a tuple.

    :param len_: Optional expected length of the tuple

    :return: ``True`` if argument is a tuple (of given length, if any),
             ``False`` otherwise
    """
    if not isinstance(obj, tuple):
        return False

    if len_ is None:
        return True
    if not isinstance(len_, Integral):
        raise TypeError(
            "length must be a number (got %s instead)" % type(len_).__name__)
    if len_ < 0:
        raise ValueError("length must be positive (got %s instead)" % len_)

    return len(obj) == len_


def is_single(obj):
    """Checks whether given object is a 1-element tuple.
    :return: ``True`` if argument is a 1-element tuple, ``False`` otherwise
    """
    return is_tuple(obj, len_=1)


def is_pair(obj):
    """Checks whether given object is a 2-element tuple.
    :return: ``True`` if argument is a 2-element tuple, ``False`` otherwise
    """
    return is_tuple(obj, len_=2)


def is_triple(obj):
    """Checks whether given object is a 3-element tuple.
    :return: ``True`` if argument is a 3-element tuple, ``False`` otherwise
    """
    return is_tuple(obj, len_=3)


def is_quadruple(obj):
    """Checks whether given object is a 4-element tuple.
    :return: ``True`` if argument is a 4-element tuple, ``False`` otherwise
    """
    return is_tuple(obj, len_=4)


def is_quintuple(obj):
    """Checks whether given object is a 5-element tuple.
    :return: ``True`` if argument is a 5-element tuple, ``False`` otherwise
    """
    return is_tuple(obj, len_=5)


# Tuple assertions

def ensure_tuple(arg, len_=None):
    """Checks whether argument is a tuple.
    :param len_: Optional expected length of the tuple
    :return: Argument, if it's a tuple (of given length, if any)
    :raise TypeError: When argument is not a tuple (of given length, if any)
    """
    if not is_tuple(arg, len_=len_):
        len_part = "" if len_ is None else " of length %s" % len_
        raise TypeError(
            "expected tuple%s, got %s" % (len_part, _describe_type(arg)))
    return arg


def ensure_single(arg):
    """Checks whether argument is a 1-element tuple.
    :return: Argument, if it's a 1-element tuple
    :raise TypeError: When argument is not a 1-element tuple
    """
    if not is_single(arg):
        raise TypeError(
            "expected a 1-element tuple, got %s" % _describe_type(arg))
    return arg


def ensure_pair(arg):
    """Checks whether argument is a 2-element tuple.
    :return: Argument, if it's a 2-element tuple
    :raise TypeError: When argument is not a 2-element tuple
    """
    if not is_pair(arg):
        raise TypeError(
            "expected a 2-element tuple, got %s" % _describe_type(arg))
    return arg


def ensure_triple(arg):
    """Checks whether argument is a 3-element tuple.
    :return: Argument, if it's a 3-element tuple
    :raise TypeError: When argument is not a 3-element tuple
    """
    if not is_triple(arg):
        raise TypeError(
            "expected a 3-element tuple, got %s" % _describe_type(arg))
    return arg


def ensure_quadruple(arg):
    """Checks whether argument is a 4-element tuple.
    :return: Argument, if it's a 4-element tuple
    :raise TypeError: When argument is not a 4-element tuple
    """
    if not is_quadruple(arg):
        raise TypeError(
            "expected a 4-element tuple, got %s" % _describe_type(arg))
    return arg


def ensure_quintuple(arg):
    """Checks whether argument is a 5-element tuple.
    :return: Argument, if it's a 5-element tuple
    :raise TypeError: When argument is not a 5-element tuple
    """
    if not is_quintuple(arg):
        raise TypeError(
            "expected a 5-element tuple, got %s" % _describe_type(arg))
    return arg


# Tuple access functions

def first(arg):
    """Returns the first element of a tuple (or other sequence)."""
    ensure_sequence(arg)
    return arg[0]


def second(arg):
    """Returns the second element of a tuple (or other sequence)."""
    ensure_sequence(arg)
    return arg[1]


def third(arg):
    """Returns the third element of a tuple (or other sequence)."""
    ensure_sequence(arg)
    return arg[2]


def fourth(arg):
    """Returns the fourth element of a tuple (or other sequence)."""
    ensure_sequence(arg)
    return arg[3]


def fifth(arg):
    """Returns the fifth element of a tuple (or other sequence)."""
    ensure_sequence(arg)
    return arg[4]


def select(indices, from_, strict=False):
    """Selects a subsequence of given tuple, including only specified indices.

    :param indices: Iterable of indices to include
    :param strict: Whether ``indices`` are required to exist in the tuple.

    :return: Tuple with selected elements, in the order corresponding
             to the order of ``indices``.

    :raise IndexError: If ``strict`` is True and one of ``indices``
                       is out of range.
    """
    ensure_iterable(indices)
    ensure_sequence(from_)

    if strict:
        return from_.__class__(from_[index] for index in indices)
    else:
        len_ = len(from_)
        return from_.__class__(from_[index] for index in indices
                               if 0 <= index < len_)


# Utility functions

def _describe_type(arg):
    """Describe given argument, including length if it's a tuple.

    The purpose is to prevent nonsensical exception messages such as::

        expected a tuple of length 2, got tuple
        expected a tuple, got tuple

    by turning them into::

        expected a tuple of length 3, got tuple of length 2
    """
    if isinstance(arg, tuple):
        return "tuple of length %s" % len(arg)
    else:
        return type(arg).__name__
