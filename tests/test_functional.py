"""
Tests for the .functional module.
"""
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


class Compose(TestCase):
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
        self._assertFunctionsEqual(Compose.F, __unit__.compose(Compose.F))
        self._assertFunctionsEqual(Compose.G, __unit__.compose(Compose.G))
        self._assertFunctionsEqual(Compose.H, __unit__.compose(Compose.H))

    def test_two_functions(self):
        self._assertFunctionsEqual(
            Compose.FG, __unit__.compose(Compose.F, Compose.G))
        self._assertFunctionsEqual(
            Compose.GF, __unit__.compose(Compose.G, Compose.F))
        self._assertFunctionsEqual(
            Compose.FH, __unit__.compose(Compose.F, Compose.H))
        self._assertFunctionsEqual(
            Compose.HF, __unit__.compose(Compose.H, Compose.F))
        self._assertFunctionsEqual(
            Compose.GH, __unit__.compose(Compose.G, Compose.H))
        self._assertFunctionsEqual(
            Compose.HG, __unit__.compose(Compose.H, Compose.G))

    def test_associativity(self):
        self._assertFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.F, Compose.GH))
        self._assertFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.FG, Compose.H))

        self._assertFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.H, Compose.GF))
        self._assertFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.HG, Compose.F))

    def test_three_functions(self):
        self._assertFunctionsEqual(
            Compose.FGH, __unit__.compose(Compose.F, Compose.G, Compose.H))
        self._assertFunctionsEqual(
            Compose.HGF, __unit__.compose(Compose.H, Compose.G, Compose.F))

    def _assertFunctionsEqual(self, f, g, domain=None):
        if domain is None:
            domain = xrange(-512, 512 + 1)
        for x in domain:
            self.assertEquals(f(x), g(x))


class LogicalCombinators(TestCase):
    pass
