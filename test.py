"""
Test suite for pyoload 4.0.
"""

import functools
import inspect
import os
import sys
import types
import typing
import unittest
import warnings

sys.path.insert(0, "src")
import pyoload


class TestGetName(unittest.TestCase):
    def test_plain_function(self):
        def my_func(): pass
        self.assertIn("my_func", pyoload.get_name(my_func))

    def test_builtin(self):
        self.assertEqual(pyoload.get_name(print), "builtins.print")

    def test_class(self):
        class Foo: pass
        self.assertIn("Foo", pyoload.get_name(Foo))

    def test_method(self):
        class Bar:
            def baz(self): pass
        self.assertIn("baz", pyoload.get_name(Bar.baz))


class TestTypeMatchBasic(unittest.TestCase):
    def assertMatch(self, val, spec):
        ok, msg = pyoload.type_match(val, spec)
        self.assertTrue(ok, f"{val!r} should match {spec!r} but got: {msg}")

    def assertNoMatch(self, val, spec):
        ok, msg = pyoload.type_match(val, spec)
        self.assertFalse(ok, f"{val!r} should NOT match {spec!r}")

    def test_int_ok(self):            self.assertMatch(1, int)
    def test_str_ok(self):            self.assertMatch("hi", str)
    def test_float_ok(self):          self.assertMatch(3.14, float)
    def test_int_fail(self):          self.assertNoMatch("x", int)
    def test_none_type(self):         self.assertMatch(None, type(None))
    def test_bool_not_int(self):      self.assertNoMatch(True, int)
    def test_bool_as_bool(self):      self.assertMatch(True, bool)

    def test_any_accepts_all(self):
        for v in (1, "x", None, [], object()):
            self.assertMatch(v, typing.Any)

    def test_union_first(self):       self.assertMatch(1, int | str)
    def test_union_second(self):      self.assertMatch("x", int | str)
    def test_union_fail(self):        self.assertNoMatch([], int | str)
    def test_optional_none(self):     self.assertMatch(None, typing.Optional[int])
    def test_optional_value(self):    self.assertMatch(42, typing.Optional[int])
    def test_optional_wrong(self):    self.assertNoMatch("x", typing.Optional[int])

    def test_literal_ok(self):        self.assertMatch("r", typing.Literal["r", "w", "a"])
    def test_literal_fail(self):      self.assertNoMatch("z", typing.Literal["r", "w", "a"])
    def test_literal_int(self):       self.assertMatch(1, typing.Literal[1, 2, 3])

    def test_bare_any_raises(self):
        with self.assertRaises(TypeError):
            pyoload.type_match(1, any)


class TestTypeMatchCollections(unittest.TestCase):
    def assertMatch(self, val, spec):
        ok, _ = pyoload.type_match(val, spec)
        self.assertTrue(ok)

    def assertNoMatch(self, val, spec):
        ok, _ = pyoload.type_match(val, spec)
        self.assertFalse(ok)

    def test_list_ok(self):           self.assertMatch([1, 2, 3], list[int])
    def test_list_fail(self):         self.assertNoMatch([1, "x"], list[int])
    def test_list_empty(self):        self.assertMatch([], list[int])
    def test_list_nested(self):       self.assertMatch([[1, 2], [3]], list[list[int]])
    def test_list_nested_fail(self):  self.assertNoMatch([[1, "x"]], list[list[int]])

    def test_tuple_fixed_ok(self):    self.assertMatch((1, "a"), tuple[int, str])
    def test_tuple_fixed_fail(self):  self.assertNoMatch((1, 2), tuple[int, str])
    def test_tuple_wrong_len(self):   self.assertNoMatch((1,), tuple[int, str])
    def test_tuple_homog_ok(self):    self.assertMatch((1, 2, 3), tuple[int, ...])

    def test_set_ok(self):            self.assertMatch({1, 2}, set[int])
    def test_set_fail(self):          self.assertNoMatch({1, "x"}, set[int])
    def test_frozenset_ok(self):      self.assertMatch(frozenset({1}), frozenset[int])

    def test_dict_ok(self):           self.assertMatch({"a": 1}, dict[str, int])
    def test_dict_bad_key(self):      self.assertNoMatch({1: 1}, dict[str, int])
    def test_dict_bad_val(self):      self.assertNoMatch({"a": "x"}, dict[str, int])
    def test_dict_empty(self):        self.assertMatch({}, dict[str, int])

    def test_typing_list(self):       self.assertMatch([1], typing.List[int])
    def test_typing_dict(self):       self.assertMatch({"k": 1}, typing.Dict[str, int])

    def test_max_iter_short_circuit(self):
        ok, _ = pyoload.type_match([1, "x"], list[int], max_iter=1)
        self.assertTrue(ok)

    def test_max_iter_still_fails(self):
        ok, _ = pyoload.type_match(["x", 1], list[int], max_iter=1)
        self.assertFalse(ok)


