"""
Test case class with additional enhancements.
"""
from taipan._compat import IS_PY3, metaclass
from taipan.collections import dicts
from taipan.objective.methods import is_method
from taipan.testing._unittest import TestCase as _TestCase
from taipan.testing.asserts import AssertsMixin


__all__ = ['TestCase']


class TestCaseMetaclass(type):
    """Metaclass for :class:`TestCase`.

    Its purpose is to interpret the methods adorned with test stage decorators
    and construct the appropriate :func:`setUp`, etc. methods which invoke them
    in the right order.
    """
    CLASS_STAGES = ('setUpClass', 'tearDownClass')
    INSTANCE_STAGES = ('setUp', 'tearDown')

    def __new__(meta, name, bases, dict_):
        """Create the new subclass of :class:`TestCase`."""
        super_ = (bases[0] if bases else object).__mro__[0]

        # FIXME(xion): doesn't work correctly for @classmethod,
        # we probably need to use technique similar to _WrappedMethod
        # from ObjectMetaclass
        get_stage = lambda meth: getattr(meth, '__stage__', (None, None))[0]

        for stage in meta.CLASS_STAGES + meta.INSTANCE_STAGES:
            if stage in dict_:
                continue  # test case class is overriding this stage completely

            stage_step_methods = [m for m in dicts.itervalues(dict_)
                                  if is_method(m) and get_stage(m) == stage]
            stage_step_methods.sort(key=lambda m: m.__stage__[1])
            dict_[stage] = meta._create_stage_method(
                stage, stage_step_methods, super_)

        return super(TestCaseMetaclass, meta).__new__(meta, name, bases, dict_)

    @classmethod
    def _create_stage_method(meta, stage, methods, super_):
        """Create method for given test stage.

        :param stage: Test stage string identifier, e.g. ``'setUp'``
        :param methods: List of methods to be executed at that stage
        :param super_: Superclass to delegate to ``super`` calls to

        :return: Function that invokes all ``methods`` in given order.
        """
        def invoke_methods(target):
            for method in methods:
                method(target)

        is_setup = stage.startswith('setUp')
        is_teardown = stage.startswith('tearDown')

        if stage in meta.CLASS_STAGES:
            def class_method(cls):
                if is_setup:
                    getattr(super_, stage)()
                invoke_methods(cls)
                if is_teardown:
                    getattr(super_, stage)()

            class_method.__name__ = stage
            class_method = classmethod(class_method)
            return class_method

        if stage in meta.INSTANCE_STAGES:
            def instance_method(self):
                if is_setup:
                    getattr(super_, stage)(self)
                invoke_methods(self)
                if is_teardown:
                    getattr(super_, stage)(self)

            instance_method.__name__ = stage
            return instance_method

        raise ValueError("invalid test stage identifier: %r" % (stage,))


@metaclass(TestCaseMetaclass)
class TestCase(_TestCase, AssertsMixin):
    """Augmented test case class.

    Includes few additional, convenience assertion methods,
    as well as the capability to use test stage decorators,
    such as :func:`setUp` and :func:`tearDown`.
    """
    # Python 3 changes name of the following assert function,
    # so we provide backward and forward synonyms for compatibility
    if IS_PY3:
        assertItemsEqual = _TestCase.assertCountEqual
    else:
        assertCountEqual = _TestCase.assertItemsEqual
