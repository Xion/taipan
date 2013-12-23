"""
List-related functions and classes.
"""
from taipan._compat import imap
from taipan.collections import ensure_sequence


__all__ = [
    'head', 'last', 'tail', 'init',
    'intersperse', 'intercalate', 'concat',
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
    return list(list_[1:])


def init(list_):
    """Returns all the elements of a list except the last one."""
    ensure_sequence(list_)
    return list(list_[:-1])


# List manipulation

# TODO(xion): implement intersperse() (insert single element between existing)
def intersperse(list_, elem):
    raise NotImplementedError()


# TODO(xion): implement intercalate() (insert sublist between existing items)
def intercalate(list_, elems):
    raise NotImplementedError()


def concat(list_):
    """Concatenates a list of lists into a single reslting list."""
    ensure_sequence(list_)
    return sum(imap(ensure_sequence, list_), [])

#: Alias for the :func:`concat` function.
join = concat
