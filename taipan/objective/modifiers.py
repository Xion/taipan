"""
Modifiers ("annotation" decorators) for classes and class members.
"""
import abc
import inspect

from taipan.objective import _get_first_arg_name
from taipan.objective.base import (_ABCMetaclass, _ABCObjectMetaclass,
                                   ObjectMetaclass)
from taipan.objective.classes import metaclass
from taipan.objective.methods import ensure_method, is_method


__all__ = ['abstract', 'final', 'override']


# @abstract

def abstract(class_):
    """Mark the class as _abstract_ base class, forbidding its instantiation.

    .. note::

        Unlike other modifiers, ``@abstract`` can be applied
        to all Python classes, not just subclasses of :class:`Object`.

    .. versionadded:: 0.0.3
    """
    if not inspect.isclass(class_):
        raise TypeError("@abstract can only be applied to classes")

    # decide what metaclass to use, depending on whether it's a subclass
    # of our universal :class:`Object` or not
    if type(class_) is type:
        abc_meta = _ABCMetaclass  # like ABCMeta, but can never instantiate
    elif type(class_) is ObjectMetaclass:
        abc_meta = _ABCObjectMetaclass  # ABCMeta mixed with ObjectMetaclass
    else:
        raise ValueError(
            "@abstract cannot be applied to classes with custom metaclass")

    class_.__abstract__ = True
    return metaclass(abc_meta)(class_)

#: Alias for :func:`abc.abstractmethod` for marking abstract methods
#: inside abstract base classes.
abstract.method = abc.abstractmethod

#: Alias for :func:`abc.abstractproperty` for marking abstract properties
#: inside abstract base classes.
abstract.property = abc.abstractproperty


# @final

def final(arg):
    """Mark a class or method as _final_.

    Final classes are those that end the inheritance chain, i.e. forbid
    further subclassing. A final class can thus be only instantiated,
    not inherited from.

    Similarly, methods marked as final in a superclass cannot be overridden
    in any of the subclasses.

    .. note::

        Final method itself can also be (in fact, it usually is) an overridden
        method from a superclass. In those cases, it's recommended to place
        @\ :func:`final` modifier before @\ :func:`override` for clarity::

            class Foo(Base):
                @final
                @override
                def florb(self):
                    super(Foo, self).florb()
                    # ...

    .. versionadded:: 0.0.3
       Now applicable to methods in addition to classes
    """
    if inspect.isclass(arg):
        if not isinstance(arg, ObjectMetaclass):
            raise ValueError("@final can only be applied to a class "
                             "that is a subclass of Object")
    elif not is_method(arg):
        raise TypeError("@final can only be applied to classes or methods")

    method = arg.method if isinstance(arg, _OverriddenMethod) else arg
    method.__final__ = True

    return arg


# @override

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

    return _OverriddenMethod(method)


class _OverriddenMethod(object):
    """Wrapper for methods that have been marked with ``@override``.

    Those methods will be unpacked by :class:`ObjectMetaclass` during creation
    of the class which contains them.
    """
    def __init__(self, method):
        self.method = method

    # We proxy most operations to the underlying method to support the use case
    # when it's called / referenced / etc. even before its class is created.
    # An example would be a class attribute defined in terms of calling
    # an overridden class or static method.

    def __call__(self, *args, **kwargs):
        """Proxy calls to underlying method."""
        return self.method(*args, **kwargs)

    def __getattribute__(self, attr):
        """Proxy attribute access to underlying method."""
        if attr == 'method':
            return object.__getattribute__(self, attr)
        else:
            return getattr(self.method, attr)
