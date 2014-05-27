"""
Collections-related functions and classes.
"""
from __future__ import absolute_import  # for importing built-in `collections`

import collections


__all__ = [
    'is_countable', 'is_iterable', 'is_mapping', 'is_ordered_mapping',
    'is_sequence', 'is_set', 'is_sized',
    'ensure_countable', 'ensure_iterable', 'ensure_mapping',
    'ensure_ordered_mapping', 'ensure_sequence', 'ensure_set', 'ensure_sized',
]


# Collection kind checks

def is_countable(obj):
    """Check whether given object is a countable collection (has a length).
    :return: ``True`` if argument has a length, ``False`` otherwise
    """
    return isinstance(obj, collections.Sized)


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


def is_ordered_mapping(obj):
    """Checks whether given object is an ordered mapping,
    e.g. a :class:`OrderedDict`.
    :return: ``True`` if argument is an ordered mapping, ``False`` otherwise
    """
    if not (is_mapping(obj) and hasattr(obj, '__reversed__')):
        return False

    # PyPy has a bug where the standard :class:`dict` has the ``__reversed__``
    # method but it's unusable and throws an exception when called
    try:
        obj.__reversed__()
    except TypeError:
        return False
    else:
        return True


def is_sequence(obj):
    """Checks whether given object is a sequence.
    :return: ``True`` if argument is a sequence, ``False`` otherwise
    """
    return isinstance(obj, collections.Sequence)


def is_set(obj):
    """Checks whether given object is a set.
    :return: ``True`` if argument is a set, ``False`` otherwise
    """
    return isinstance(obj, collections.Set)


#: Alias for :func:`is_countable`.
is_sized = is_countable


# Collection kind assertions

def ensure_countable(arg):
    """Check whether argument is a countable collection (has a length).
    :return: Argument, if it's a countable collection
    :raise TypeError: When argument is not a countable collection
    """
    if not is_countable(arg):
        raise TypeError(
            "expected a countable collection, got %s" % type(arg).__name__)
    return arg


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


def ensure_ordered_mapping(arg):
    """Checks whether argument is an ordered mapping.
    :return: Argument, if it's an ordered mapping
    :raise TypeError: When argument is not an ordered mapping
    """
    if not is_ordered_mapping(arg):
        raise TypeError(
            "expected an ordered mapping, got %s" % type(arg).__name__)
    return arg


def ensure_sequence(arg):
    """Checks whether given argument is a sequence.
    :return: Argument, if it's a sequence
    :raise TypeError: When argument is not a sequence
    """
    if not is_sequence(arg):
        raise TypeError("expected a sequence, got %s" % type(arg).__name__)
    return arg


def ensure_set(arg):
    """Checks whether given argument is a set.
    :return: Argument, if it's a set
    :raise TypeError: When argument is not a set
    """
    if not is_set(arg):
        raise TypeError("expected a set got, %s" % type(arg).__name__)
    return arg


#: Alias for :func:`ensure_countable`.
ensure_sized = ensure_countable
