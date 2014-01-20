"""
Object-oriented programming utilities.
"""
import inspect

from taipan._compat import IS_PY3
from taipan.functional import ensure_callable
from taipan.strings import is_string


__all__ = [
    'is_method', 'ensure_method', 'get_methods',
    'is_internal', 'is_magic',
    'Object', 'ObjectMetaclass', 'ClassError',
    'override',
]


# Method-related functions

def is_method(arg):
    """Checks whether given object is a class or instance method."""
    # in Python 3, methods in class are ordinary functions,
    # but in Python 2 they are special "bound method" objects
    predicate = inspect.isfunction if IS_PY3 else inspect.ismethod
    return predicate(arg)


def ensure_method(arg):
    """Checks whether given object is a class or instance method
    :return: Argument if it's a method
    :raise TypeError: When argument is not a method
    """
    if not is_method(arg):
        raise TypeError("expected a method, got %s" % type(arg).__name__)
    return arg


def get_methods(class_):
    """Retrieve all methods of a class."""
    return inspect.getmembers(class_, is_method)


# Class member checks

def is_internal(member):
    """Checks whether given class/instance member, or its name, is internal."""
    name = _get_member_name(member)
    return name.startswith('_') and not is_magic(name)


def is_magic(member):
    """Checks whether given class/instance member, or its name, is "magic".

    Magic fields and methods have names that begin and end
    with double underscores, such ``__hash__`` or ``__eq__``.
    """
    name = _get_member_name(member)
    return len(name) > 4 and name.startswith('__') and name.endswith('__')


# Universal base class for objects

class ObjectMetaclass(type):
    """Metaclass for the :class:`Object` class.

    Using this metaclass (typically by inheriting from :class:`Object`)
    will grant access to additional object-oriented features.
    """
    #: Methods exempt from ``@override`` requirement.
    #: Note that not all magic method names are includes, but only those
    #: that are by default present in :class:`object`
    OVERRIDE_EXEMPTIONS = set([
        '__delattr__', '__getattr__', '__getattribute__', '__setattr__',
        '__format__', '__hash__', '__repr__',  '__str__',
        '__init__', '__new__',
        '__reduce__', '__reduce_ex__', '__sizeof__',
        '__instancehook__', '__subclasshook__',
    ])
    if IS_PY3:
        OVERRIDE_EXEMPTIONS.add('__unicode__')
    else:
        OVERRIDE_EXEMPTIONS.update([
            '__eq__', '__ne__',
            '__ge__', '__gt__', '__le__', '__lt__',
        ])

    def __new__(meta, name, bases, dict_):
        """Creates a new class using this metaclass.
        Usually this means the class is inheriting from :class:`Object`.
        """
        class_ = type.__new__(meta, name, bases, dict_)

        # check for presence of ``@override`` on appropriate methods
        super_mro = class_.__mro__[1:]
        for name, method in get_methods(class_):
            if name in meta.OVERRIDE_EXEMPTIONS:
                continue
            if any(hasattr(base, name) for base in super_mro):
                is_override = getattr(method, '__is_override', False)
                if not is_override:
                    raise ClassError(
                        "overridden method %s.%s must be marked with @override"
                        % (class_.__name__, name))

        return class_


class Object(object):
    """Universal base class for objects.

    Inheriting from this class rather than the standard :class:`object`
    will grant access to additional object-oriented features.
    """
    __metaclass__ = ObjectMetaclass


class ClassError(Exception):
    """Exception raised when the class definition of :class:`Object` subclass
    is found to be incorrect.
    """


def override(method):
    """Mark a method as overriding a corresponding method from superclass."""
    ensure_callable(method)
    method.__is_override = True
    return method


# Utility functions

def _get_member_name(member):
    if is_string(member):
        return member

    # Python has no "field declaration" objects, so the only valid
    # class or instance member is actually a method
    ensure_method(member)
    return member.__name__
