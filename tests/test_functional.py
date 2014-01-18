"""
Tests for the .functional module.
"""
from collections import namedtuple
from itertools import product

from taipan.testing import TestCase

from taipan._compat import xrange
import taipan.functional as __unit__


class EnsureCallable(TestCase):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(object())

    def test_number(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable(42)

    def test_string(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_callable("foo")

    def test_few_builtins(self):
        __unit__.ensure_callable(open)
        __unit__.ensure_callable(min)
        __unit__.ensure_callable(sum)
        __unit__.ensure_callable(str.__add__)

    def test_lambda(self):
        func = lambda : self.fail("lambda must not be acually called")
        __unit__.ensure_callable(func)

    def test_function(self):
        def func():
            self.fail("function must not be actually called")
        __unit__.ensure_callable(func)

    def test_class(self):
        class Foo(object):
            def __init__(self_):
                self.fail("class must not be actually instantiated")
        __unit__.ensure_callable(Foo)

    def test_callable_object(self):
        class Foo(object):
            def __call__(self_):
                self.fail("object must not be actually called")
        __unit__.ensure_callable(Foo())


class EnsureArgcount(TestCase):
    FEW_ARGS = ["foo", 'bar']
    MANY_ARGS = ["foo", 'bar', 1.41, False, None, (1,)]

    FEW = len(FEW_ARGS)
    MANY = len(MANY_ARGS)
    MORE_THAN_FEW = FEW + 1
    LESS_THAN_MANY = MANY - 1

    def test_no_limits(self):
        with self.assertRaises(ValueError):
            __unit__.ensure_argcount(self.FEW_ARGS)

    def test_invalid_limits(self):
        with self.assertRaises(ValueError) as r:
            __unit__.ensure_argcount(self.FEW_ARGS, min_=2, max_=1)
        self.assertIn("greater", str(r.exception))

    def test_args__none(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount(None, min_=1, max_=1)

    def test_args__some_object(self):
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount(object(), min_=1, max_=1)

    def test_args__empty(self):
        __unit__.ensure_argcount([], min_=0, max_=0)
        __unit__.ensure_argcount([], min_=0, max_=self.MANY)
        with self.assertRaises(TypeError):
            __unit__.ensure_argcount([], min_=self.FEW)

    def test_args__less_than_min(self):
        with self.assertRaises(TypeError) as r:
            __unit__.ensure_argcount(self.FEW_ARGS, min_=self.MORE_THAN_FEW)
        self.assertIn("expected at least", str(r.exception))

    def test_args__more_than_max(self):
        with self.assertRaises(TypeError) as r:
            __unit__.ensure_argcount(self.MANY_ARGS, max_=self.LESS_THAN_MANY)
        self.assertIn("expected at most", str(r.exception))

    def test_args__exactly_min(self):
        __unit__.ensure_argcount(self.FEW_ARGS,
                                 min_=self.FEW, max_=self.MORE_THAN_FEW)

    def test_args__exactly_max(self):
        __unit__.ensure_argcount(self.MANY_ARGS,
                                 min_=self.LESS_THAN_MANY, max_=self.MANY)

    def test_args__exact(self):
        __unit__.ensure_argcount(self.FEW_ARGS, min_=self.FEW, max_=self.FEW)
        __unit__.ensure_argcount(self.MANY_ARGS, min_=self.MANY, max_=self.MANY)


# Constant functions

class _ConstantFunction(TestCase):
    EMPTY_TUPLE = ()

    EMPTY_LIST = []
    DIFFERENT_EMPTY_LIST = []
    LIST = list(range(5))
    LIST_COPY = list(LIST)

    EMPTY_DICT = {}
    DIFFERENT_EMPTY_DICT = {}
    DICT = dict(zip('abcde', range(5)))
    DICT_COPY = dict(DICT)

    OBJECT = object()
    DIFFERENT_OBJECT = object()


class Identity(_ConstantFunction):

    def test_values(self):
        identity = __unit__.identity()
        self.assertIsNone(identity(None))
        self.assertIs(0, identity(0))
        self.assertIs(self.EMPTY_TUPLE, identity(self.EMPTY_TUPLE))

    def test_empty_lists(self):
        identity = __unit__.identity()
        self.assertIs(self.EMPTY_LIST, identity(self.EMPTY_LIST))
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, identity(self.EMPTY_LIST))

    def test_lists(self):
        identity = __unit__.identity()
        self.assertIs(self.LIST, identity(self.LIST))
        self.assertIsNot(self.LIST_COPY, identity(self.LIST))

    def test_empty_dicts(self):
        identity = __unit__.identity()
        self.assertIs(self.EMPTY_DICT, identity(self.EMPTY_DICT))
        self.assertIsNot(self.DIFFERENT_EMPTY_DICT, identity(self.EMPTY_DICT))

    def test_dicts(self):
        identity = __unit__.identity()
        self.assertIs(self.DICT, identity(self.DICT))
        self.assertIsNot(self.DICT_COPY, identity(self.DICT))

    def test_object(self):
        identity = __unit__.identity()
        self.assertIs(self.OBJECT, identity(self.OBJECT))
        self.assertIsNot(self.DIFFERENT_OBJECT, identity(self.OBJECT))


class Const(_ConstantFunction):

    def test_values(self):
        self.assertIsNone(__unit__.const(None)())
        self.assertIs(0, __unit__.const(0)())
        self.assertIs(self.EMPTY_TUPLE, __unit__.const(self.EMPTY_TUPLE)())

    def test_empty_lists(self):
        empty_list = __unit__.const(self.EMPTY_LIST)
        self.assertIs(self.EMPTY_LIST, empty_list())
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, empty_list())

    def test_lists(self):
        list_ = __unit__.const(self.LIST)
        self.assertIs(self.LIST, list_())
        self.assertIsNot(self.DIFFERENT_EMPTY_LIST, list_())

    def test_empty_dicts(self):
        empty_dict = __unit__.const(self.EMPTY_DICT)
        self.assertIs(self.EMPTY_DICT, empty_dict())
        self.assertIsNot(self.DIFFERENT_EMPTY_DICT, empty_dict())

    def test_dicts(self):
        dict_ = __unit__.const(self.DICT)
        self.assertIs(self.DICT, dict_())
        self.assertIsNot(self.DICT_COPY, dict_())

    def test_object(self):
        object_ = __unit__.const(self.OBJECT)
        self.assertIs(self.OBJECT, object_())
        self.assertIsNot(self.DIFFERENT_OBJECT, object_())


class PredefinedConstantFunctions(_ConstantFunction):

    def test_true(self):
        true = __unit__.true()
        self.assertTrue(true())
        with self.assertRaises(TypeError):
            true("extraneous argument")

    def test_false(self):
        false = __unit__.false()
        self.assertFalse(false())
        with self.assertRaises(TypeError):
            false("extraneous argument")

    def test_none(self):
        none = __unit__.none()
        self.assertIsNone(none())
        with self.assertRaises(TypeError):
            none("extraneous argument")

    def test_zero(self):
        zero = __unit__.zero()
        self.assertZero(zero())
        with self.assertRaises(TypeError):
            zero("extraneous argument")

    def test_one(self):
        one = __unit__.one()
        self.assertEquals(1, one())
        with self.assertRaises(TypeError):
            one("extraneous argument")

    def test_empty(self):
        empty = __unit__.empty()
        self.assertEmpty(empty())
        with self.assertRaises(TypeError):
            empty("extraneous argument")


# Unary functions

class AttrFunc(TestCase):
    CLASS = namedtuple('Foo', ['foo', 'bar'])

    SINGLE_NESTED_OBJECT = CLASS(foo=1, bar='baz')
    DOUBLY_NESTED_OBJECT = CLASS(foo=CLASS(foo=1, bar=2), bar='a')

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.attr_func(object())

    def test_single_attr__good(self):
        func = __unit__.attr_func('foo')
        self.assertEquals(
            self.SINGLE_NESTED_OBJECT.foo, func(self.SINGLE_NESTED_OBJECT))
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo, func(self.DOUBLY_NESTED_OBJECT))

    def test_single_attr__bad(self):
        func = __unit__.attr_func('doesnt_exist')
        with self.assertRaises(AttributeError):
            func(self.SINGLE_NESTED_OBJECT)
        with self.assertRaises(AttributeError):
            func(self.DOUBLY_NESTED_OBJECT)

    def test_two_attrs__good(self):
        func = __unit__.attr_func('foo', 'bar')
        self.assertEquals(
            self.DOUBLY_NESTED_OBJECT.foo.bar, func(self.DOUBLY_NESTED_OBJECT))

    def test_two_attrs__bad(self):
        func = __unit__.attr_func('doesnt_exist', 'foo')
        with self.assertRaises(AttributeError):
            func(self.DOUBLY_NESTED_OBJECT)


