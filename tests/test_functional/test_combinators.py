"""
Tests for .functional.combinators module.
"""
from itertools import product

from taipan._compat import xrange
from taipan.testing import TestCase

import taipan.functional.combinators as __unit__


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
            self.assertEquals(f(*args), g(*args),
                              msg="result mismatch for args: %r" % (args,))


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
    EVEN = staticmethod(lambda x: x % 2 == 0)
    ODD = staticmethod(lambda x: x % 2 == 1)

    BETWEEN = staticmethod(lambda min_, max_: lambda x: min_ < x < max_)
    EVEN_BETWEEN = staticmethod(
        lambda min_, max_: lambda x: min_ < x < max_ and x % 2 == 0)
    ODD_BETWEEN = staticmethod(
        lambda min_, max_: lambda x: min_ < x < max_ and x % 2 == 1)

    OUTSIDE = staticmethod(lambda min_, max_: lambda x: x < min_ or x > max_)
    EVEN_OR_OUTSIDE = staticmethod(
        lambda min_, max_: lambda x: x % 2 == 0 or x < min_ or x > max_)
    ODD_OR_OUTSIDE = staticmethod(
        lambda min_, max_: lambda x: x % 2 == 0 or x < min_ or x > max_)


class And_(_BinaryLogicalCombinator):

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


class Nand(_BinaryLogicalCombinator):

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.nand()

    def test_one_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.nand(None)

    def test_one_arg__true(self):
        self._assertBooleanFunctionsEqual(Nand.FALSE, __unit__.nand(Nand.TRUE))

    def test_one_arg__false(self):
        self._assertBooleanFunctionsEqual(Nand.TRUE, __unit__.nand(Nand.FALSE))

    def test_two_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Nand.FALSE, __unit__.nand(Nand.TRUE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.TRUE, Nand.FALSE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.FALSE))

    def test_two_args__integer_ranges__half_open(self):
        self._assertIntegerFunctionsEqual(
            Nand.LESS_THAN(11),  # higher minimum "wins" and is negated
            __unit__.nand(Nand.GREATER_THAN(5), Nand.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Nand.GREATER_THAN(4),  # lower maximum "wins" ans is negated
            __unit__.nand(Nand.LESS_THAN(5), Nand.LESS_THAN(10)))

    def test_two_args__integer_ranges__open(self):
        self._assertIntegerFunctionsEqual(
            Nand.TRUE,
            __unit__.nand(Nand.LESS_THAN(5), Nand.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Nand.OUTSIDE(6, 9),
            __unit__.nand(Nand.GREATER_THAN(5), Nand.LESS_THAN(10)))

    def test_three_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Nand.FALSE, __unit__.nand(Nand.TRUE, Nand.TRUE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.TRUE, Nand.TRUE, Nand.FALSE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.TRUE, Nand.FALSE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.TRUE, Nand.FALSE, Nand.FALSE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.TRUE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.TRUE, Nand.FALSE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.FALSE, Nand.TRUE))
        self._assertBooleanFunctionsEqual(
            Nand.TRUE, __unit__.nand(Nand.FALSE, Nand.FALSE, Nand.FALSE))

    def test_three_args__even_integer_intervals(self):
        self._assertIntegerFunctionsEqual(
            Nand.TRUE,
            __unit__.nand(Nand.LESS_THAN(5), Nand.GREATER_THAN(10),
                          Nand.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Nand.TRUE,
            __unit__.nand(Nand.GREATER_THAN(6), Nand.LESS_THAN(7),
                          Nand.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Nand.TRUE,
            __unit__.nand(Nand.GREATER_THAN(10), Nand.LESS_THAN(10),
                          Nand.DIVISIBLE_BY(2)))


class Nor(_BinaryLogicalCombinator):

    def test_no_args(self):
        with self.assertRaises(TypeError):
            __unit__.nor()

    def test_one_arg__none(self):
        with self.assertRaises(TypeError):
            __unit__.nor(None)

    def test_one_arg__true(self):
        self._assertBooleanFunctionsEqual(Nor.FALSE, __unit__.nor(Nor.TRUE))

    def test_one_arg__false(self):
        self._assertBooleanFunctionsEqual(Nor.TRUE, __unit__.nor(Nor.FALSE))

    def test_two_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.FALSE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.FALSE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.TRUE, __unit__.nor(Nor.FALSE, Nor.FALSE))

    def test_two_args__integer_ranges__half_open(self):
        self._assertIntegerFunctionsEqual(
            Nor.LESS_THAN(6),  # lower minimum "wins" and is negated
            __unit__.nor(Nor.GREATER_THAN(5), Nor.GREATER_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Nor.GREATER_THAN(9),  # higher maximum "wins" and is negated
            __unit__.nor(Nor.LESS_THAN(5), Nor.LESS_THAN(10)))

    def test_two_args__integer_ranges__closed(self):
        self._assertIntegerFunctionsEqual(
            Nor.FALSE,
            __unit__.nor(Nor.GREATER_THAN(5), Nor.LESS_THAN(10)))
        self._assertIntegerFunctionsEqual(
            Nor.BETWEEN(4, 11),
            __unit__.nor(Nor.GREATER_THAN(10), Nor.LESS_THAN(5)))

    def test_three_args__boolean_functions(self):
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.TRUE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.TRUE, Nor.FALSE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.FALSE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.TRUE, Nor.FALSE, Nor.FALSE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.FALSE, Nor.TRUE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.FALSE, Nor.TRUE, Nor.FALSE))
        self._assertBooleanFunctionsEqual(
            Nor.FALSE, __unit__.nor(Nor.FALSE, Nor.FALSE, Nor.TRUE))
        self._assertBooleanFunctionsEqual(
            Nor.TRUE, __unit__.nor(Nor.FALSE, Nor.FALSE, Nor.FALSE))

    def test_three_args__even_integer_intervals(self):
        self._assertIntegerFunctionsEqual(
            Nor.FALSE,
            __unit__.nor(Nor.GREATER_THAN(5), Nor.LESS_THAN(10),
                         Nor.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Nor.FALSE,
            __unit__.nor(Nor.GREATER_THAN(6), Nor.LESS_THAN(7),
                         Nor.DIVISIBLE_BY(2)))
        self._assertIntegerFunctionsEqual(
            Nor.ODD_BETWEEN(4, 11),
            __unit__.nor(Nor.GREATER_THAN(10), Nor.LESS_THAN(5),
                         Nor.DIVISIBLE_BY(2)))
