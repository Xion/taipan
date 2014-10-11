"""
Universal base class for objects.
"""
import abc
import functools
import inspect
import sys

from taipan._compat import IS_PY3, ifilter, xrange
from taipan.objective.classes import is_class, metaclass
from taipan.objective.methods import is_method


__all__ = [
    'Object', 'ObjectMetaclass',
    'ClassError', 'AbstractError',
]


# Universal base class

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
        meta._validate_base_classes(bases)

        class_ = super(ObjectMetaclass, meta).__new__(meta, name, bases, dict_)
        meta._validate_method_decoration(class_)

        return class_

    @classmethod
    def _validate_base_classes(meta, bases):
        """Validate the base classes of the new class to be created,
        making sure none of them are ``@final``.
        """
        for base in bases:
            if meta._is_final(base):
                raise ClassError(
                    "cannot inherit from @final class %s" % (base.__name__,))

    @classmethod
    def _validate_method_decoration(meta, class_):
        """Validate the usage of ``@override`` and ``@final`` modifiers
        on methods of the given ``class_``.
        """
        # TODO(xion): employ some code inspection tricks to serve ClassErrors
        # as if they were thrown at the offending class's/method's definition

        super_mro = class_.__mro__[1:]
        own_methods = ((name, member)
                       for name, member in class_.__dict__.items()
                       if is_method(member))

        # check that ``@override`` modifier is present where it should be
        # and absent where it shouldn't (e.g. ``@final`` methods)
        for name, method in own_methods:
            shadowed_method, base_class = next(
                ((getattr(base, name), base)
                 for base in super_mro if hasattr(base, name)),
                (None, None)
            )
            if meta._is_override(method):
                # ``@override`` is legal only when the method actually shadows
                # a method from a superclass, and that metod is not ``@final``
                if not shadowed_method:
                    raise ClassError("unnecessary @override on %s.%s" % (
                        class_.__name__, name), class_=class_)
                if meta._is_final(shadowed_method):
                    raise ClassError(
                        "illegal @override on a @final method %s.%s" % (
                            base_class.__name__, name), class_=class_)

                # if @override had parameter supplied, verify if it was
                # the same class as the base of shadowed method
                override_base = meta._get_override_base(method)
                if override_base and base_class is not override_base:
                    if is_class(override_base):
                        raise ClassError(
                            "incorrect override base: expected %s, got %s" % (
                                base_class.__name__, override_base.__name__))
                    else:
                        raise ClassError(
                            "invalid override base specified: %s" % (
                                override_base,))

                setattr(class_, name, method.method)
            else:
                if shadowed_method and name not in meta.OVERRIDE_EXEMPTIONS:
                    if meta._is_final(shadowed_method):
                        msg = "%s.%s is hiding a @final method %s.%s" % (
                            class_.__name__, name, base_class.__name__, name)
                    else:
                        msg = ("overridden method %s.%s "
                               "must be marked with @override" % (
                                class_.__name__, name))
                    raise ClassError(msg, class_=class_)

    @classmethod
    def _is_final(meta, arg):
        """Checks whether given class or method has been marked
        with the ``@final`` decorator.
        """
        if inspect.isclass(arg) and not isinstance(arg, ObjectMetaclass):
            return False  # of classes, only subclasses of Object can be final

        # account for method wrappers, such as the one introduced by @override
        from taipan.objective.modifiers import _WrappedMethod
        if isinstance(arg, _WrappedMethod):
            arg = arg.method

        return getattr(arg, '__final__', False)

    @classmethod
    def _is_override(meta, method):
        """Checks whether given class or instance method has been marked
        with the ``@override`` decorator.
        """
        from taipan.objective.modifiers import _OverriddenMethod
        return isinstance(method, _OverriddenMethod)

    @classmethod
    def _get_override_base(self, override_wrapper):
        """Retrieve the override base class from the
        :class:`_OverriddenMethod` wrapper.
        """
        base = override_wrapper.modifier.base
        if not base:
            return None
        if is_class(base):
            return base

        # resolve the (possibly qualified) class name
        if '.' in base:
            # repeatedly try to import the first N-1, N-2, etc. dot-separated
            # parts of the qualified name; this way we can handle all names
            # including `package.module.Class.InnerClass`
            dot_parts = base.split('.')
            for i in xrange(len(dot_parts) - 1, 1, -1):  # n-1 -> 1
                module_name = '.'.join(dot_parts[:i])
                class_name = '.'.join(dot_parts[i:])
                try:
                    module = __import__(module_name, fromlist=[dot_parts[i]])
                    break
                except ImportError:
                    pass
            else:
                # couldn't resolve class name, return it verbatim
                return base
        else:
            class_name = base
            module_name = override_wrapper.method.__module__
            module = sys.modules[module_name]

        return getattr(module, class_name)


