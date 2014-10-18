"""
Decorators for :class:`TestCase` methods.
"""
from taipan.api.decorators import function_decorator, method_decorator
from taipan.strings import ensure_string


__all__ = [
    'setUpClass', 'beforeClass',
    'setUp', 'before',
    'tearDown', 'after',
    'tearDownClass', 'afterClass',
]


class _StageMethod(object):
    """Wrapper for methods that's been marked with the test stage decorator.

    Those methods will be unwrapped by :class:`TestCaseMetaclass`
    during creation of the test case class that defined them.
    """
    __slots__ = ['method', 'stage', 'order']

    def __init__(self, method, stage, order):
        self.method = method
        self.stage = ensure_string(stage)
        self.order = order

    # We proxy most operations to the underlying method to support the use case
    # when it's called / referenced / etc. even before test class is created.
    # (It should be very, very rare, though).

    def __call__(self, *args, **kwargs):
        """Proxy calls to underlying method."""
        return self.method(*args, **kwargs)

    def __getattribute__(self, attr):
        """Proxy attribute access to underlying method."""
        if attr in _StageMethod.__slots__:
            return object.__getattribute__(self, attr)
        else:
            return getattr(self.method, attr)


class _StageDecorator(object):
    """Base for the decorators that are applicable to :class:`TestCase` methods
    that are to be invoked at various stages of running a test.
    """
    #: Name of the test stage of this decorator.
    stage = None

    #: Tracks the use counters of the specific decorator
    #: to reestablish the proper order of decorated methods.
    use_counter = 0

    def __call__(self, func):
        """Decorate a test case method,
        attaching the stage & order information to it.
        """
        class_ = self.__class__

        counter = class_.use_counter
        class_.use_counter = counter + 1

        return _StageMethod(func, stage=class_.stage, order=counter)


# Specific stage decorators

@function_decorator
class setUpClass(_StageDecorator):
    """Decorator for test case methods which should be invoked at the time
    when the whole test case class is being set up.

    .. warning::

        Even though the decorated method is class-level, it should **not**
        be also decorated as ``@classmethod``!

    Example::

        class MyTest(TestCase):
            @setUpClass
            def do_some_class_setup(cls):
                ...

    Multiple methods decorated this way will be invoked in the order
    they were defined in the test case class.

    .. versionadded:: 0.0.4
    """
    stage = 'setUpClass'

#: Alias for :class:`setUpClass`.
beforeClass = setUpClass


@method_decorator
class setUp(_StageDecorator):
    """Decorator for test case methods which should be invoked immediately
    before any test is run.

    Example::

        class MyTest(TestCase):
            @setUp
            def do_some_test_setup(self):
                ...

    Multiple methods decorated this way will be invoked in the order
    they were defined in the test case class.

    .. versionadded:: 0.0.4
    """
    stage = 'setUp'

#: Alias for :class:`setUp`.
before = setUp


@method_decorator
class tearDown(_StageDecorator):
    """Decorator for test case methods which should be invoked immediately
    after any test has been run.

    Example::

        class MyTest(TestCase):
            @tearDown
            def do_some_test_cleanup(self):
                ...

    Multiple methods decorated this way will be invoked in the order
    they were defined in the test case class.

    .. versionadded:: 0.0.4
    """
    stage = 'tearDown'

#: Alias for :class:`tearDown`.
after = tearDown


@function_decorator
class tearDownClass(_StageDecorator):
    """Decorator for test case methods which should be invoked at the time
    when the whole test case class is being torn down.

    .. warning::

        Even though the decorated method is class-level, it should **not**
        be also decorated as ``@classmethod``!

    Example::

        class MyTest(TestCase):
            @tearDownClass
            def do_some_class_cleanup(cls):
                ...

    Multiple methods decorated this way will be invoked in the order
    they were defined in the test case class.

    .. versionadded:: 0.0.4
    """
    stage = 'tearDownClass'

#: Alias for :class:`tearDownClass`
afterClass = tearDownClass