class TestTypeMatchCustomGeneric(unittest.TestCase):
    def setUp(self):
        pyoload.enable()

    def tearDown(self):
        pyoload.disable()

    def test_custom_generic_base_ok(self):
        T = typing.TypeVar("T")
        class Stack(typing.Generic[T]): pass

        s = Stack()
        ok, _ = pyoload.type_match(s, Stack)
        self.assertTrue(ok)

    def test_custom_generic_base_fail(self):
        T = typing.TypeVar("T")
        class Stack(typing.Generic[T]): pass

        ok, _ = pyoload.type_match("not a stack", Stack)
        self.assertFalse(ok)


class TestResolveAnnotations(unittest.TestCase):
    def test_string_resolved_function(self):
        def f(x: "int") -> "str": return str(x)
        pyoload.resolve_annotations(f)
        self.assertIs(f.__annotations__["x"], int)
        self.assertIs(f.__annotations__["return"], str)

    def test_none_becomes_nonetype(self):
        def f(x: None) -> None: pass
        pyoload.resolve_annotations(f)
        self.assertIs(f.__annotations__["x"], type(None))

    def test_class_annotations(self):
        class MyClass:
            x: "int"
            y: "str"
        pyoload.resolve_annotations(MyClass)
        self.assertIs(MyClass.__annotations__["x"], int)
        self.assertIs(MyClass.__annotations__["y"], str)

    def test_no_annotations_raises(self):
        with self.assertRaises(TypeError):
            pyoload.resolve_annotations(42)


