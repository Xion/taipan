"""
Combinators for constructing new functions from existing functions.
"""
import functools

from taipan._compat import imap
from taipan.collections import ensure_sequence, is_mapping
from taipan.functional import (
    ensure_argcount, ensure_callable, ensure_keyword_args)


__all__ = [
    'curry', 'uncurry', 'flip', 'compose', 'merge',
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

    result = lambda *args, **kwargs: f(*reversed(args), **kwargs)
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


def merge(arg, *rest, **kwargs):
    """Merge a collection, with functions as items, into a single function
    that takes a collection and maps its items through corresponding functions.

    :param arg: A collection of functions, such as list, tuple, or dictionary
    :param default: Optional default function to use for items
                    within merged function's arguments that do not have
                    corresponding functions in ``arg``

    Example with two-element tuple::

        >> dict_ = {'Alice': -5, 'Bob': 4}
        >> func = merge((str.upper, abs))
        >> dict(map(func, dict_.items()))
        {'ALICE': 5, 'BOB': 4}

    Example with a dictionary::

        >> func = merge({'id': int, 'name': str.split})
        >> data = [
            {'id': '1', 'name': "John Doe"},
            {'id': '2', 'name': "Anne Arbor"},
        ]
        >> list(map(func, data))
        [{'id': 1, 'name': ['John', 'Doe']},
         {'id': 2, 'name': ['Anne', 'Arbor']}]

    :return: Merged function

    .. versionadded:: 0.0.2
    """
    ensure_keyword_args(kwargs, optional=('default',))

    has_default = 'default' in kwargs
    if has_default:
        default = ensure_callable(kwargs['default'])

    # if more than one argument was given, they must all be functions;
    # result will be a function that takes multiple arguments (rather than
    # a single collection) and returns a tuple
    unary_result = True
    if rest:
        fs = (ensure_callable(arg),) + tuple(imap(ensure_callable, rest))
        unary_result = False
    else:
        fs = arg

    if is_mapping(fs):
        if has_default:
            return lambda arg_: fs.__class__((k, fs.get(k, default)(arg_[k]))
                                             for k in arg_)
        else:
            return lambda arg_: fs.__class__((k, fs[k](arg_[k]))
                                             for k in arg_)
    else:
        ensure_sequence(fs)
        if has_default:
            # we cannot use ``izip_longest(fs, arg_, fillvalue=default)``,
            # because we want to terminate the generator
            # only when ``arg_`` is exhausted (not when just ``fs`` is)
            func = lambda arg_: fs.__class__(
                (fs[i] if i < len(fs) else default)(x)
                for i, x in enumerate(arg_))
        else:
            # we cannot use ``izip(fs, arg_)`` because it would short-circuit
            # if ``arg_`` is longer than ``fs``, rather than raising
            # the required ``IndexError``
            func = lambda arg_: fs.__class__(fs[i](x)
                                             for i, x in enumerate(arg_))
        return func if unary_result else lambda *args: func(args)


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
