"""
Dictionary-related functions and classes.
"""
from itertools import chain, starmap

from taipan._compat import IS_PY3, ifilter, imap, izip
from taipan.collections import ensure_iterable, ensure_mapping, is_mapping
from taipan.collections.sets import remove_subset
from taipan.functional import (ensure_argcount, ensure_callable,
                               ensure_keyword_args)
from taipan.functional.combinators import curry, compose
from taipan.functional.functions import dotcall, identity
import taipan.lang


__all__ = [
    'AbsentDict', 'ABSENT',
    'iteritems', 'iterkeys', 'itervalues', 'items', 'keys', 'values',
    'get', 'peekitem', 'select', 'pick', 'omit',
    'filteritems', 'starfilteritems', 'filterkeys', 'filtervalues',
    'mapitems', 'starmapitems', 'mapkeys', 'mapvalues',
    'merge', 'extend',
    'invert',
]


class AbsentDict(dict):
    """Improved dictionary that supports the special ``ABSENT`` value.

    Assigning the ``ABSENT`` value to key will remove the key from dictionary.
    Initializing a key with ``ABSENT`` value will result in key not being
    added to dictionary at all.

    Rationale is to eliminate 'ifs' which are sometimes needed when creating
    dictionaries e.g. when sometimes we want default value for keyword argument.

    Example::

        >> dicts.AbsentDict({
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
#: This is the same object as ``taipan.lang.ABSENT``.
ABSENT = taipan.lang.ABSENT


# Compatibility shims

# Helper function to call a method of a dictionary
_m = lambda method: compose(dotcall(method), ensure_mapping)

#: Return an iterator over key-value pairs stored within the dictionary.
iteritems = compose(iter, _m('items')) if IS_PY3 else _m('iteritems')

#: Return an iterator over keys stored within the dictionary.
iterkeys = compose(iter, _m('keys')) if IS_PY3 else _m('iterkeys')

#: Return an iterator over values stored within the dictionary
itervalues = compose(iter, _m('values')) if IS_PY3 else _m('itervalues')

#: Return a list of key-value pairs stored within the dictionary.
items = compose(list, _m('items')) if IS_PY3 else _m('items')

#: Return a list of keys stored within the dictionary.
keys = compose(list, _m('keys')) if IS_PY3 else _m('keys')

#: Return a list of values stored within the dictionary.
values = compose(list, _m('values')) if IS_PY3 else _m('values')


# Access functions

# TODO(xion): this may need a better name
def get(dict_, keys=(), default=None):
    """Extensions of standard :meth:`dict.get`.
    Retrieves an item from given dictionary, trying given keys in order.

    :param dict_: Dictionary to perform the lookup(s) in
    :param keys: Iterable of keys
    :param default: Default value to return if no key is found

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


def peekitem(dict_):
    """Return some item from the dictionary without modifying it.

    :param dict_: Dictionary to retrieve the item from
    :return: Pair of ``(key, value)`` from ``dict_``

    :raise KeyError: If the dictionary is empty

    .. versionadded:: 0.0.3
    """
    ensure_mapping(dict_)
    if not dict_:
        raise KeyError("peekitem(): dictionary is empty")
    return next(iteritems(dict_))


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


#: Alias for :func:`select`.
#: .. versionadded:: 0.0.2
pick = select


def omit(keys, from_, strict=False):
    """Returns a subset of given dictionary, omitting specified keys.

    :param keys: Iterable of keys to exclude
    :param strict: Whether ``keys`` are required to exist in the dictionary

    :return: Dictionary filtered by omitting ``keys``

    :raise KeyError: If ``strict`` is True and one of ``keys`` is not found
                     in the dictionary

    .. versionadded:: 0.0.2
    """
    ensure_iterable(keys)
    ensure_mapping(from_)

    if strict:
        remaining_keys = set(iterkeys(from_))
        remove_subset(remaining_keys, keys)  # raises KeyError if necessary
    else:
        remaining_keys = set(iterkeys(from_)) - set(keys)

    return from_.__class__((k, from_[k]) for k in remaining_keys)


# Filter functions

def filteritems(predicate, dict_):
    """Return a new dictionary comprising of items
    for which ``predicate`` returns True.

    :param predicate: Predicate taking a key-value pair, or None

    .. versionchanged: 0.0.2
       ``predicate`` is now taking a key-value pair as a single argument.
    """
    predicate = all if predicate is None else ensure_callable(predicate)
    ensure_mapping(dict_)
    return dict_.__class__(ifilter(predicate, iteritems(dict_)))


