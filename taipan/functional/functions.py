"""
Common functions and function "factories".
"""
import operator

from taipan.collections.lists import flatten
from taipan.functional import (ensure_argcount, ensure_callable,
                               ensure_keyword_args)
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

    :return: Function that always returns ``k``,
             regardless of what arguments, if any, were passed to it
    """
    return lambda *args, **kwargs: k


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

def attr_func(*attrs, **kwargs):
    """Creates an "attribute function" for given attribute name(s).

    Resulting function will retrieve attributes with given names, in order,
    from the object that has been passed to it.
    For example, ``attr_func('a', 'b')(foo)`` yields the same as ``foo.a.b``

    :param attrs: Attribute names
    :param default: Optional keyword argument specifying default value
                    that will be returned when some attribute is not present

    :return: Unary attribute function
    """
    ensure_argcount(attrs, min_=1)
    attrs = map(ensure_string, attrs)
    # TODO(xion): verify attribute names correctness

    # allow arguments with dots, interpreting them as multiple attributes,
    # e.g. ``attr_func('a.b')`` as ``attr_func('a', 'b')``
    attrs = flatten(attr.split('.') if '.' in attr else [attr]
                    for attr in attrs)

    ensure_keyword_args(kwargs, optional=('default',))

    if 'default' in kwargs:
        default = kwargs['default']
        if len(attrs) == 1:
            getattrs = lambda obj: getattr(obj, attrs[0], default)
        else:
            def getattrs(obj):
                for attr in attrs:
                    try:
                        obj = getattr(obj, attr)
                    except AttributeError:
                        return default
                return obj
    else:
        if len(attrs) == 1:
            getattrs = operator.attrgetter(attrs[0])
        else:
            def getattrs(obj):
                for attr in attrs:
                    obj = getattr(obj, attr)
                return obj

    return getattrs


def key_func(*keys, **kwargs):
    """Creates a "key function" based on given keys.

    Resulting function will perform lookup using specified keys, in order,
    on the object passed to it as an argument.
    For example, ``key_func('a', 'b')(foo)`` is equivalent to ``foo['a']['b']``.

    :param keys: Lookup keys
    :param default: Optional keyword argument specifying default value
                    that will be returned when some lookup key is not present

    :return: Unary key function
    """
    ensure_argcount(keys, min_=1)
    keys = list(map(ensure_string, keys))

    ensure_keyword_args(kwargs, optional=('default',))

    if 'default' in kwargs:
        default = kwargs['default']
        def getitems(obj):
            for key in keys:
                try:
                    obj = obj[key]
                except KeyError:
                    return default
            return obj
    else:
        if len(keys) == 1:
            getitems = operator.itemgetter(keys[0])
        else:
            def getitems(obj):
                for key in keys:
                    obj = obj[key]
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
