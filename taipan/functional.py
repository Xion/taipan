"""
Functional programming utilities.
"""
import functools
import operator

from taipan._compat import imap
from taipan.collections import ensure_sequence
from taipan.strings import ensure_string


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
    ensure_sequence(args)

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


# Constant functions

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


# Unary functions

def attr_func(*attrs):
    """Creates an "attribute function" for given attribute name(s).

    Resulting function will retrieve attributes with given names, in order,
    from the object that has been passed to it.
    For example, ``attr_func('a', 'b')(foo)`` yields the same as ``foo.a.b``

    :param attrs: Attribute names
    :return: Unary attribute function
    """
    ensure_argcount(attrs, min_=1)
    attrs = list(map(ensure_string, attrs))
    # TODO(xion): verify attribute names correctness

    # TODO(xion): support arguments containing dots, e.g.
    # attr_func('a.b') instead of attr_func('a', 'b')

    if len(attrs) == 1:
        return operator.attrgetter(attrs[0])

    def getattrs(obj):
        for attr in attrs:
            obj = getattr(obj, attr)
        return obj

    return getattrs


def key_func(*keys):
    """Creates a "key function" based on given keys.

    Resulting function will perform lookup using specified keys, in order,
    on the object passed to it as an argument.
    For example, ``key_func('a', 'b')(foo)`` is equivalent to ``foo['a']['b']``.

    :param keys: Lookup keys
    :return: Unary key function
    """
    ensure_argcount(keys, min_=1)
    keys = list(map(ensure_string, keys))

    if len(keys) == 1:
        return operator.itemgetter(keys[0])

    def getitems(obj):
        for item in keys:
            obj = obj[item]
        return obj

    return getitems


#: Alias for :func:`key_func`.
item_func = key_func


def dotcall(name, *args, **kwargs):
    """Creates a function that accepts an object and invokes a member function
    (a "method") on it. The object can be a class instance, a class, a type,
    or even a module.

    :param name: Name of member function to invoke

    The rest of positional and keyword arguments will be passed
    to the member function as its parameters.

    :return: Unary function invoking member function ``name`` on its argument
    """
    ensure_string(name)

    get_member_func = attr_func(name)

    def call(obj):
        member_func = ensure_callable(get_member_func(obj))
        return member_func(*args, **kwargs)

    # through :func:`attr_func`, we may support ``name`` containing dots,
    # but we need to turn it into valid Python identifier for function's name
    call.__name__ = name.replace('.', '__')

    return call


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


def flip(f):
    """Flip the order of positonal arguments of given function."""
    ensure_callable(f)

    result = lambda args=(), kwargs=None: f(*reversed(args), **(kwargs or {}))
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

    :return: Function ``g`` such that ``g(<args>) == not f(<args>)``
             for any ``<args>``
    """
    ensure_callable(f)
    return lambda *args, **kwargs: not f(*args, **kwargs)


def and_(*fs):
    """Creates a function that returns true for given arguments
    if every given function evalutes to true for those arguments.

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

    def g(*args, **kwargs):
        for f in fs:
            if not f(*args, **kwargs):
                return False
        return True

    return g


def or_(*fs):
    """Creates a function that returns false for given arugments
    if every given function evaluates to false for those arguments.

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

    def g(*args, **kwargs):
        for f in fs:
            if f(*args, **kwargs):
                return True
        return False

    return g