class TestAnnotateFunction(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_correct_int(self):
        @pyoload.annotate_function
        def add(a: int, b: int) -> int: return a + b
        self.assertEqual(add(1, 2), 3)

    def test_wrong_arg_type(self):
        @pyoload.annotate_function
        def neg(x: int) -> int: return -x
        with self.assertRaises(TypeError):
            neg("bad")

    def test_wrong_return_type(self):
        @pyoload.annotate_function
        def bad_ret(x: int) -> str: return x
        with self.assertRaises(TypeError):
            bad_ret(5)

    def test_no_annotations_pass_through(self):
        @pyoload.annotate_function
        def plain(x, y): return x + y
        self.assertEqual(plain(1, 2), 3)

    def test_bool_not_accepted_as_int(self):
        @pyoload.annotate_function
        def takes_int(x: int) -> int: return x
        with self.assertRaises(TypeError):
            takes_int(True)

    def test_optional_none(self):
        @pyoload.annotate_function
        def greet(name: typing.Optional[str] = None) -> str:
            return f"Hello {name}"
        self.assertEqual(greet(), "Hello None")
        self.assertEqual(greet("World"), "Hello World")

    def test_optional_wrong_type(self):
        @pyoload.annotate_function
        def greet(name: typing.Optional[str] = None) -> str:
            return f"Hello {name}"
        with self.assertRaises(TypeError):
            greet(42)

    def test_union(self):
        @pyoload.annotate_function
        def stringify(v: int | str) -> str: return str(v)
        self.assertEqual(stringify(1), "1")
        self.assertEqual(stringify("hi"), "hi")
        with self.assertRaises(TypeError):
            stringify([])

    def test_list_type_ok(self):
        @pyoload.annotate_function
        def total(items: list[int]) -> int: return sum(items)
        self.assertEqual(total([1, 2, 3]), 6)

    def test_list_type_fail(self):
        @pyoload.annotate_function
        def total(items: list[int]) -> int: return sum(items)
        with self.assertRaises(TypeError):
            total([1, "x"])

    def test_dict_type(self):
        @pyoload.annotate_function
        def lookup(d: dict[str, int], k: str) -> int: return d[k]
        self.assertEqual(lookup({"a": 1}, "a"), 1)
        with self.assertRaises(TypeError):
            lookup({1: 1}, "a")

    def test_tuple_fixed(self):
        @pyoload.annotate_function
        def swap(t: tuple[int, str]) -> tuple[str, int]: return (t[1], t[0])
        self.assertEqual(swap((1, "x")), ("x", 1))

    def test_literal(self):
        @pyoload.annotate_function
        def open_file(mode: typing.Literal["r", "w", "a"]) -> None: pass
        open_file("r")
        with self.assertRaises(TypeError):
            open_file("z")

    def test_idempotent(self):
        @pyoload.annotate_function
        @pyoload.annotate_function
        def f(x: int) -> int: return x
        self.assertTrue(pyoload.is_annotated(f))
        self.assertEqual(f(1), 1)

    def test_forward_ref_string(self):
        @pyoload.annotate_function
        def make() -> "int": return 42
        self.assertEqual(make(), 42)

    def test_no_return_annotation_warns_once(self):
        @pyoload.annotate_function
        def f(x: int): return x

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            f(1)
            self.assertEqual(len(w), 1)
            self.assertIn("return", str(w[0].message).lower())

        with warnings.catch_warnings(record=True) as w2:
            warnings.simplefilter("always")
            f(2)
            self.assertEqual(len(w2), 0)

    def test_bad_default_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            @pyoload.annotate_function
            def f(x: int = "wrong") -> int: return x
            self.assertTrue(any("default" in str(x.message).lower() for x in w))

    def test_validator_pass(self):
        @pyoload.annotate_function(validators={"x": lambda v: None if v > 0 else "must be positive"})
        def pos(x: int) -> int: return x
        self.assertEqual(pos(5), 5)

    def test_validator_fail(self):
        @pyoload.annotate_function(validators={"x": lambda v: None if v > 0 else "must be positive"})
        def pos(x: int) -> int: return x
        with self.assertRaises(ValueError):
            pos(-1)

    def test_return_validator(self):
        @pyoload.annotate_function(validators={"return": lambda v: None if v < 100 else "too big"})
        def f(x: int) -> int: return x
        with self.assertRaises(ValueError):
            f(200)

    def test_max_iter_annotate(self):
        @pyoload.annotate_function(max_iter=1)
        def f(items: list[int]) -> int: return items[0]
        self.assertEqual(f([1, "x"]), 1)

    def test_called_form_no_args(self):
        @pyoload.annotate_function()
        def f(x: int) -> int: return x
        self.assertEqual(f(3), 3)
        with self.assertRaises(TypeError):
            f("bad")

    def test_mutable_default_warn(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            @pyoload.annotate_function
            def f(items: list = []) -> list: return items
            self.assertTrue(any("mutable" in str(x.message).lower() for x in w))

    def test_unannotated_param_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            @pyoload.annotate_function
            def f(x: int, y) -> int: return x
            self.assertTrue(any("annotation" in str(x.message).lower() for x in w))


class TestAnnotateClass(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_type_check_ok(self):
        @pyoload.annotate_class
        class Point:
            x: int
            y: int
            def __init__(self, x: int, y: int):
                self.x = x
                self.y = y
        p = Point(1, 2)
        self.assertEqual(p.x, 1)

    def test_type_check_fail(self):
        @pyoload.annotate_class
        class Point:
            x: int
            y: int
            def __init__(self, x: int, y: int):
                self.x = x
                self.y = y
        p = Point(3, 4)
        with self.assertRaises(TypeError):
            p.x = "bad"

    def test_strict_no_annotation_raises(self):
        @pyoload.annotate_class
        class Strict:
            name: str
            def __init__(self): self.name = "ok"
        s = Strict()
        with self.assertRaises(AttributeError):
            s.unknown = 42

    def test_private_attr_no_annotation_ok(self):
        @pyoload.annotate_class
        class Cls:
            x: int
            def __init__(self):
                self.x = 1
                self._cache = {}
        c = Cls()
        self.assertEqual(c._cache, {})

    def test_non_strict_allows_unannotated(self):
        @pyoload.annotate_class(strict=False)
        class Relaxed:
            x: int
            def __init__(self):
                self.x = 1
                self.free = "anything"
        r = Relaxed()
        self.assertEqual(r.free, "anything")

    def test_recur_annotates_methods(self):
        @pyoload.annotate_class
        class Math:
            result: int
            def __init__(self): self.result = 0
            def add(self, a: int, b: int) -> int: return a + b
        m = Math()
        self.assertEqual(m.add(1, 2), 3)
        with self.assertRaises(TypeError):
            m.add("x", 2)

    def test_init_also_annotated(self):
        @pyoload.annotate_class
        class Cls:
            x: int
            def __init__(self, x: int): self.x = x
        with self.assertRaises(TypeError):
            Cls("bad")

    def test_norecur_skips_method_wrapping(self):
        @pyoload.annotate_class
        class NoRecur:
            __pyod_norecur__ = True
            x: int
            def __init__(self): self.x = 1
            def helper(self, v): return v
        n = NoRecur()
        self.assertEqual(n.helper("anything"), "anything")

    def test_inheritance_base_annotation(self):
        @pyoload.annotate_class
        class Base:
            x: int
            def __init__(self): self.x = 0

        @pyoload.annotate_class
        class Child(Base):
            y: str
            def __init__(self):
                super().__init__()
                self.y = "hi"

        c = Child()
        with self.assertRaises(TypeError):
            c.x = "bad"
        with self.assertRaises(TypeError):
            c.y = 999

    def test_validator_class(self):
        @pyoload.annotate_class(
            validators={"age": lambda v: "too young" if v < 0 else None}
        )
        class Person:
            age: int
            def __init__(self): self.age = 25
        p = Person()
        with self.assertRaises(TypeError):
            p.age = -1

    def test_called_form_keyword_only(self):
        @pyoload.annotate_class(strict=False)
        class K:
            x: int
            def __init__(self): self.x = 1
        k = K()
        k.y = "free"

    def test_annotate_class_marks_class(self):
        @pyoload.annotate_class
        class Foo:
            x: int
            def __init__(self): self.x = 0
        self.assertTrue(getattr(Foo, "__pyod_annotate__", False))

    def test_classvar_ignored(self):
        @pyoload.annotate_class
        class WithCV:
            count: typing.ClassVar[int] = 0
            x: int
            def __init__(self): self.x = 1
        w = WithCV()
        with self.assertRaises(TypeError):
            w.x = "bad"


class TestAnnotateModule(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def _make_module(self, name: str) -> types.ModuleType:
        mod = types.ModuleType(name)
        mod.__name__ = name
        sys.modules[name] = mod
        return mod

    def _cleanup(self, *names: str) -> None:
        for n in names:
            sys.modules.pop(n, None)

    def test_annotates_functions(self):
        mod = self._make_module("_test_am_funcs")
        def greet(name: str) -> str: return f"Hello {name}"
        greet.__module__ = "_test_am_funcs"
        mod.greet = greet

        pyoload.annotate_module(mod)
        self.assertTrue(pyoload.is_annotated(mod.greet))
        with self.assertRaises(TypeError):
            mod.greet(123)
        self._cleanup("_test_am_funcs")

    def test_annotates_classes(self):
        mod = self._make_module("_test_am_classes")
        class Box:
            value: int
            def __init__(self): self.value = 0
        Box.__module__ = "_test_am_classes"
        mod.Box = Box
        sys.modules["_test_am_classes"] = mod

        pyoload.annotate_module(mod)
        b = mod.Box()
        with self.assertRaises(TypeError):
            b.value = "bad"
        self._cleanup("_test_am_classes")

    def test_skips_private_names(self):
        mod = self._make_module("_test_am_private")
        def _private(x: int) -> int: return x
        _private.__module__ = "_test_am_private"
        mod._private = _private

        pyoload.annotate_module(mod)
        self.assertFalse(pyoload.is_annotated(mod._private))
        self._cleanup("_test_am_private")

    def test_skips_imported_objects(self):
        mod = self._make_module("_test_am_foreign")
        mod.print = print

        pyoload.annotate_module(mod)
        self.assertIs(mod.print, print)
        self._cleanup("_test_am_foreign")

    def test_returns_module(self):
        mod = self._make_module("_test_am_ret")
        result = pyoload.annotate_module(mod)
        self.assertIs(result, mod)
        self._cleanup("_test_am_ret")

    def test_wrong_arg_raises(self):
        with self.assertRaises(TypeError):
            pyoload.annotate_module("not a module")


class TestAnnotateDispatcher(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_prod_is_noop(self):
        pyoload.disable()
        def original(x): return x
        self.assertIs(pyoload.pyoload(original), original)

    def test_prod_class_noop(self):
        pyoload.disable()
        class Foo: pass
        self.assertIs(pyoload.pyoload(Foo), Foo)

    def test_dispatches_function(self):
        @pyoload.pyoload
        def f(x: int) -> int: return x
        self.assertTrue(pyoload.is_annotated(f))

    def test_dispatches_class(self):
        @pyoload.pyoload
        class C:
            x: int
            def __init__(self): self.x = 0
        self.assertTrue(getattr(C, "__pyod_annotate__", False))

    def test_called_form_strict_false(self):
        @pyoload.pyoload(strict=False)
        class K:
            x: int
            def __init__(self): self.x = 0
        k = K()
        k.anything = 99

    def test_called_form_no_args(self):
        @pyoload.pyoload()
        def f(x: int) -> int: return x
        self.assertEqual(f(1), 1)
        with self.assertRaises(TypeError):
            f("bad")

    def test_dispatches_module(self):
        mod = types.ModuleType("_test_disp_mod")
        mod.__name__ = "_test_disp_mod"
        sys.modules["_test_disp_mod"] = mod
        result = pyoload.pyoload(mod)
        self.assertIs(result, mod)
        sys.modules.pop("_test_disp_mod", None)


class TestModuleCallable(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_bare_decorator_function(self):
        import pyoload as p

        @p
        def mul(a: int, b: int) -> int: return a * b

        self.assertEqual(mul(2, 3), 6)
        with self.assertRaises(TypeError):
            mul("x", 3)

    def test_bare_decorator_class(self):
        import pyoload as p

        @p
        class MyClass:
            x: int
            def __init__(self): self.x = 0

        obj = MyClass()
        with self.assertRaises(TypeError):
            obj.x = "bad"

    def test_called_decorator_with_kwargs(self):
        import pyoload as p

        @p(strict=False)
        def f(x: int) -> int: return x

        self.assertEqual(f(1), 1)
        with self.assertRaises(TypeError):
            f("x")

    def test_module_repr(self):
        import pyoload as p
        self.assertIn("pyoload", repr(p))
        self.assertIn("4.0", repr(p))


class TestModeAndInit(unittest.TestCase):
    def tearDown(self): pyoload.disable()

    def test_enable_disable(self):
        pyoload.enable()
        self.assertTrue(pyoload.is_enabled())
        pyoload.disable()
        self.assertFalse(pyoload.is_enabled())

    def test_init_from_env_enabled(self):
        os.environ["PYOLOAD_ENABLED"] = "true"
        pyoload.init()
        self.assertTrue(pyoload.is_enabled())
        os.environ.pop("PYOLOAD_ENABLED")

    def test_init_from_env_disabled(self):
        os.environ["PYOLOAD_ENABLED"] = "false"
        pyoload.init()
        self.assertFalse(pyoload.is_enabled())
        os.environ.pop("PYOLOAD_ENABLED")


class TestCallbackHooks(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_function_callback_pass(self):
        def cb(bound, ret):
            if ret > 100:
                return "return value too large"
            return None

        @pyoload.annotate_function(callback=cb)
        def add(a: int, b: int) -> int:
            return a + b

        self.assertEqual(add(10, 20), 30)

    def test_function_callback_fail(self):
        def cb(bound, ret):
            if ret > 100:
                return "return value too large"
            return None

        @pyoload.annotate_function(callback=cb)
        def add(a: int, b: int) -> int:
            return a + b

        with self.assertRaises(TypeError):
            add(60, 50)

    def test_class_callback_pass(self):
        def cb(instance, attr_name, val):
            if attr_name == "age" and val < 0:
                return "age cannot be negative"
            return None

        @pyoload.annotate_class(callback=cb)
        class Person:
            age: int
            def __init__(self, age: int):
                self.age = age

        p = Person(25)
        self.assertEqual(p.age, 25)

    def test_class_callback_fail(self):
        def cb(instance, attr_name, val):
            if attr_name == "age" and val < 0:
                return "age cannot be negative"
            return None

        @pyoload.annotate_class(callback=cb)
        class Person:
            age: int
            def __init__(self, age: int):
                self.age = age

        with self.assertRaises(TypeError):
            Person(-5)


class TestIsValid(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_is_valid_true(self):
        self.assertTrue(pyoload.is_valid(42, int))

    def test_is_valid_false(self):
        self.assertFalse(pyoload.is_valid("x", int))

    def test_is_valid_always_runs(self):
        pyoload.disable()
        self.assertFalse(pyoload.is_valid("x", int))

    def test_is_valid_collection(self):
        self.assertTrue(pyoload.is_valid([1, 2, 3], list[int]))
        self.assertFalse(pyoload.is_valid([1, "x"], list[int]))


class TestValidatorHelpers(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def _wrap(self, validators):
        @pyoload.annotate_function(validators=validators)
        def f(x: int) -> int: return x
        return f

    def test_gt_pass(self):     self.assertEqual(self._wrap({"x": pyoload.gt(0)})(5), 5)
    def test_gt_fail(self):
        with self.assertRaises(ValueError): self._wrap({"x": pyoload.gt(0)})(0)

    def test_lt_pass(self):     self.assertEqual(self._wrap({"x": pyoload.lt(10)})(5), 5)
    def test_lt_fail(self):
        with self.assertRaises(ValueError): self._wrap({"x": pyoload.lt(10)})(10)

    def test_ge_pass(self):     self.assertEqual(self._wrap({"x": pyoload.ge(0)})(0), 0)
    def test_ge_fail(self):
        with self.assertRaises(ValueError): self._wrap({"x": pyoload.ge(1)})(-1)

    def test_le_pass(self):     self.assertEqual(self._wrap({"x": pyoload.le(5)})(5), 5)
    def test_le_fail(self):
        with self.assertRaises(ValueError): self._wrap({"x": pyoload.le(5)})(6)

    def test_non_empty_str_pass(self):
        self.assertIsNone(pyoload.non_empty("hi"))
    def test_non_empty_str_fail(self):
        self.assertIsNotNone(pyoload.non_empty(""))
    def test_non_empty_list_pass(self):
        self.assertIsNone(pyoload.non_empty([1]))
    def test_non_empty_list_fail(self):
        self.assertIsNotNone(pyoload.non_empty([]))

    def test_positive_pass(self):   self.assertIsNone(pyoload.positive(1))
    def test_positive_fail(self):   self.assertIsNotNone(pyoload.positive(0))
    def test_negative_pass(self):   self.assertIsNone(pyoload.negative(-1))
    def test_negative_fail(self):   self.assertIsNotNone(pyoload.negative(0))
    def test_non_zero_pass(self):   self.assertIsNone(pyoload.non_zero(1))
    def test_non_zero_fail(self):   self.assertIsNotNone(pyoload.non_zero(0))

    def test_finite_pass(self):     self.assertIsNone(pyoload.finite(3.14))
    def test_finite_nan_fail(self):
        import math
        self.assertIsNotNone(pyoload.finite(math.nan))
    def test_finite_inf_fail(self):
        self.assertIsNotNone(pyoload.finite(float("inf")))

    def test_regex_pass(self):
        self.assertIsNone(pyoload.regex(r"^\w+$")("hello"))
    def test_regex_fail(self):
        self.assertIsNotNone(pyoload.regex(r"^\w+$")("hello world"))

    def test_predicate_pass(self):
        v = pyoload.predicate(lambda x: x % 2 == 0, "must be even")
        self.assertIsNone(v(4))
    def test_predicate_fail(self):
        v = pyoload.predicate(lambda x: x % 2 == 0, "must be even")
        self.assertIsNotNone(v(3))

    def test_kwargs_validators_in_decorator(self):
        @pyoload.pyoload(
            n=pyoload.gt(0),
            name=pyoload.non_empty,
            return_=pyoload.non_empty,
        )
        def process(n: int, name: str) -> str:
            return name * n

        self.assertEqual(process(2, "hi"), "hihi")
        with self.assertRaises(ValueError):
            process(0, "hi")
        with self.assertRaises(ValueError):
            process(2, "")

    def test_multiple_validators_sequence(self):
        @pyoload.pyoload(
            age=[pyoload.ge(18), pyoload.le(100)],
        )
        def set_age(age: int) -> int:
            return age

        self.assertEqual(set_age(20), 20)
        with self.assertRaises(ValueError):
            set_age(17)
        with self.assertRaises(ValueError):
            set_age(105)


class TestTypedDict(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_typeddict_ok(self):
        class Point(typing.TypedDict):
            x: int
            y: int
        ok, _ = pyoload.type_match({"x": 1, "y": 2}, Point)
        self.assertTrue(ok)

    def test_typeddict_wrong_value_type(self):
        class Point(typing.TypedDict):
            x: int
            y: int
        ok, _ = pyoload.type_match({"x": "bad", "y": 2}, Point)
        self.assertFalse(ok)

    def test_typeddict_missing_required_key(self):
        class Point(typing.TypedDict):
            x: int
            y: int
        ok, _ = pyoload.type_match({"x": 1}, Point)
        self.assertFalse(ok)

    def test_typeddict_not_a_dict(self):
        class Point(typing.TypedDict):
            x: int
            y: int
        ok, _ = pyoload.type_match("not a dict", Point)
        self.assertFalse(ok)

    def test_typeddict_in_annotate(self):
        class Config(typing.TypedDict):
            host: str
            port: int

        @pyoload.annotate_function
        def connect(cfg: Config) -> str:
            return f"{cfg['host']}:{cfg['port']}"

        self.assertEqual(connect({"host": "localhost", "port": 8080}), "localhost:8080")
        with self.assertRaises(TypeError):
            connect({"host": "localhost", "port": "bad"})


class TestProtocolStructural(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_protocol_ok_structural(self):
        class Closeable(typing.Protocol):
            def close(self) -> None: ...

        class MyResource:
            def close(self): pass

        ok, _ = pyoload.type_match(MyResource(), Closeable)
        self.assertTrue(ok)

    def test_protocol_fail_missing_method(self):
        class Closeable(typing.Protocol):
            def close(self) -> None: ...

        ok, _ = pyoload.type_match(42, Closeable)
        self.assertFalse(ok)

    def test_runtime_checkable_protocol(self):
        @typing.runtime_checkable
        class Sized(typing.Protocol):
            def __len__(self) -> int: ...

        ok, _ = pyoload.type_match([1, 2, 3], Sized)
        self.assertTrue(ok)


class TestCallableType(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_callable_ok(self):
        ok, _ = pyoload.type_match(len, typing.Callable)
        self.assertTrue(ok)

    def test_callable_fail(self):
        ok, _ = pyoload.type_match(42, typing.Callable)
        self.assertFalse(ok)

    def test_callable_with_args(self):
        ok, _ = pyoload.type_match(lambda x: x, typing.Callable[[int], int])
        self.assertTrue(ok)

    def test_callable_in_annotate(self):
        @pyoload.annotate_function
        def apply(fn: typing.Callable, x: int) -> int:
            return fn(x)
        self.assertEqual(apply(lambda x: x * 2, 3), 6)
        with self.assertRaises(TypeError):
            apply(42, 3)


class TestSpecialTypes(unittest.TestCase):
    def test_never_always_false(self):
        if hasattr(typing, "Never"):
            ok, _ = pyoload.type_match(42, typing.Never)
            self.assertFalse(ok)

    def test_noreturn_always_false(self):
        ok, _ = pyoload.type_match(42, typing.NoReturn)
        self.assertFalse(ok)

    def test_literalstring(self):
        if hasattr(typing, "LiteralString"):
            ok, _ = pyoload.type_match("hello", typing.LiteralString)
            self.assertTrue(ok)
            ok, _ = pyoload.type_match(42, typing.LiteralString)
            self.assertFalse(ok)


class TestPEP563(unittest.TestCase):
    def setUp(self):    pyoload.enable()
    def tearDown(self): pyoload.disable()

    def test_string_annotation_resolves(self):
        def f(x: "int") -> "str": return str(x)
        pyoload.resolve_annotations(f)
        self.assertIs(f.__annotations__["x"], int)
        self.assertIs(f.__annotations__["return"], str)

    def test_string_annotation_in_wrapper(self):
        @pyoload.annotate_function
        def f(x: "int") -> "str": return str(x)
        self.assertEqual(f(42), "42")
        with self.assertRaises(TypeError):
            f("not int")


class TestZeroLockIn(unittest.TestCase):
    def test_stub_function_decorator(self):
        stub_pyoload = lambda *a, **kw: (a[0] if a and callable(a[0]) else lambda f: f)

        @stub_pyoload
        def add(a: int, b: int) -> int: return a + b

        self.assertEqual(add(1, 2), 3)

    def test_stub_class_decorator(self):
        stub_pyoload = lambda *a, **kw: (a[0] if a and callable(a[0]) else lambda f: f)

        @stub_pyoload
        class Point:
            x: int
            y: int
            def __init__(self, x, y): self.x = x; self.y = y

        p = Point(1, 2)
        self.assertEqual(p.x, 1)

    def test_function_signature_unchanged(self):
        import pyoload as p

        pyoload.enable()
        @p
        def greet(name: str) -> str: return f"Hello {name}"

        sig = inspect.signature(greet)
        self.assertIs(sig.parameters["name"].annotation, str)
        self.assertIs(sig.return_annotation, str)


class TestNewFeatures40(unittest.TestCase):
    def test_context_managers(self):
        pyoload.disable()
        self.assertFalse(pyoload.is_enabled())

        with pyoload.enabled():
            self.assertTrue(pyoload.is_enabled())

        self.assertFalse(pyoload.is_enabled())

        pyoload.enable()
        with pyoload.disabled():
            self.assertFalse(pyoload.is_enabled())
        self.assertTrue(pyoload.is_enabled())

    def test_union_detailed_failure_message(self):
        ok, msg = pyoload.type_match("bad", int | list[str])
        self.assertFalse(ok)
        self.assertIn("matched none of Union options", msg)
        self.assertIn("Option 0", msg)
        self.assertIn("Option 1", msg)

    def test_dataclass_decoration(self):
        import dataclasses
        pyoload.enable()

        @pyoload
        @dataclasses.dataclass
        class Person:
            name: str
            age: int

        p = Person("Alice", 30)
        self.assertEqual(p.name, "Alice")
        with self.assertRaises(TypeError):
            p.age = "wrong"


if __name__ == "__main__":
    unittest.main(verbosity=2)