class KeyFunc(TestCase):
    SINGLY_NESTED_DICT = dict(foo=1, bar='baz')
    DOUBLY_NESTED_DICT = dict(foo=dict(foo=1, bar=2), bar='a')

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.key_func()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.key_func(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.key_func(object())

    def test_single_key__good(self):
        func = __unit__.key_func('foo')
        self.assertEquals(
            self.SINGLY_NESTED_DICT['foo'], func(self.SINGLY_NESTED_DICT))
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo'], func(self.DOUBLY_NESTED_DICT))

    def test_single_key__bad(self):
        func = __unit__.key_func('doesnt_exist')
        with self.assertRaises(LookupError):
            func(self.SINGLY_NESTED_DICT)
        with self.assertRaises(LookupError):
            func(self.DOUBLY_NESTED_DICT)

    def test_two_keys__good(self):
        func = __unit__.key_func('foo', 'bar')
        self.assertEquals(
            self.DOUBLY_NESTED_DICT['foo']['bar'],
            func(self.DOUBLY_NESTED_DICT))

    def test_two_keys__bad(self):
        func = __unit__.key_func('doesnt_exist', 'foo')
        with self.assertRaises(LookupError):
            func(self.DOUBLY_NESTED_DICT)


# General combinators

class _Combinator(TestCase):

    def _assertIntegerFunctionsEqual(self, f, g, argcount=1, domain=None):
        if domain is None:
            # use roughly the same amount time regardless of function's arity
            limit = int(pow(512, 1.0 / argcount))
            self.assertGreater(
                limit, 0, msg="Too many arguments for integer functions")
            domain = xrange(-limit, limit + 1)

        for args in product(domain, repeat=argcount):
            self.assertEquals(f(*args), g(*args))


class _UnaryCombinator(_Combinator):
    VERBATIM = staticmethod(lambda *args, **kwargs: (args, kwargs))

    SINGLE_VARARG = ((42,), {})
    TWO_VARARGS = (('foo', 'bar'), {})

    SINGLE_KWARG = ((), {'foo': 1})
    TWO_KWARGS = ((), {'foo': 1, 'bar': 2})

    ARG_AND_KWARG = ((42,), {'foo': 1})
    ARGS_AND_KWARGS = ((13, 42), {'foo': 1, 'bar': 2})


class Uncurry(_UnaryCombinator):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.uncurry(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.uncurry(object())

    def test_callable__positional_args(self):
        uncurried = __unit__.uncurry(Uncurry.VERBATIM)
        self.assertEquals(self.SINGLE_VARARG, uncurried(*self.SINGLE_VARARG))
        self.assertEquals(self.TWO_VARARGS, uncurried(*self.TWO_VARARGS))

    def test_callable__keyword_args(self):
        uncurried = __unit__.uncurry(Uncurry.VERBATIM)
        self.assertEquals(self.SINGLE_KWARG, uncurried(*self.SINGLE_KWARG))
        self.assertEquals(self.TWO_KWARGS, uncurried(*self.TWO_KWARGS))

    def test_callable__both(self):
        uncurried = __unit__.uncurry(Uncurry.VERBATIM)
        self.assertEquals(self.ARG_AND_KWARG, uncurried(*self.ARG_AND_KWARG))
        self.assertEquals(
            self.ARGS_AND_KWARGS, uncurried(*self.ARGS_AND_KWARGS))


class Flip(_UnaryCombinator):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.flip(None)

    def test_some_object(self):
        with self.assertRaises(TypeError):
            __unit__.flip(object())

    def test_callable__positional_args(self):
        flipped = __unit__.flip(Flip.VERBATIM)
        self.assertEquals(self.SINGLE_VARARG, flipped(*self.SINGLE_VARARG))
        self.assertEquals(
            self._reverse_first(self.TWO_VARARGS), flipped(*self.TWO_VARARGS))

    def test_callable__keyword_args(self):
        flipped = __unit__.flip(Flip.VERBATIM)
        self.assertEquals(self.SINGLE_KWARG, flipped(*self.SINGLE_KWARG))
        self.assertEquals(self.TWO_KWARGS, flipped(*self.TWO_KWARGS))

    def test_callable__both(self):
        flipped = __unit__.flip(Flip.VERBATIM)
        self.assertEquals(self.ARG_AND_KWARG, flipped(*self.ARG_AND_KWARG))
        self.assertEquals(
            self._reverse_first(self.ARGS_AND_KWARGS),
            flipped(*self.ARGS_AND_KWARGS))

    # Utility functions

    def _reverse_first(self, tuple_):
        return (tuple(reversed(tuple_[0])),) + tuple_[1:]


class Compose(_Combinator):
    F = staticmethod(lambda x: x + 1)
    G = staticmethod(lambda x: 3*x)
    H = staticmethod(lambda x: x*x)

    FG = staticmethod(lambda x: 3*x + 1)  # f(g(x))
    GF = staticmethod(lambda x: 3*(x + 1))  # g(f(x))
    FH = staticmethod(lambda x: x*x + 1)  # f(h(x))
    HF = staticmethod(lambda x: (x + 1)**2)  # h(f(x))
    GH = staticmethod(lambda x: 3*(x*x))  # g(h(x))
    HG = staticmethod(lambda x: (3*x)**2)  # h(g(x))

    FGH = staticmethod(lambda x: 3*(x*x) + 1)  # f(g(h(x)))
    HGF = staticmethod(lambda x: (3*(x + 1))**2)  # h(g(f(x)))

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.compose()

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.compose(None)

    def test_single_arg(self):
        self._assertIntegerFunctionsEqual(
            Compose.F, __unit__.compose(Compose.F))
        self._assertIntegerFunctionsEqual(
            Compose.G, __unit__.compose(Compose.G))
        self._assertIntegerFunctionsEqual(
            Compose.H, __unit__.compose(Compose.H))

    def test_two_functions(self):
        self._assertIntegerFunctionsEqual(
            Compose.FG, __unit__.compose(Compose.F, Compose.G))
        self._assertIntegerFunctionsEqual(
            Compose.GF, __unit__.compose(Compose.G, Compose.F))
        self._assertIntegerFunctionsEqual(
            Compose.FH, __unit__.compose(Compose.F, Compose.H))
        self._assertIntegerFunctionsEqual(
            Compose.HF, __unit__.compose(Compose.H, Compose.F))
        self._assertIntegerFunctionsEqual(
            Compose.GH, __unit__.compose(Compose.G, Compose.H))
        self._assertIntegerFunctionsEqual(
            Compose.HG, __unit__.compose(Compose.H, Compose.G))

    def test_associativity(self):
        self._assertIntegerFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.F, Compose.GH))
        self._assertIntegerFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.FG, Compose.H))

        self._assertIntegerFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.H, Compose.GF))
        self._assertIntegerFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.HG, Compose.F))

    def test_three_functions(self):
        self._assertIntegerFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.F, Compose.G, Compose.H))
        self._assertIntegerFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.H, Compose.G, Compose.F))

    def test_last_function_with_multiple_args(self):
        self._assertIntegerFunctionsEqual(
            lambda a, b: Compose.F(a * b),
            __unit__.compose(Compose.F, int.__mul__),
            argcount=2)
        self._assertIntegerFunctionsEqual(
            lambda a, b: Compose.G(a + b),
            __unit__.compose(Compose.G, int.__add__),
            argcount=2)


