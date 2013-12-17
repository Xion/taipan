"""
Dictionary-related functions and classes.
"""
from taipan.collections import ensure_iterable, ensure_mapping


__all__ = ['get', 'merge', 'select']


# TODO(xion): this probably needs a better name
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


def select(keys, from_, strict=False):
    """Selects a subset of given dictionary, including only the specified keys.

    :param keys: Iterable of keys to include
    :param strict: Whether ``keys`` are required to exist in the dictionary.

    :raises KeyError: If ``strict`` is True and one of ``keys`` is not found
                      in the dictionary.
    """
    ensure_iterable(keys)
    ensure_mapping(from_)

    if strict:
        return dict((k, from_[k]) for k in keys)
    else:
        return dict((k, from_[k]) for k in keys if k in from_)
