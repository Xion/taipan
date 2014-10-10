"""
Class related functions and utilities.
"""
import inspect

from taipan._compat import metaclass
from taipan.algorithms import breadth_first
from taipan.api.decorators import _wrap_decorator
from taipan.functional.combinators import and_, not_


__all__ = [
    'is_class', 'ensure_class',
    'iter_subclasses', 'iter_superclasses',
    'is_metaclass', 'ensure_metaclass',
    'metaclass',
]


# Class checks and assetions

#: Alias for ``inspect.isclass``
is_class = inspect.isclass


def ensure_class(arg):
    """Check whether argument is a class.
    :return: Argument, if it's a class
    :raise TypeError: When argument is not a class
    """
    if not is_class(arg):
        raise TypeError(
            "expected a class, got %s instead" % type(arg).__name__)
    return arg


def iter_subclasses(class_):
    """Iterate over all the subclasses (and subclasses thereof, etc.)
    of given class.

    :param class_: Class to yield the subclasses of
    :return: Iterable of subclasses, sub-subclasses, etc. of ``class_``
    """
    ensure_class(class_)

    classes = set()

    def descend(class_):
        subclasses = set(class_.__subclasses__()) - classes
        classes.update(subclasses)
        return subclasses

    result = breadth_first(class_, descend)
    next(result)  # omit ``class_`` itself
    return result


def iter_superclasses(class_):
    """Iterate over all the superclasses (and superclasses thereof, etc.)
    of given class.

    :param class_: Class to yield the superclasses of
    :return: Iterable of superclasses, super-superclasses, etc. of ``class_``

    .. note::

        In most cases, the result of :func:`iter_superclasses` is the same as
        ``class_.__mro__``, except when the method resolution order
        has been customized by the metaclass of ``class_``.
    """
    ensure_class(class_)

    classes = set()

    def ascend(class_):
        superclasses = set(class_.__bases__) - classes
        classes.update(superclasses)
        return superclasses

    result = breadth_first(class_, ascend)
    next(result)  # omit ``class_`` itself
    return result


# Metaclass utilities

def is_metaclass(obj):
    """Checks whether given object is a metaclass.
    :return: ``True`` if object is a metaclass, ``False`` otherwise
    """
    return issubclass(obj, type)


def ensure_metaclass(arg):
    """Check whether argument is a metaclass.
    :return: Argument, if it's a metaclass
    :raise TypeError: When argument is not a metaclass
    """
    if not is_metaclass(arg):
        raise TypeError(
            "expected a metaclass, got %s instead" % type(arg).__name__)
    return arg


# Expose the :class:`metaclass` decorator after augmenting it with type checks.
metaclass = _wrap_decorator(metaclass, "non-meta classes",
                            and_(inspect.isclass, not_(is_metaclass)))
metaclass.__name__ = 'metaclass'
