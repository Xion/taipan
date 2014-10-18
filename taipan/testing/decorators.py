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

# TODO(xion): add docstrings to them

@function_decorator
class setUpClass(_StageDecorator):
    stage = 'setUpClass'

#: Alias for :class:`setUpClass`.
beforeClass = setUpClass


@method_decorator
class setUp(_StageDecorator):
    stage = 'setUp'

#: Alias for :class:`setUp`.
before = setUp


@method_decorator
class tearDown(_StageDecorator):
    stage = 'tearDown'

#: Alias for :class:`tearDown`.
after = tearDown


@function_decorator
class tearDownClass(_StageDecorator):
    stage = 'tearDownClass'

#: Alias for :class:`tearDownClass`
afterClass = tearDownClass