# Logical combinators

class _LogicalCombinator(_Combinator):
    TRUE = staticmethod(lambda _: True)
    FALSE = staticmethod(lambda _: False)
    NONE = staticmethod(lambda _: None)

    IDENTITY = staticmethod(lambda x: x)
    NOT = staticmethod(lambda x: not x)

    def _assertBooleanFunctionsEqual(self, f, g):
        for val in (True, False):
            self.assertEquals(f(val), g(val))
        self.assertEquals(bool(f(None)), bool(g(None)))


class Not_(_LogicalCombinator):

    def test_none(self):
        with self.assertRaises(TypeError):
            __unit__.not_(None)

    def test_true_func(self):
        self._assertBooleanFunctionsEqual(Not_.FALSE, __unit__.not_(Not_.TRUE))

    def test_false_func(self):
        self._assertBooleanFunctionsEqual(Not_.TRUE, __unit__.not_(Not_.FALSE))

    def test_none_func(self):
        self._assertBooleanFunctionsEqual(Not_.TRUE, __unit__.not_(Not_.NONE))

    def test_identity_func(self):
        self._assertBooleanFunctionsEqual(
            Not_.NOT, __unit__.not_(Not_.IDENTITY))

    def test_not_func(self):
        self._assertBooleanFunctionsEqual(
            Not_.IDENTITY, __unit__.not_(Not_.NOT))

    def test_double_not(self):
        not_ = __unit__.not_(Not_.IDENTITY)
        identity = __unit__.not_(Not_.NOT)
        self._assertBooleanFunctionsEqual(Not_.IDENTITY, __unit__.not_(not_))
        self._assertBooleanFunctionsEqual(Not_.NOT, __unit__.not_(identity))


