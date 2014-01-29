"""
Object-oriented programming utilities.
"""
import inspect

from taipan._compat import IS_PY26, IS_PY3
from taipan.functional import ensure_callable
from taipan.strings import is_string


__all__ = [
    'NonInstanceMethod', 'is_method', 'ensure_method', 'get_methods',
    'is_internal', 'is_magic',
    'Object', 'ObjectMetaclass', 'ClassError',
    'final', 'override',
]


# Method-related functions

#: Tuple of non-instance method types (class method & static method).
NonInstanceMethod = (classmethod, staticmethod)


def is_method(arg):
    """Checks whether given object is a method."""
    if inspect.ismethod(arg):
        return True
    if isinstance(arg, NonInstanceMethod):
        return True

    # Unfortunately, there is no disctinction between instance methods
    # that are yet to become part of a class, and regular functions.
    # We attempt to evade this little gray zone by relying on extremely strong
    # convention (which is nevertheless _not_ enforced by the intepreter)
    # that first argument of an instance method must be always named ``self``.
    if inspect.isfunction(arg):
        return _get_first_arg_name(arg) == 'self'

    return False


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
        OVERRIDE_EXEMPTIONS.update([
            '__eq__', '__ne__',
            '__ge__', '__gt__', '__le__', '__lt__',
        ])
    else:
        OVERRIDE_EXEMPTIONS.add('__unicode__')

    def __new__(meta, name, bases, dict_):
        """Creates a new class using this metaclass.
        Usually this means the class is inheriting from :class:`Object`.
        """
        # prevent class creation if any of its base classes is final
        for base in bases:
            if getattr(base, '__is_final', False):
                raise ClassError(
                    "cannot inherit from @final class %s" % (base.__name__,))

        class_ = type.__new__(meta, name, bases, dict_)

        # check for presence of ``@override`` on appropriate methods
        super_mro = class_.__mro__[1:]
        own_methods = ((name, member) for name, member in dict_.items()
                       if is_method(member))
        for name, method in own_methods:
            if IS_PY26 and isinstance(method, NonInstanceMethod):
                continue  # see TODO in :func:`override`
            shadows_base = any(hasattr(base, name) for base in super_mro)
            if meta._is_override(method):
                if not shadows_base:
                    raise ClassError("unnecessary @override on %s.%s" % (
                        class_.__name__, name))
            else:
                if shadows_base and name not in meta.OVERRIDE_EXEMPTIONS:
                    raise ClassError(
                        "overridden method %s.%s must be marked with @override"
                        % (class_.__name__, name))

        return class_

    @classmethod
    def _is_override(meta, method):
        """Checks whether given class or instance method has been marked
        with the ``@override`` decorator.
        """
        func = method.__func__ \
            if isinstance(method, NonInstanceMethod) \
            else method
        return getattr(func, '__is_override', False)


# We can't use a regular ``class`` block to define :class:`Object`
# because syntax for metaclasses differ between Python 2.x and 3.x.
Object = ObjectMetaclass('Object', (object,), {
    '__doc__': """
    Universal base class for objects.

    Inheriting from this class rather than the standard :class:`object`
    will grant access to additional object-oriented features.
    """,
})


class ClassError(Exception):
    """Exception raised when the class definition of :class:`Object` subclass
    is found to be incorrect.
    """


def final(class_):
    """Mark a class as _final_, forbidding any more class from
    inheriting from it (subclassing it).
    """
    if not inspect.isclass(class_):
        raise TypeError("@final can only be applied to classes")
    if not isinstance(class_, ObjectMetaclass):
        raise ValueError("@final can only be applied to subclasses of Object")

    class_.__is_final = True
    return class_


def override(method):
    """Mark a method as overriding a corresponding method from superclass.

    .. note::

        When overriding a :class:`classmethod`, remember to place ``@override``
        above the ``@classmethod`` decorator::

            class Foo(Bar):
                @override
                @classmethod
                def florb(cls):
                    pass
    """
    try:
        ensure_method(method)
    except TypeError:
        # in case user mixed up the order of ``@override`` and ``@classmethod``,
        # we can detect the issue and provide a targeted exception message
        if inspect.isfunction(method) and _get_first_arg_name(method) == 'cls':
            raise TypeError("@override must be applied above @classmethod")
        else:
            raise

    # non-instance methods do not allow setting attributes on them,
    # so we mark the underlying raw functions instead
    if isinstance(method, NonInstanceMethod):
        # TODO(xion): support @override on non-instance methods in Python 2.6
        # by introducing custom subclasses of classmethod and staticmethod
        # where we would store the __is_override flag
        if IS_PY26:
            raise NotImplementedError("@override on non-instance methods "
                                      "is not supported in Python 2.6")
        method.__func__.__is_override = True
    else:
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


def _get_first_arg_name(function):
    argnames, _, _, _ = inspect.getargspec(function)
    return argnames[0] if argnames else None
