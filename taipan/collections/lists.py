"""
List-related functions and classes.
"""
from taipan._compat import imap, xrange
from taipan.collections import ensure_iterable, ensure_sequence


__all__ = [
    'head', 'last', 'tail', 'init',
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
