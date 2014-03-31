"""
Dictionary-related functions and classes.
"""
from itertools import chain

from taipan._compat import IS_PY3, imap, izip
from taipan.collections import ensure_iterable, ensure_mapping, is_mapping
from taipan.functional import (ensure_argcount, ensure_callable,
                               ensure_keyword_args)
from taipan.functional.combinators import compose


__all__ = [
    'AbsentDict', 'ABSENT',
    'iteritems', 'iterkeys', 'itervalues', 'items', 'keys', 'values',
    'get', 'select',
    'filteritems', 'filterkeys', 'filtervalues',
    'invert', 'merge',
]


class AbsentDict(dict):
    """Improved dictionary that supports a special ``ABSENT`` value.

    Assigning the ``ABSENT`` value to key will remove the key from dictionary.
    Initializing a key with ``ABSENT`` value will result in key not being
    added to dictionary at all.

    Rationale is to eliminate 'ifs' which are sometimes needed when creating
    dictionaries e.g. when sometimes we want default value for keyword argument.

    Example::

        >>> dicts.AbsentDict({
            'zero': 0 or dicts.ABSENT,
            'one': 1,
        })
        {'one': 1}
    """
    def __init__(self, iterable=(), **kwargs):
        if is_mapping(iterable):
            iterable = iteritems(iterable)
        super(AbsentDict, self).__init__(chain(
            ((k, v) for k, v in iterable if v is not ABSENT),
            ((k, v) for k, v in iteritems(kwargs) if v is not ABSENT)
        ))

    def __setitem__(self, key, obj):
        if obj is ABSENT:
            self.pop(key, None)
        else:
            super(AbsentDict, self).__setitem__(key, obj)


#: Value which indicates that its key is absent from :class:`AbsentDict`.
ABSENT = object()


# Compatibility shims

#: Return an iterator over key-value pairs stored within the dictionary.
iteritems = dict.items if IS_PY3 else dict.iteritems

#: Return an iterator over keys stored within the dictionary.
iterkeys = dict.keys if IS_PY3 else dict.iterkeys

#: Return an iterator over values stored within the dictionary
itervalues = dict.values if IS_PY3 else dict.itervalues

#: Return a list of key-value pairs stored within the dictionary.
items = compose(list, dict.items) if IS_PY3 else dict.items

#: Return a list of keys stored within the dictionary.
keys = compose(list, dict.keys) if IS_PY3 else dict.keys

#: Return a list of values stored within the dictionary.
values = compose(list, dict.values) if IS_PY3 else dict.values


# Access functions

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

    for key in keys:
        try:
            return dict_[key]
        except KeyError:
            pass

    return default


def select(keys, from_, strict=False):
    """Selects a subset of given dictionary, including only the specified keys.

    :param keys: Iterable of keys to include
    :param strict: Whether ``keys`` are required to exist in the dictionary.

    :return: Dictionary whose keys are a subset of given ``keys``

    :raise KeyError: If ``strict`` is True and one of ``keys`` is not found
                     in the dictionary.
    """
    ensure_iterable(keys)
    ensure_mapping(from_)

    if strict:
        return from_.__class__((k, from_[k]) for k in keys)
    else:
        existing_keys = set(keys) & set(iterkeys(from_))
        return from_.__class__((k, from_[k]) for k in existing_keys)


# Filter functions

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

    return dict_.__class__((k, v) for k, v in iteritems(dict_)
                           if function(k, v))


def filterkeys(function, dict_):
    """Return a new dictionary comprising of keys
    for which ``function`` returns True, and their corresponding values.

    :param function: Function taking a dictionary key, or None
    """
    function = bool if function is None else ensure_callable(function)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in iteritems(dict_) if function(k))


def filtervalues(function, dict_):
    """Returns a new dictionary comprising of values
    for which ``function`` return True, and keys that corresponded to them.

    :param function: Function taking a dictionary value, or None
    """
    function = bool if function is None else ensure_callable(function)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in iteritems(dict_) if function(v))


# Mutation functions

def invert(dict_):
    """Return an inverted dictionary, where former values are keys
    and former keys are values.

    .. warning::

        If more than one key maps to any given value in input dictionary,
        it is undefined which one will be chosen for the result.

    :param dict_: Dictionary to swap keys and values in
    :return: Inverted dictionary
    """
    ensure_mapping(dict_)
    return dict_.__class__(izip(itervalues(dict_), iterkeys(dict_)))


def merge(*dicts, **kwargs):
    """Merges two or more dictionaries into a single one.

    Repeated keys will retain their last values,
    as per given order of dictionaries.

    :param deep:

        Whether merging should proceed recursively, and cause
        corresponding subdictionaries to be merged into each other.

        Example::

            >> merge({'a': {'b': 1}}, {'a': {'c': 2}}, deep=False)
            {'a': {'c': 2}}
            >> merge({'a': {'b': 1}}, {'a': {'c': 2}}, deep=True)
            {'a': {'b': 1, 'c': 2}}

    :return: Merged dictionary
    """
    ensure_argcount(dicts, min_=1)
    dicts = list(imap(ensure_mapping, dicts))

    ensure_keyword_args(kwargs, optional=('deep',))

    res = dicts[0].copy()
    if len(dicts) == 1:
        return res

    deep = kwargs.get('deep', False)
    dict_update = _recursive_dict_update if deep else res.__class__.update

    for d in dicts[1:]:
        dict_update(res, d)
    return res


def _recursive_dict_update(one_dict, other_dict):
    """Deep/recursive version of ``dict.update``.

    If a key is present in both dictionaries, and points to
    "child" dictionaries, those will be appropriately merged.

    :return: First of the two dictionaries
    """
    result = one_dict  # first arg works like ``self`` in dict.update()

    for key, other_value in iteritems(other_dict):
        if key not in result:
            result[key] = other_value
            continue

        # only merge if both values are subdictionaries
        value = result[key]
        both_dicts = is_mapping(value) and is_mapping(other_value)
        if not both_dicts:
            result[key] = other_value
            continue

        _recursive_dict_update(value, other_value)

    return result
