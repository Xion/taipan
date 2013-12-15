"""
Collections-related functions and classes.
"""
from __future__ import absolute_import  # for importing built-in `collections`

import collections


__all__ = [
    'is_iterable', 'is_mapping', 'is_sequence',
    'ensure_iterable', 'ensure_mapping', 'ensure_sequence',
]


# Collection kind checks

def is_iterable(obj):
    """Checks whether given object is an iterable.
    :return: ``True`` if argument is an iterable, ``False`` otherwise
    """
    return isinstance(obj, collections.Iterable)


def is_mapping(obj):
    """Checks whether given object is a mapping, e.g. a :class:`dict`.
    :return: ``True`` if argument is a mapping, ``False`` otherwise
    """
    return isinstance(obj, collections.Mapping)


def is_sequence(obj):
    """Checks whether given object is a sequence.
    :return: ``True`` if argument is a sequence, ``False`` otherwise
    """
    return isinstance(obj, collections.Sequence)


# Collection kind assertions

def ensure_iterable(arg):
    """Checks whether argument is an iterable.
    :return: Argument, if it's an iterable
    :raise TypeError: When argument is not an iterable
    """
    if not is_iterable(arg):
        raise TypeError("expected an iterable, got %s" % type(arg).__name__)
    return arg


def ensure_mapping(arg):
    """Checks whether given argument is a mapping, e.g. a :class:`dict`.
    :return: Argument, if it's a mapping
    :raise TypeError: When argument is not a mapping
    """
    if not is_mapping(arg):
        raise TypeError("expected a mapping, got %s" % type(arg).__name__)
    return arg


def ensure_sequence(arg):
    """Checks whether given argument is a sequence.
    :return: Argument, if it's a sequence
    :raise TypeError: When argument is not a sequence
    """
    if not is_sequence(arg):
        raise TypeError("expected a sequence, got %s" % type(arg).__name__)
    return arg
