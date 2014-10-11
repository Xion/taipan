"""
Modifiers ("annotation" decorators) for classes and class members.
"""
import abc
import inspect

from taipan.lang import ABSENT
from taipan.objective import _get_first_arg_name
from taipan.objective.base import (_ABCMetaclass, _ABCObjectMetaclass,
                                   ObjectMetaclass)
from taipan.objective.classes import is_class, metaclass
from taipan.objective.methods import ensure_method, is_method, NonInstanceMethod
from taipan.strings import is_string


__all__ = ['abstract', 'final', 'override']


class _WrappedMethod(object):
    """Wrapper for methods that have been marked with a modifier.

    Those methods will be unpacked by :class:`ObjectMetaclass` during creation
    of the class that contains them.
    """
    __slots__ = ['method', 'modifier']

    def __init__(self, method, modifier=None):
        self.method = method
        self.modifier = modifier

    # We proxy most operations to the underlying method to support the use case
    # when it's called / referenced / etc. even before its class is created.
    # An example would be a class attribute defined in terms of calling
    # an overridden class or static method.

    def __call__(self, *args, **kwargs):
        """Proxy calls to underlying method."""
        return self.method(*args, **kwargs)

    def __getattribute__(self, attr):
        """Proxy attribute access to underlying method."""
        if attr in _WrappedMethod.__slots__:
            return object.__getattribute__(self, attr)
        else:
            return getattr(self.method, attr)


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

    method = arg.method if isinstance(arg, _WrappedMethod) else arg
    method.__final__ = True

    return arg


# @override

def override(base=ABSENT):
    """Mark a method as overriding a corresponding method from superclass.

    :param base:

        Optional base class from which this method is being overridden.
        If provided, it can be a class itself, or its (qualified) name.

    .. note::

        When overriding a :class:`classmethod`, remember to place ``@override``
        above the ``@classmethod`` decorator::

            class Foo(Bar):
                @override
                @classmethod
                def florb(cls):
                    pass
    """
    arg = base  # ``base`` is just for clean, user-facing argument name

    # direct application of the modifier through ``@override``
    if inspect.isfunction(arg) or isinstance(arg, NonInstanceMethod):
        _OverrideDecorator.maybe_signal_classmethod(arg)
        decorator = _OverrideDecorator(None)
        return decorator(arg)

    # indirect (but simple) application of the modifier through ``@override()``
    if arg is ABSENT:
        return _OverrideDecorator(None)

    # full-blown application, with base class specified
    if is_class(arg) or is_string(arg):
        return _OverrideDecorator(arg)

    raise TypeError("explicit base class for @override "
                    "must be either a string or a class object")


class _OverrideDecorator(object):
    """Decorator for applying the ``@override`` modifier.
    This should not be used directly -- use :func:`override` instead.
    """
    def __init__(self, base):
        self.base = base

    def __call__(self, method):
        try:
            ensure_method(method)
        except TypeError:
            if not _OverrideDecorator.maybe_signal_classmethod(method):
                raise

        return _OverriddenMethod(method, self)  # remember the override's base

    @staticmethod
    def maybe_signal_classmethod(method):
        """Signal the case when user mixed up the order of ``@override`` and
        ``@classmethod``, detecting the problem and providing a targeted
        exception message.
        """
        if inspect.isfunction(method) and _get_first_arg_name(method) == 'cls':
            raise TypeError("@override must be applied above @classmethod")


class _OverriddenMethod(_WrappedMethod):
    """Wrapper for methods that have been marked with ``@override``."""
    __slots__ = _WrappedMethod.__slots__