def starfilteritems(predicate, dict_):
    """Return a new dictionary comprising of keys and values
    for which ``predicate`` returns True.

    :param predicate: Predicate taking key and value, or None

    .. versionchanged:: 0.0.2
       Renamed ``starfilteritems`` for consistency with :func:`starmapitems`.
    """
    ensure_mapping(dict_)

    if predicate is None:
        predicate = lambda k, v: all((k, v))
    else:
        ensure_callable(predicate)

    return dict_.__class__((k, v) for k, v in iteritems(dict_)
                           if predicate(k, v))


def filterkeys(predicate, dict_):
    """Return a new dictionary comprising of keys
    for which ``predicate`` returns True, and their corresponding values.

    :param predicate: Predicate taking a dictionary key, or None
    """
    predicate = bool if predicate is None else ensure_callable(predicate)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in iteritems(dict_) if predicate(k))


def filtervalues(predicate, dict_):
    """Returns a new dictionary comprising of values
    for which ``predicate`` return True, and keys that corresponded to them.

    :param predicate: Predicate taking a dictionary value, or None
    """
    predicate = bool if predicate is None else ensure_callable(predicate)
    ensure_mapping(dict_)
    return dict_.__class__((k, v) for k, v in iteritems(dict_) if predicate(v))


# Mapping functions

def mapitems(function, dict_):
    """Return a new dictionary where the keys and values come from applying
    ``function`` to key-value pairs from given dictionary.

    .. warning::

        If ``function`` returns a key-value pair with the same key
        more than once, it is undefined which value will be chosen
        for that key in the resulting dictionary.

    :param function: Function taking a key-value pair as a single argument,
                     and returning a new key-value pair; or None
                     (corresponding to identity function)

    .. versionadded:: 0.0.2
    """
    ensure_mapping(dict_)
    function = identity() if function is None else ensure_callable(function)
    return dict_.__class__(imap(function, iteritems(dict_)))


def starmapitems(function, dict_):
    """Return a new dictionary where the keys and values come from applying
    ``function`` to the keys and values of given dictionary.

    .. warning::

        If ``function`` returns a key-value pair with the same key
        more than once, it is undefined which value will be chosen
        for that key in the resulting dictionary.

    :param function: Function taking key and value as two arguments
                     and returning a new key-value pair, or None
                     (corresponding to identity function)

    .. versionadded:: 0.0.2
    """
    ensure_mapping(dict_)

    if function is None:
        function = lambda k, v: (k, v)
    else:
        ensure_callable(function)

    return dict_.__class__(starmap(function, iteritems(dict_)))


def mapkeys(function, dict_):
    """Return a new dictionary where the keys come from applying ``function``
    to the keys of given dictionary.

    .. warning::

        If ``function`` returns the same value for more than one key,
        it is undefined which key will be chosen for the resulting dictionary.

    :param function: Function taking a dictionary key,
                     or None (corresponding to identity function)

    .. versionadded:: 0.0.2
    """
    ensure_mapping(dict_)
    function = identity() if function is None else ensure_callable(function)
    return dict_.__class__((function(k), v) for k, v in iteritems(dict_))


def mapvalues(function, dict_):
    """Return a new dictionary where the values come from applying ``function``
    to the values of given dictionary.

    :param function: Function taking a dictionary value,
                     or None (corresponding to identity function)

    .. versionadded:: 0.0.2
    """
    ensure_mapping(dict_)
    function = identity() if function is None else ensure_callable(function)
    return dict_.__class__((k, function(v)) for k, v in iteritems(dict_))


# Extending / combining dictionaries

