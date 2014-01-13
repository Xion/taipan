"""
Dictionary-related functions and classes.
"""
from taipan._compat import IS_PY3
from taipan.collections import ensure_iterable, ensure_mapping
from taipan.functional import ensure_callable


__all__ = [
    'filteritems', 'filterkeys', 'filtervalues',
    'get',
    'merge', 'select',
]


def filteritems(function, dict_):
    """Return a new dictionary comprising of items
    for which ``function`` returns True.

    :param function: Function taking key and value, or None
    """
    ensure_mapping(dict_)

    if function is None:
        function = lambda k, v: all((k, v))
    else:
        ensure_callable(function)

    return dict_.__class__((k, v) for k, v in _items(dict_) if function(k, v))


def filterkeys(function, dict_):
    """Return a new dictionary comprising of keys
    for which ``function`` returns True, and their corresponding values.

    :param function: Function taking a dictionary key, or None
    """
    function = bool if function is None else ensure_callable(function)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in _items(dict_) if function(k))


def filtervalues(function, dict_):
    """Returns a new dictionary comprising of values
    for which ``function`` return True, and keys that corresponded to them.

    :param function: Function taking a dictionary value, or None
    """
    function = bool if function is None else ensure_callable(function)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in _items(dict_) if function(v))


# TODO(xion): this may need a better name
def get(dict_, keys=(), default=None):
    """Extensions of standard :meth:`dict.get`.
    Retrieves an item from given dictionary, trying given keys in order.

    :param dict_: Dictionary to perform the lookup(s) in
    :param keys: Iterable of keys
    :param default: Default value to return if not key is found

    :return: Value for one of given ``keys``, or ``default``
    """
    ensure_mapping(dict_)
    ensure_iterable(keys)

    keys = list(keys)
    if not keys:
        return default

    for key in keys[:-1]:
        if key in dict_:
            return dict_[key]

    return dict_.get(keys[-1], default)


def merge(*dicts):
    """Merges two or more dictionaries into a single one.

    Repeated keys will retain their last values,
    as per given order of dictionaries.

    :return: Merged dictionary
    """
    res = {}
    for d in dicts:
        res.update(d)
    return res


def reverse(dict_):
    """Return a reversed dictionary, where former values are keys
    and former keys are values.

    .. warning::

        If more than one key maps to any given value in input dictionary,
        it is undefined which one will be chosen for the result.

    :param dict_: Dictionary to swap keys and values in
    :return: Reversed dictionary
    """
    ensure_mapping(dict_)
    return dict_.__class__((v, k) for k, v in _items(dict_))


def select(keys, from_, strict=False):
    """Selects a subset of given dictionary, including only the specified keys.

    :param keys: Iterable of keys to include
    :param strict: Whether ``keys`` are required to exist in the dictionary.

    :return: Dictionary whose keys are a subset of given ``keys``

    :raises KeyError: If ``strict`` is True and one of ``keys`` is not found
                      in the dictionary.
    """
    ensure_iterable(keys)
    ensure_mapping(from_)

    if strict:
        return from_.__class__((k, from_[k]) for k in keys)
    else:
        return from_.__class__((k, from_[k]) for k in keys if k in from_)


# Utility functions

_items = dict.items if IS_PY3 else dict.iteritems
_keys = dict.keys if IS_PY3 else dict.iterkeys
_values = dict.values if IS_PY3 else dict.itervalues
