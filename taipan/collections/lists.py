"""
List-related functions and classes.
"""
import sys

from taipan._compat import imap, xrange
from taipan.collections import ensure_iterable, ensure_sequence
from taipan.functional import ensure_callable, ensure_keyword_args


__all__ = [
    'head', 'last', 'tail', 'init',
    'index', 'lastindex',
    'intersperse', 'intercalate', 'concat', 'join', 'flatten',
]


# Element access

def head(list_):
    """Returns head of a list, i.e. it's first element."""
    ensure_sequence(list_)
    return list_[0]


def last(list_):
    """Returns last element of a list."""
    ensure_sequence(list_)
    return list_[-1]


def tail(list_):
    """Returns tail of a list (all elements without the first one)."""
    ensure_sequence(list_)
    if not list_:
        raise ValueError("can't tail an empty list")
    return list(list_[1:])


def init(list_):
    """Returns all the elements of a list except the last one."""
    ensure_sequence(list_)
    if not list_:
        raise ValueError("can't extract initial part of an empty list")
    return list(list_[:-1])


# Searching for elements

def index(*args, **kwargs):
    """Search a list for an exact element, or element satisfying a predicate.

    Usage::

        index(element, list_)
        index(of=element, in_=list_)
        index(where=predicate, in_=list_)

    :param element, of: Element to search for
    :param where: Predicate defining an element to search for.
                  This should be a callable taking a single argument
                  and returning a boolean result.
    :param list_, in_: List to search in

    :return: Index of first matching element, or -1 if none was found

    .. versionadded:: 0.0.3
    """
    return _index(*args, start=0, step=1, **kwargs)


def lastindex(*args, **kwargs):
    """Search a list backwards for an exact element,
    or element satisfying a predicate.

    Usage::

        lastindex(element, list_)
        lastindex(of=element, in_=list_)
        lastindex(where=predicate, in_=list_)

    :param element, of: Element to search for
    :param where: Predicate defining an element to search for.
                  This should be a callable taking a single argument
                  and returning a boolean result.
    :param list_, in_: List to search in

    :return: Index of the last matching element, or -1 if none was found

    .. versionadded:: 0.0.3
    """
    return _index(*args, start=sys.maxsize, step=-1, **kwargs)


def _index(*args, **kwargs):
    """Implementation of list searching.

    :param of: Element to search for
    :param where: Predicate to search for
    :param in_: List to search in
    :param start: Start index for the lookup
    :param step: Counter step (i.e. in/decrement) for each iteration

    :return: Index of the first element found, or -1
    """
    start = kwargs.pop('start', 0)
    step = kwargs.pop('step', 1)

    if len(args) == 2:
        elem, list_ = args
        ensure_sequence(list_)
        predicate = lambda item: item == elem
    else:
        ensure_keyword_args(kwargs,
                            mandatory=('in_',), optional=('of', 'where'))
        if 'of' in kwargs and 'where' in kwargs:
            raise TypeError(
                "either an item or predicate must be supplied, not both")
        if not ('of' in kwargs or 'where' in kwargs):
            raise TypeError("an item or predicate must be supplied")

        list_ = ensure_sequence(kwargs['in_'])
        if 'where' in kwargs:
            predicate = ensure_callable(kwargs['where'])
        else:
            elem = kwargs['of']
            predicate = lambda item: item == elem

    len_ = len(list_)
    start = max(0, min(len_ - 1, start))

    i = start
    while 0 <= i < len_:
        if predicate(list_[i]):
            return i
        i += step
    else:
        return -1


# List manipulation

def intersperse(elem, list_):
    """"Intersperse an ``elem``\ ent between the elements of the ``list_``.

    :return: A new list where ``elem`` is inserted between
             every two elements of ``list_``
    """
    return intercalate([elem], list_)


def intercalate(elems, list_):
    """Insert given elements between existing elements of a list.

    :param elems: List of elements to insert between elements of ``list_`
    :param list_: List to insert the elements to

    :return: A new list where items from ``elems`` are inserted
             between every two elements of ``list_``
    """
    ensure_sequence(elems)
    ensure_sequence(list_)

    if len(list_) <= 1:
        return list_

    return sum(
        (elems + list_[i:i+1] for i in xrange(1, len(list_))),
        list_[:1])


def concat(list_):
    """Concatenates a list of lists into a single resulting list."""
    ensure_iterable(list_)

    # we don't use ``itertools.chain.from_iterable``, because that would
    # inadvertenly allow strings, treating them as lists of characters
    # and potentially producing very difficult bugs
    return sum(imap(ensure_sequence, list_), [])

#: Alias for the :func:`concat` function.
join = concat

#: Alias for the :func:`concat` function.
flatten = concat
