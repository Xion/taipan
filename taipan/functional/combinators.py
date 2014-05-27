"""
Combinators for constructing new functions from existing functions.
"""
import functools

from taipan._compat import imap
from taipan.functional import ensure_argcount, ensure_callable


__all__ = [
    'curry', 'uncurry', 'flip', 'compose',
    'not_', 'and_', 'or_', 'nand', 'nor',
]


# General combinators

#: Alias for :func`functools.partial`.
curry = functools.partial


def uncurry(f):
    """Convert a curried function into a function on tuples
    (of positional arguments) and dictionaries (of keyword arguments).
    """
    ensure_callable(f)

    result = lambda args=(), kwargs=None: f(*args, **(kwargs or {}))
    functools.update_wrapper(result, f, ('__name__', '__module__'))
    return result


def flip(f):
    """Flip the order of positonal arguments of given function."""
    ensure_callable(f)

    result = lambda args=(), kwargs=None: f(*reversed(args), **(kwargs or {}))
    functools.update_wrapper(result, f, ('__name__', '__module__'))
    return result


def compose(*fs):
    """Creates composition of the functions passed in.

    :param fs: One-argument functions, with the possible exception of last one
               that can accept arbitrary arguments

    :return: Function returning a result of functions from ``fs``
             applied consecutively to the argument(s), in reverse order
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: f1(f2(*args, **kwargs))
    if len(fs) == 3:
        f1, f2, f3 = fs
        return lambda *args, **kwargs: f1(f2(f3(*args, **kwargs)))

    fs.reverse()

    def g(*args, **kwargs):
        x = fs[0](*args, **kwargs)
        for f in fs[1:]:
            x = f(x)
        return x

    return g


# Logical combinators

def not_(f):
    """Creates a function that returns a Boolean negative of provided function.

    :param f: Function to create a Boolean negative of

    :return: Function ``g`` such that ``g(<args>) == not f(<args>)``
             for any ``<args>``
    """
    ensure_callable(f)
    return lambda *args, **kwargs: not f(*args, **kwargs)


def and_(*fs):
    """Creates a function that returns true for given arguments
    iff every given function evalutes to true for those arguments.

    :param fs: Functions to combine

    :return: Short-circuiting function performing logical conjunction
             on results of ``fs`` applied to its arguments
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: (
            f1(*args, **kwargs) and f2(*args, **kwargs))
    if len(fs) == 3:
        f1, f2, f3 = fs
        return lambda *args, **kwargs: (
            f1(*args, **kwargs) and f2(*args, **kwargs) and f3(*args, **kwargs))

    def g(*args, **kwargs):
        for f in fs:
            if not f(*args, **kwargs):
                return False
        return True

    return g


def or_(*fs):
    """Creates a function that returns false for given arugments
    iff every given function evaluates to false for those arguments.

    :param fs: Functions to combine

    :return: Short-circuiting function performing logical alternative
             on results of ``fs`` applied to its arguments
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: (
            f1(*args, **kwargs) or f2(*args, **kwargs))
    if len(fs) == 3:
        f1, f2, f3 = fs
        return lambda *args, **kwargs: (
            f1(*args, **kwargs) or f2(*args, **kwargs) or f3(*args, **kwargs))

    def g(*args, **kwargs):
        for f in fs:
            if f(*args, **kwargs):
                return True
        return False

    return g


def nand(*fs):
    """Creates a function that returns false for given arguments
    iff every given function evalutes to true for those arguments.

    :param fs: Functions to combine

    :return: Short-circuiting function performing logical NAND operation
             on results of ``fs`` applied to its arguments
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return not_(fs[0])
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: not (
            f1(*args, **kwargs) and f2(*args, **kwargs))
    if len(fs) == 3:
        f1, f2, f3 = fs
        return lambda *args, **kwargs: not (
            f1(*args, **kwargs) and f2(*args, **kwargs) and f3(*args, **kwargs))

    def g(*args, **kwargs):
        for f in fs:
            if not f(*args, **kwargs):
                return True
        return False

    return g


def nor(*fs):
    """Creates a function that returns true for given arguments
    iff every given function evalutes to false for those arguments.

    :param fs: Functions to combine

    :return: Short-circuiting function performing logical NOR operation
             on results of ``fs`` applied to its arguments
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return not_(fs[0])
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: not (
            f1(*args, **kwargs) or f2(*args, **kwargs))
    if len(fs) == 3:
        f1, f2, f3 = fs
        return lambda *args, **kwargs: not (
            f1(*args, **kwargs) or f2(*args, **kwargs) or f3(*args, **kwargs))

    def g(*args, **kwargs):
        for f in fs:
            if f(*args, **kwargs):
                return False
        return True

    return g
