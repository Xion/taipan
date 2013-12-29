"""
Functional utilities.
"""
import functools

from taipan._compat import imap
from taipan.collections import ensure_iterable


def ensure_callable(arg):
    """Checks whether given object is a callable.
    :return: Argument if it's a callable
    :raise TypeError: When argument is not a callable
    """
    if not callable(arg):
        raise TypeError("expected a callable, got %s" % type(arg).__name__)
    return arg


def ensure_argcount(args, min_=None, max_=None):
    """Checks whether iterable of positional arguments satisfies condictions.

    :param args: Iterable of positional arguments, received via ``*args``
    :param min_: Minimum number of arguments
    :param max_: Maximum number of arguments

    :return: ``args`` if the conditions are met
    :raise TypeError: When conditions are not met
    """
    ensure_iterable(args)

    has_min = min_ is not None
    has_max = max_ is not None
    if not (has_min or has_max):
        raise ValueError(
            "minimum and/or maximum number of arguments must be provided")
    if has_min and has_max and min_ > max_:
        raise ValueError(
            "maximum number of arguments must be greater or equal to minimum")

    if has_min and len(args) < min_:
        raise TypeError(
            "expected at least %s arguments, got %s" % (min_, len(args)))
    if has_max and len(args) > max_:
        raise TypeError(
            "expected at most %s arguments, got %s" % (max_, len(args)))

    return args


# Comstant functions

def identity():
    """Returns an identity function.
    :return: Function that returns the argument passed in verbatim
    """
    return lambda x: x


def const(k):
    """Creates a function that always returns the same value.
    :param k: Value that resulting function will always return
    :return: Function that takes no arguments and always returns ``k``
    """
    return lambda: k


def true():
    """Creates a function that always returns ``True``."""
    return const(True)


def false():
    """Creates a function that always return ``False``."""
    return const(False)


def none():
    """Creates a function that always returns ``None``."""
    return const(None)


def zero():
    """Creates a function that always returns 0."""
    return const(0)


def one():
    """Creates a function that always returns 1."""
    return const(1)


def empty():
    """Creates a function that always returns an empty iterable."""
    return const(())


# General combinators

curry = functools.partial


def uncurry(f):
    """Convert a curried function into a function on tuples
    (of positional arguments) and dictionaries (of keyword arguments).
    """
    ensure_callable(f)

    result = lambda args=(), kwargs=None: f(*args, **(kwargs or {}))
    functools.update_wrapper(result, f, ('__name__', '__module__'))
    return result


def compose(*fs):
    """Creates composition of the functions passed in.

    :param fs: One-argument functions
    :return: Function returning a result of functions from ``fs``
             applied consecutively to its argument in reverse order
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda *args, **kwargs: f1(f2(*args, **kwargs))

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
    :return: Function ``g`` such that ``g(x) == not f(x)`` for every ``x``
    """
    ensure_callable(f)
    return lambda x: not f(x)


def and_(*fs):
    """Creates a function that returns true for an argument
    if every given function evalutes to true for that argument.

    :param fs: One-argument functions
    :return: Short-circuiting function performing logical conjunction
             on results of ``fs`` applied to its argument
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda x: f1(x) and f2(x)

    def g(x):
        for f in fs:
            if not f(x):
                return False
        return True

    return g


def or_(*fs):
    """Creates a function that returns false for an argument
    if every given function evaluates to false for that argument.

    :param fs: One-argument functions
    :return: Short-circuiting function performing logical alternative
             on results of ``fs`` applied to its argument
    """
    ensure_argcount(fs, min_=1)
    fs = list(imap(ensure_callable, fs))

    if len(fs) == 1:
        return fs[0]
    if len(fs) == 2:
        f1, f2 = fs
        return lambda x: f1(x) or f2(x)

    def g(x):
        for f in fs:
            if f(x):
                return True
        return False

    return g