def merge(*dicts, **kwargs):
    """Merges two or more dictionaries into a single one.

    Optional keyword arguments allow to control the exact way
    in which the dictionaries will be merged.

    :param overwrite:

        Whether repeated keys should have their values overwritten,
        retaining the last value, as per given order of dictionaries.
        This is the default behavior (equivalent to ``overwrite=True``).
        If ``overwrite=False``, repeated keys are simply ignored.

        Example::

            >> merge({'a': 1}, {'a': 10, 'b': 2}, overwrite=True)
            {'a': 10, 'b': 2}
            >> merge({'a': 1}, {'a': 10, 'b': 2}, overwrite=False)
            {'a': 1, 'b': 2}

    :param deep:

        Whether merging should proceed recursively, and cause
        corresponding subdictionaries to be merged into each other.
        By default, this does not happen (equivalent to ``deep=False``).

        Example::

            >> merge({'a': {'b': 1}}, {'a': {'c': 2}}, deep=False)
            {'a': {'c': 2}}
            >> merge({'a': {'b': 1}}, {'a': {'c': 2}}, deep=True)
            {'a': {'b': 1, 'c': 2}}

    :return: Merged dictionary

    .. note:: For ``dict``\ s ``a`` and ``b``, ``merge(a, b)`` is equivalent
              to ``extend({}, a, b)``.

    .. versionadded:: 0.0.2
       The ``overwrite`` keyword argument.
    """
    ensure_argcount(dicts, min_=1)
    dicts = list(imap(ensure_mapping, dicts))

    ensure_keyword_args(kwargs, optional=('deep', 'overwrite'))

    return _nary_dict_update(dicts, copy=True,
                             deep=kwargs.get('deep', False),
                             overwrite=kwargs.get('overwrite', True))


def extend(dict_, *dicts, **kwargs):
    """Extend a dictionary with keys and values from other dictionaries.

    :param dict_: Dictionary to extend

    Optional keyword arguments allow to control the exact way
    in which ``dict_`` will be extended.

    :param overwrite:

        Whether repeated keys should have their values overwritten,
        retaining the last value, as per given order of dictionaries.
        This is the default behavior (equivalent to ``overwrite=True``).
        If ``overwrite=False``, repeated keys are simply ignored.

        Example::

            >> foo = {'a': 1}
            >> extend(foo, {'a': 10, 'b': 2}, overwrite=True)
            {'a': 10, 'b': 2}
            >> foo = {'a': 1}
            >> extend(foo, {'a': 10, 'b': 2}, overwrite=False)
            {'a': 1, 'b': 2}

    :param deep:

        Whether extending should proceed recursively, and cause
        corresponding subdictionaries to be merged into each other.
        By default, this does not happen (equivalent to ``deep=False``).

        Example::

            >> foo = {'a': {'b': 1}}
            >> extend(foo, {'a': {'c': 2}}, deep=False)
            {'a': {'c': 2}}
            >> foo = {'a': {'b': 1}}
            >> extend(foo, {'a': {'c': 2}}, deep=True)
            {'a': {'b': 1, 'c': 2}}

    :return: Extended ``dict_``

    .. versionadded:: 0.0.2
    """
    ensure_mapping(dict_)
    dicts = list(imap(ensure_mapping, dicts))

    ensure_keyword_args(kwargs, optional=('deep', 'overwrite'))

    return _nary_dict_update([dict_] + dicts, copy=False,
                             deep=kwargs.get('deep', False),
                             overwrite=kwargs.get('overwrite', True))


def _nary_dict_update(dicts, **kwargs):
    """Implementation of n-argument ``dict.update``,
    with flags controlling the exact strategy.
    """
    copy = kwargs['copy']
    res = dicts[0].copy() if copy else dicts[0]
    if len(dicts) == 1:
        return res

    # decide what strategy to use when updating a dictionary
    # with the values from another: {(non)recursive} x {(non)overwriting}
    deep = kwargs['deep']
    overwrite = kwargs['overwrite']
    if deep:
        dict_update = curry(_recursive_dict_update, overwrite=overwrite)
    else:
        if overwrite:
            dict_update = res.__class__.update
        else:
            def dict_update(dict_, other):
                for k, v in iteritems(other):
                    dict_.setdefault(k, v)

    for d in dicts[1:]:
        dict_update(res, d)
    return res


def _recursive_dict_update(dict_, other, **kwargs):
    """Deep/recursive version of ``dict.update``.

    If a key is present in both dictionaries, and points to
    "child" dictionaries, those will be appropriately merged.

    :param overwrite: Whether to overwrite exisiting dictionary values
    """
    overwrite = kwargs['overwrite']

    for key, other_value in iteritems(other):
        if key in dict_:
            value = dict_[key]
            if is_mapping(value) and is_mapping(other_value):
                _recursive_dict_update(value, other_value, overwrite=overwrite)
                continue
        if overwrite:
            dict_[key] = other_value
        else:
            dict_.setdefault(key, other_value)


# Other transformation functions

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
