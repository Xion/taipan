"""
Universal base class for objects.
"""
from taipan._compat import IS_PY3
from taipan.objective.classes import metaclass
from taipan.objective.methods import is_method


__all__ = [
    'Object', 'ObjectMetaclass',
    'ClassError',
]


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
            if getattr(base, '__final__', False):
                raise ClassError(
                    "cannot inherit from @final class %s" % (base.__name__,))

        class_ = super(ObjectMetaclass, meta).__new__(meta, name, bases, dict_)

        # check for presence of ``@override`` on appropriate methods
        super_mro = class_.__mro__[1:]
        own_methods = ((name, member) for name, member in dict_.items()
                       if is_method(member))
        for name, method in own_methods:
            shadows_base = any(hasattr(base, name) for base in super_mro)
            if meta._is_override(method):
                if not shadows_base:
                    raise ClassError("unnecessary @override on %s.%s" % (
                        class_.__name__, name))
                setattr(class_, name, method.method)
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
        from taipan.objective.modifiers import _OverriddenMethod
        return isinstance(method, _OverriddenMethod)


@metaclass(ObjectMetaclass)
class Object(object):
    """Universal base class for objects.

    Inheriting from this class rather than the standard :class:`object`
    will grant access to additional object-oriented features.
    """


class ClassError(RuntimeError):
    """Exception raised when the class definition of :class:`Object` subclass
    is found to be incorrect.
    """
