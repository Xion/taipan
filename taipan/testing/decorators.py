"""
Decorators for :class:`TestCase` methods.
"""
from taipan.api.decorators import function_decorator, method_decorator


__all__ = [
    'setUpClass', 'beforeClass',
    'setUp', 'before',
    'tearDown', 'after',
    'tearDownClass', 'afterClass',
]


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

        func.__stage__ = (class_.stage, counter)
        return func


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