@metaclass(ObjectMetaclass)
class Object(object):
    """Universal base class for objects.

    Inheriting from this class rather than the standard :class:`object`
    will grant access to additional object-oriented features.
    """


# Special flavors for metaclasses

class _ABCMetaclass(abc.ABCMeta):
    """Enhanced version of :class:`abc.ABCMeta` that wholly prevents
    instantiation of ``@abstract`` classes, only allowing to inherit from them.
    """
    def __new__(meta, name, bases, dict_):
        """Creates a new class using this metaclass.

        Usually this means the class is NOT inheriting from :class:`Object`
        while having ``@abstract`` modifier applied.
        """
        # abstract-ness is not transitive, so we explicitly mark subclasses
        # of abstract classes as concrete (this is irrespective of their
        # abstract methods/properties, if any)
        is_abstract = dict_.get('__abstract__', False)
        if not is_abstract:
            dict_['__abstract__'] = False

        # to prevent instantiation, either enhance existing __new__ method
        # of the upcming class, or equip it with a dedicated one
        if '__new__' in dict_:
            # create the class and obtain its custom instantiator,
            # i.e. the __new__ method (not to be confused with
            # the __new__ method of the METAclass)
            class_ = super(_ABCMetaclass, meta).__new__(
                meta, name, bases, dict_)
            instantiator = class_.__new__

            # replace the class's __new__ to check for abstract-ness
            @functools.wraps(instantiator)
            def new_instantiator(cls, *args, **kwargs):
                meta._ensure_concrete_class(cls)
                return instantiator(*args, **kwargs)

            class_.__new__ = new_instantiator
        else:
            # include straightforward instantation to check for abstract-ness
            def __new__(cls, *args, **kwargs):
                meta._ensure_concrete_class(cls)
                return super(class_, cls).__new__(cls, *args, **kwargs)

            dict_['__new__'] = __new__
            class_ = super(_ABCMetaclass, meta).__new__(
                meta, name, bases, dict_)

        return class_

    @classmethod
    def _ensure_concrete_class(meta, cls):
        """Check if given class is non-abstract."""
        if getattr(cls, '__abstract__', False):
            raise AbstractError(
                "cannot instantiate abstract class %s" % cls.__name__)


class _ABCObjectMetaclass(ObjectMetaclass, _ABCMetaclass):
    """Specialized version of :class:`ObjectMetaclass` for ``@abstract``
    subclassess of :class:`Object`.

    Do not use this metaclass directly; it can be only applied through
    the ``@abstract`` decorator.
    """
    def __new__(meta, name, bases, dict_):
        """Creates a new class using this metaclass.

        Usually this means the class is inheriting from :class:`Object`
        and has the ``@abstract`` modifier applied.
        """
        try:
            return super(_ABCObjectMetaclass, meta).__new__(
                meta, name, bases, dict_)
        except ClassError as e:
            # creating class failed; unfortunately, the ephemeral class
            # might have been already registered as implementation of some
            # abstract base classes residing up the inheritance chain;
            # we go up and de-register it manually
            if e.class_:
                for base in bases:
                    abclasses = ifilter(meta._is_abc, base.__mro__)
                    for abclass in abclasses:
                        # remove the class from given ABC's registry,
                        # its temporary cache, and so-called negative cache
                        # (+= 1 invalidates said negative cache)
                        abclass._abc_registry.discard(e.class_)
                        abclass._abc_cache.discard(e.class_)
                        abc.ABCMeta._abc_invalidation_counter += 1
            raise

    @classmethod
    def _is_abc(meta, class_):
        """Checks if given class is an abstract base class
        (in the traditional Python meaning).
        """
        return issubclass(type(class_), abc.ABCMeta)


# Exceptions

class ClassError(RuntimeError):
    """Exception raised when the class definition of :class:`Object` subclass
    is found to be incorrect.
    """
    # TODO(xion): introduce subclasses for all the various misuses
    # of @override, @final, and combinations thereof

    def __init__(self, *args, **kwargs):
        class_ = kwargs.pop('class_', None)
        super(ClassError, self).__init__(*args, **kwargs)
        self.class_ = class_


class AbstractError(TypeError):
    """Exception rasied when trying to instantiate an ``@abstract`` class."""