class _BinaryLogicalCombinator(_LogicalCombinator):
    GREATER_THAN = staticmethod(lambda min_: lambda x: x > min_)
    LESS_THAN = staticmethod(lambda max_: lambda x: x < max_)
    DIVISIBLE_BY = staticmethod(lambda d: lambda x: x % d == 0)


class And_(_BinaryLogicalCombinator):
    BETWEEN = staticmethod(lambda min_, max_: lambda x: min_ < x < max_)
    EVEN_BETWEEN = staticmethod(
        lambda min_, max_: lambda x: min_ < x < max_ and x % 2 == 0)

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.and_()

    def test_one_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.and_(None)

    def test_one_arg__true(self):
        self._assertBooleanFunctionsEqual(And_.TRUE, __unit__.and_(And_.TRUE))

    def test_one_arg__false(self):
        self._assertBooleanFunctionsEqual(And_.FALSE, __unit__.and_(And_.FALSE))

    def test_two_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            And_.TRUE, __unit__.and_(And_.TRUE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.TRUE, And_.FALSE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.FALSE))

    def test_two_args__integer_ranges__half_open(self):
        self._assertIntegerFunctionsEqual(
            And_.GREATER_THAN(10),  # higher minimum "wins"
            __unit__.and_(And_.GREATER_THAN(5), And_.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            And_.LESS_THAN(5),  # lower maximum "wins"
            __unit__.and_(And_.LESS_THAN(5), And_.LESS_THAN(10)))

    def test_two_args__integer_ranges__closed(self):
        self._assertIntegerFunctionsEqual(
            And_.BETWEEN(5, 10),
            __unit__.and_(And_.GREATER_THAN(5), And_.LESS_THAN(10)))
        self._assertIntegerFunctionsEqual(
            And_.FALSE,
            __unit__.and_(And_.GREATER_THAN(10), And_.LESS_THAN(5)))

    def test_three_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            And_.TRUE, __unit__.and_(And_.TRUE, And_.TRUE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.TRUE, And_.TRUE, And_.FALSE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.TRUE, And_.FALSE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.TRUE, And_.FALSE, And_.FALSE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.TRUE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.TRUE, And_.FALSE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.FALSE, And_.TRUE))
        self._assertBooleanFunctionsEqual(
            And_.FALSE, __unit__.and_(And_.FALSE, And_.FALSE, And_.FALSE))

    def test_three_args__even_integer_intervals(self):
        self._assertIntegerFunctionsEqual(
            And_.EVEN_BETWEEN(5, 10),
            __unit__.and_(And_.GREATER_THAN(5), And_.LESS_THAN(10),
                          And_.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            And_.FALSE,  # because there are no even numbers in range
            __unit__.and_(And_.GREATER_THAN(6), And_.LESS_THAN(7),
                          And_.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            And_.FALSE,  # because there are no numbers in range
            __unit__.and_(And_.GREATER_THAN(10), And_.LESS_THAN(5),
                          And_.DIVISIBLE_BY(2)))


class Or_(_BinaryLogicalCombinator):
    OUTSIDE = staticmethod(lambda min_, max_: lambda x: x < min_ or x > max_)
    EVEN_OR_OUTSIDE = staticmethod(
        lambda min_, max_: lambda x: x % 2 == 0 or x < min_ or x > max_)

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.or_()

    def test_one_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.or_(None)

    def test_one_arg__true(self):
        self._assertBooleanFunctionsEqual(Or_.TRUE, __unit__.or_(Or_.TRUE))

    def test_one_arg__false(self):
        self._assertBooleanFunctionsEqual(Or_.FALSE, __unit__.or_(Or_.FALSE))

    def test_two_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.FALSE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.FALSE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.FALSE, __unit__.or_(Or_.FALSE, Or_.FALSE))

    def test_two_args__integer_ranges__half_open(self):
        self._assertIntegerFunctionsEqual(
            Or_.GREATER_THAN(5),  # lower minimum "wins"
            __unit__.or_(Or_.GREATER_THAN(5), Or_.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Or_.LESS_THAN(10),  # higher maximum "wins"
            __unit__.or_(Or_.LESS_THAN(5), Or_.LESS_THAN(10)))

    def test_two_args__integer_ranges__open(self):
        self._assertIntegerFunctionsEqual(
            Or_.OUTSIDE(5, 10),
            __unit__.or_(Or_.LESS_THAN(5), Or_.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Or_.TRUE,
            __unit__.or_(Or_.GREATER_THAN(5), Or_.LESS_THAN(10)))

    def test_three_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.TRUE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.TRUE, Or_.FALSE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.FALSE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.TRUE, Or_.FALSE, Or_.FALSE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.FALSE, Or_.TRUE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.FALSE, Or_.TRUE, Or_.FALSE))
        self._assertBooleanFunctionsEqual(
            Or_.TRUE, __unit__.or_(Or_.FALSE, Or_.FALSE, Or_.TRUE))
        self._assertBooleanFunctionsEqual(
            Or_.FALSE, __unit__.or_(Or_.FALSE, Or_.FALSE, Or_.FALSE))

    def test_three_args__even_integer_intervals(self):
        self._assertIntegerFunctionsEqual(
            Or_.EVEN_OR_OUTSIDE(5, 10),
            __unit__.or_(Or_.LESS_THAN(5), Or_.GREATER_THAN(10),
                          Or_.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Or_.TRUE,  # because the ranges overlap
            __unit__.or_(Or_.GREATER_THAN(6), Or_.LESS_THAN(7),
                          Or_.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Or_.TRUE,  # because an even number closes the gap between ranges
            __unit__.or_(Or_.GREATER_THAN(10), Or_.LESS_THAN(10),
                          Or_.DIVISIBLE_BY(2)))
