"""
Common functions and function "factories".
"""
import operator

from taipan.functional import ensure_argcount, ensure_callable
from taipan.strings import ensure_string


__all__ = [
    'identity', 'const', 'true', 'false', 'none', 'zero', 'one', 'empty',
    'attr_func', 'key_func', 'item_func', 'dotcall',
]


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
