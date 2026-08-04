"""
pyoload 4.0 — Zero-overhead, zero-lock-in runtime type-checking for Python.
"""

import collections.abc
import dataclasses
import functools
import inspect
import os
import re as _re
import sys
import types
import typing
import warnings

__version__: str = "4.0.0"

ENABLED: bool = False

MUTABLE_DEFAULT_TYPES: set[type] = {list, dict, set, bytearray}

CLASSVAR_ORIGINS: set[typing.Any] = {typing.ClassVar, typing.Final}

MAPPING_ORIGINS: set[typing.Any] = {
    dict,
    collections.abc.Mapping,
    collections.abc.MutableMapping,
}

SEQUENCE_ORIGINS: set[typing.Any] = {
    list,
    tuple,
    set,
    frozenset,
    collections.abc.Sequence,
    collections.abc.MutableSequence,
    collections.abc.Iterable,
    collections.abc.Iterator,
    collections.abc.Set,
    collections.abc.MutableSet,
}


def enable() -> None:
    """Enable runtime type-checking in pyoload."""
    global ENABLED
    ENABLED = True


def disable() -> None:
    """Disable runtime type-checking in pyoload (zero overhead)."""
    global ENABLED
    ENABLED = False


def is_enabled() -> bool:
    """Return True if pyoload type-checking is active."""
    return ENABLED


class override_state:
    """Context manager to temporarily override pyoload ENABLED state."""

    def __init__(self, target_state: bool) -> None:
        self.target_state: bool = target_state
        self.previous_state: bool = False

    def __enter__(self) -> "override_state":
        global ENABLED
        self.previous_state = ENABLED
        ENABLED = self.target_state
        return self

    def __exit__(
        self,
        exc_type: typing.Optional[type],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None:
        global ENABLED
        ENABLED = self.previous_state


def disabled() -> override_state:
    """Context manager temporarily disabling pyoload type checking."""
    return override_state(False)


def enabled() -> override_state:
    """Context manager temporarily enabling pyoload type checking."""
    return override_state(True)


def init() -> None:
    """Initialize activation state from environment variables PYOLOAD_ENABLED or PYOLOAD_MODE."""
    global ENABLED
    enabled_env: typing.Optional[str] = os.getenv("PYOLOAD_ENABLED")
    if enabled_env is not None:
        if enabled_env.lower() in ("true", "1", "yes", "dev"):
            enable()
        else:
            disable()
    else:
        mode_env: typing.Optional[str] = os.getenv("PYOLOAD_MODE")
        if mode_env is not None:
            if mode_env.lower() in ("dev", "true", "1", "debug"):
                enable()
            else:
                disable()
        else:
            disable()


def get_name(obj: typing.Any) -> str:
    """Return a dotted name string for the given object."""
    if hasattr(obj, "__module__"):
        mod: str = getattr(obj, "__module__")
    else:
        mod = type(obj).__module__

    if hasattr(obj, "__qualname__"):
        name: str = getattr(obj, "__qualname__")
    else:
        name = type(obj).__qualname__

    return f"{mod}.{name}"


def is_annotated(func: typing.Callable[..., typing.Any]) -> bool:
    """Return True if func has already been annotated by pyoload."""
    if hasattr(func, "__pyod_annotate__"):
        return bool(getattr(func, "__pyod_annotate__"))
    else:
        return False


def all_annotations(klass: type) -> dict[str, typing.Any]:
    """Collect annotations from class MRO hierarchy."""
    result: dict[str, typing.Any] = {}
    for base in reversed(getattr(klass, "__mro__", [])):
        result.update(getattr(base, "__annotations__", {}))
    return result


def is_typeddict(tp: typing.Any) -> bool:
    """Return True if tp is a TypedDict class."""
    if hasattr(typing, "is_typeddict"):
        return typing.is_typeddict(tp)
    else:
        if isinstance(tp, type) and issubclass(tp, dict) and hasattr(tp, "__required_keys__"):
            return True
        else:
            return False


def is_protocol(tp: typing.Any) -> bool:
    """Return True if tp is a Protocol subclass."""
    if isinstance(tp, type):
        if getattr(tp, "_is_protocol", False) or hasattr(tp, "__protocol_attrs__"):
            return True
        else:
            return False
    else:
        return False


def protocol_members(proto: type) -> frozenset[str]:
    """Return protocol declared member names."""
    if hasattr(proto, "__protocol_attrs__"):
        return frozenset(getattr(proto, "__protocol_attrs__"))
    else:
        members: set[str] = set()
        for name in vars(proto):
            if name.startswith("_"):
                continue
            else:
                if name in vars(object):
                    continue
                else:
                    members.add(name)
        return frozenset(members)


def resolve_annotations(obj: typing.Any) -> None:
    """Resolve string annotations in-place for functions or classes."""
    if not hasattr(obj, "__annotations__"):
        raise TypeError(f"Object {obj!r} has no __annotations__ attribute.")
    else:
        if inspect.isfunction(obj) or inspect.isclass(obj):
            try:
                hints: dict[str, typing.Any] = typing.get_type_hints(obj, include_extras=True)
                getattr(obj, "__annotations__").update(hints)
            except Exception:
                pass
        else:
            pass

        raw_annotations: dict[str, typing.Any] = getattr(obj, "__annotations__")
        for key, val in list(raw_annotations.items()):
            if val is None:
                raw_annotations[key] = types.NoneType
            else:
                pass

        if inspect.isfunction(obj):
            globs: dict[str, typing.Any] = getattr(obj, "__globals__", {})
            mod_obj: typing.Optional[types.ModuleType] = inspect.getmodule(obj)
            if mod_obj is not None:
                local_ns: dict[str, typing.Any] = dict(vars(mod_obj))
            else:
                local_ns = {}
            for k, v in list(raw_annotations.items()):
                if isinstance(v, str):
                    try:
                        raw_annotations[k] = eval(v, globs, local_ns)
                    except Exception:
                        pass
                else:
                    pass
        elif inspect.isclass(obj):
            ns: dict[str, typing.Any] = {}
            for base in reversed(getattr(obj, "__mro__", [])):
                mod_b: typing.Optional[types.ModuleType] = inspect.getmodule(base)
                if mod_b is not None:
                    ns.update(vars(mod_b))
                else:
                    pass
                ns.update(vars(base))
            for k, v in list(raw_annotations.items()):
                if isinstance(v, str):
                    try:
                        raw_annotations[k] = eval(v, ns)
                    except Exception:
                        pass
                else:
                    pass
        else:
            pass


def _run_validator(
    validator_obj: typing.Any,
    value: typing.Any,
) -> typing.Optional[str]:
    """Execute a single validator or sequence of validators against value."""
    if isinstance(validator_obj, (list, tuple, set)):
        for single_v in validator_obj:
            if callable(single_v):
                msg: typing.Optional[str] = single_v(value)
                if msg:
                    return msg
                else:
                    pass
            else:
                pass
        return None
    else:
        if callable(validator_obj):
            return validator_obj(value)
        else:
            return None


def type_match(
    val: typing.Any,
    spec: typing.Any,
    max_iter: typing.Optional[int] = None,
) -> tuple[bool, typing.Optional[str]]:
    """Recursively verify whether val matches spec annotation."""
    if spec is typing.Any:
        return (True, None)
    else:
        if val.__class__ is bool and spec is int:
            return (False, "bool value is not accepted where int type is required")
        else:
            try:
                if isinstance(val, spec):
                    return (True, None)
                else:
                    if inspect.isclass(spec) and typing.get_origin(spec) is None and not is_typeddict(spec) and not is_protocol(spec):
                        return (False, f"value {val!r} of type {type(val).__name__} is not an instance of {get_name(spec)}")
                    else:
                        pass
            except TypeError:
                pass

            if is_typeddict(spec):
                if not isinstance(val, dict):
                    return (False, f"value {val!r} of type {type(val).__name__} is not a dict as required by TypedDict {spec.__name__}")
                else:
                    try:
                        hints: dict[str, typing.Any] = typing.get_type_hints(spec, include_extras=True)
                    except Exception:
                        hints = getattr(spec, "__annotations__", {})

                    for req_key in getattr(spec, "__required_keys__", set()):
                        if req_key not in val:
                            return (False, f"Required key {req_key!r} is missing from TypedDict {spec.__name__}")
                        else:
                            pass

                    for key_name, key_type in hints.items():
                        if key_name in val:
                            ok, msg = type_match(val[key_name], key_type, max_iter)
                            if not ok:
                                return (False, f"TypedDict {spec.__name__} key {key_name!r} failed validation: {msg}")
                            else:
                                pass
                        else:
                            pass

                    return (True, None)
            else:
                _Never: typing.Any = getattr(typing, "Never", None)
                _NoReturn: typing.Any = getattr(typing, "NoReturn", None)
                if spec is _Never or (spec is not None and spec is _NoReturn):
                    return (False, f"type spec is Never/NoReturn; value {val!r} is unexpected")
                else:
                    _LitStr: typing.Any = getattr(typing, "LiteralString", None)
                    if _LitStr is not None and spec is _LitStr:
                        if isinstance(val, str):
                            return (True, None)
                        else:
                            return (False, f"value {val!r} of type {type(val).__name__} is not a str")
                    else:
                        origin: typing.Any = typing.get_origin(spec)

                        if origin is typing.Literal:
                            literals: tuple[typing.Any, ...] = typing.get_args(spec)
                            if val in literals:
                                return (True, None)
                            else:
                                return (False, f"value {val!r} is not one of allowed Literal values {literals!r}")
                        elif origin in (typing.Union, types.UnionType):
                            sub_specs: tuple[typing.Any, ...] = typing.get_args(spec)
                            failures: list[str] = []
                            for idx, sub_spec in enumerate(sub_specs):
                                ok, sub_msg = type_match(val, sub_spec, max_iter)
                                if ok:
                                    return (True, None)
                                else:
                                    failures.append(f"  - Option {idx} ({sub_spec!r}): {sub_msg}")
                            failure_details: str = "\n".join(failures)
                            return (False, f"value {val!r} matched none of Union options:\n{failure_details}")
                        elif origin in CLASSVAR_ORIGINS:
                            args_inner: tuple[typing.Any, ...] = typing.get_args(spec)
                            if args_inner:
                                return type_match(val, args_inner[0], max_iter)
                            else:
                                return (True, None)
                        elif origin is not None:
                            if origin is collections.abc.Callable:
                                if callable(val):
                                    return (True, None)
                                else:
                                    return (False, f"value {val!r} is not callable as required by spec {spec!r}")
                            else:
                                try:
                                    base_ok: bool = isinstance(val, origin)
                                except TypeError:
                                    base_ok = True

                                if not base_ok:
                                    return (False, f"value {val!r} of type {type(val).__name__} is not an instance of base type {origin!r}")
                                else:
                                    args: tuple[typing.Any, ...] = typing.get_args(spec)
                                    if not args:
                                        return (True, None)
                                    else:
                                        if origin in MAPPING_ORIGINS:
                                            key_type: typing.Any = args[0] if len(args) >= 1 else typing.Any
                                            val_type: typing.Any = args[1] if len(args) >= 2 else typing.Any
                                            count: int = 0
                                            for k_item, v_item in val.items():
                                                ok, msg = type_match(k_item, key_type, max_iter)
                                                if not ok:
                                                    return (False, f"Dict key {k_item!r} failed type spec {key_type!r}: {msg}")
                                                else:
                                                    pass

                                                ok, msg = type_match(v_item, val_type, max_iter)
                                                if not ok:
                                                    return (False, f"Dict value {v_item!r} for key {k_item!r} failed type spec {val_type!r}: {msg}")
                                                else:
                                                    pass

                                                count += 1
                                                if max_iter is not None and count >= max_iter:
                                                    break
                                                else:
                                                    pass
                                            return (True, None)
                                        elif origin is tuple and len(args) >= 1 and not (len(args) == 2 and args[-1] is ...):
                                            if len(args) != len(val):
                                                return (False, f"Tuple length {len(val)} does not match expected length {len(args)} for spec {spec!r}")
                                            else:
                                                for idx, (item, sub_spec) in enumerate(zip(val, args)):
                                                    ok, msg = type_match(item, sub_spec, max_iter)
                                                    if not ok:
                                                        return (False, f"Tuple element at index {idx} ({item!r}) failed type spec {sub_spec!r}: {msg}")
                                                    else:
                                                        pass
                                                return (True, None)
                                        elif origin in SEQUENCE_ORIGINS:
                                            sub_spec: typing.Any = args[0] if args else typing.Any
                                            count: int = 0
                                            try:
                                                it = iter(val)
                                            except TypeError:
                                                return (False, f"value {val!r} is not iterable")

                                            for idx, item in enumerate(it):
                                                ok, msg = type_match(item, sub_spec, max_iter)
                                                if not ok:
                                                    return (False, f"Iterable item at index {idx} ({item!r}) failed type spec {sub_spec!r}: {msg}")
                                                else:
                                                    pass
                                                count += 1
                                                if max_iter is not None and count >= max_iter:
                                                    break
                                                else:
                                                    pass
                                            return (True, None)
                                        else:
                                            warnings.warn(
                                                f"Cannot verify type arguments for custom generic {spec!r}; verified base type {origin!r} only.",
                                                stacklevel=5,
                                            )
                                            return (True, None)
                        elif is_protocol(spec) and not getattr(spec, "_is_runtime_protocol", False):
                            for member_name in protocol_members(spec):
                                if not hasattr(val, member_name):
                                    return (False, f"value {val!r} lacks attribute {member_name!r} required by Protocol {spec.__name__}")
                                else:
                                    pass
                            return (True, None)
                        elif spec is any:
                            raise TypeError("built-in 'any' passed as type spec; use typing.Any instead.")
                        else:
                            warnings.warn(
                                f"Cannot verify unknown type spec {spec!r}; skipping runtime check.",
                                stacklevel=5,
                            )
                            return (True, None)


def is_valid(
    val: typing.Any,
    spec: typing.Any,
    max_iter: typing.Optional[int] = None,
) -> bool:
    """Return True if val matches spec annotation, False otherwise."""
    ok, _ = type_match(val, spec, max_iter)
    return ok


def annotate_function(
    obj: typing.Optional[typing.Callable[..., typing.Any]] = None,
    *,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = None,
    max_iter: typing.Optional[int] = None,
    validators: dict[str, typing.Any] = {},
    **kwargs: typing.Any,
) -> typing.Callable[..., typing.Any]:
    """Wrap a function to type-check arguments, return values, and execute callbacks."""
    effective_validators: dict[str, typing.Any] = dict(validators)
    for k, v in kwargs.items():
        if k == "return_":
            effective_validators["return"] = v
        else:
            effective_validators[k] = v

    if obj is None:
        return functools.partial(annotate_function, callback=callback, max_iter=max_iter, validators=effective_validators)
    else:
        if not ENABLED:
            return obj
        else:
            if not callable(obj):
                warnings.warn(f"annotate_function received non-callable object {obj!r}.", stacklevel=2)
                return obj
            else:
                if inspect.isclass(obj):
                    return annotate_class(obj, callback=callback, validators=effective_validators)
                else:
                    if is_annotated(obj):
                        return obj
                    else:
                        if hasattr(obj, "__annotations__"):
                            resolve_annotations(obj)
                        else:
                            pass

                        try:
                            signature: inspect.Signature = inspect.signature(obj)
                        except (ValueError, TypeError):
                            return obj

                        for param in signature.parameters.values():
                            if param.name == "self":
                                continue
                            else:
                                if param.default is not inspect._empty and type(param.default) in MUTABLE_DEFAULT_TYPES:
                                    warnings.warn(
                                        f"Parameter '{param.name}' of function {get_name(obj)} has mutable default {param.default!r}.",
                                        stacklevel=2,
                                    )
                                else:
                                    pass

                                if param.annotation is inspect._empty:
                                    warnings.warn(
                                        f"Parameter '{param.name}' of function {get_name(obj)} lacks type annotation.",
                                        stacklevel=2,
                                    )
                                else:
                                    if param.default is not inspect._empty:
                                        if not isinstance(param.annotation, str):
                                            ok, msg = type_match(param.default, param.annotation, max_iter)
                                            if not ok:
                                                warnings.warn(
                                                    f"Default value {param.default!r} for parameter '{param.name}' of {get_name(obj)} does not match annotation {param.annotation!r}: {msg}",
                                                    stacklevel=2,
                                                )
                                            else:
                                                pass
                                        else:
                                            pass
                                    else:
                                        pass

                        if signature.return_annotation is inspect._empty:
                            warnings.warn(
                                f"Function {get_name(obj)} lacks return type annotation.",
                                stacklevel=2,
                            )
                        else:
                            pass

                        _sig: inspect.Signature = signature

                        @functools.wraps(obj)
                        def wrapper(*posargs: typing.Any, **kwargs_call: typing.Any) -> typing.Any:
                            nonlocal _sig
                            if hasattr(obj, "__annotations__") and any(isinstance(v, str) for v in getattr(obj, "__annotations__").values()):
                                resolve_annotations(obj)
                                try:
                                    _sig = inspect.signature(obj)
                                except Exception:
                                    pass
                            else:
                                pass

                            try:
                                bound: inspect.BoundArguments = _sig.bind(*posargs, **kwargs_call)
                            except TypeError as bind_err:
                                try:
                                    obj(*posargs, **kwargs_call)
                                except Exception as orig_err:
                                    raise orig_err from bind_err
                                raise TypeError(f"Failed to bind arguments for function {get_name(obj)}: {bind_err}") from bind_err

                            bound.apply_defaults()

                            for pname, arg in bound.arguments.items():
                                param_item: inspect.Parameter = _sig.parameters[pname]
                                ann: typing.Any = param_item.annotation
                                if ann is inspect._empty:
                                    continue
                                else:
                                    if isinstance(ann, str):
                                        raise TypeError(
                                            f"Parameter '{pname}' of function {get_name(obj)} has unresolved forward reference annotation {ann!r}."
                                        )
                                    else:
                                        if param_item.kind is inspect.Parameter.VAR_POSITIONAL:
                                            for idx, item in enumerate(arg):
                                                ok, msg = type_match(item, ann, max_iter)
                                                if not ok:
                                                    raise TypeError(
                                                        f"Variadic positional argument *{pname}[{idx}] = {item!r} of function {get_name(obj)} does not match expected annotation {ann!r}: {msg}"
                                                    )
                                                else:
                                                    pass
                                        elif param_item.kind is inspect.Parameter.VAR_KEYWORD:
                                            for key_name, val_item in arg.items():
                                                ok, msg = type_match(val_item, ann, max_iter)
                                                if not ok:
                                                    raise TypeError(
                                                        f"Variadic keyword argument **{pname}[{key_name!r}] = {val_item!r} of function {get_name(obj)} does not match expected annotation {ann!r}: {msg}"
                                                    )
                                                else:
                                                    pass
                                        else:
                                            ok, msg = type_match(arg, ann, max_iter)
                                            if not ok:
                                                raise TypeError(
                                                    f"Argument {arg!r} provided for parameter '{pname}' of function {get_name(obj)} does not match expected annotation {ann!r}: {msg}"
                                                )
                                            else:
                                                pass

                                        if pname in effective_validators:
                                            val_msg: typing.Optional[str] = _run_validator(effective_validators[pname], arg)
                                            if val_msg:
                                                raise ValueError(
                                                    f"Validator validation failed for parameter '{pname}' of function {get_name(obj)} with value {arg!r}: {val_msg}"
                                                )
                                            else:
                                                pass
                                        else:
                                            pass

                            ret: typing.Any = obj(*posargs, **kwargs_call)

                            ret_ann: typing.Any = _sig.return_annotation
                            if ret_ann is not inspect._empty:
                                if isinstance(ret_ann, str):
                                    raise TypeError(
                                        f"Return value of function {get_name(obj)} has unresolved forward reference annotation {ret_ann!r}."
                                    )
                                else:
                                    ok, msg = type_match(ret, ret_ann, max_iter)
                                    if not ok:
                                        raise TypeError(
                                            f"Return value {ret!r} of function {get_name(obj)} does not match expected return annotation {ret_ann!r}: {msg}"
                                        )
                                    else:
                                        pass

                                    if "return" in effective_validators:
                                        val_msg = _run_validator(effective_validators["return"], ret)
                                        if val_msg:
                                            raise ValueError(
                                                f"Return validator validation failed for function {get_name(obj)} with return value {ret!r}: {val_msg}"
                                            )
                                        else:
                                            pass
                                    else:
                                        pass
                            else:
                                if ret is not None:
                                    if not getattr(wrapper, "__pyod_warned_no_return__", False):
                                        setattr(wrapper, "__pyod_warned_no_return__", True)
                                        warnings.warn(
                                            f"Function {get_name(obj)} returned non-None value {ret!r} but lacks a return type annotation.",
                                            stacklevel=2,
                                        )
                                    else:
                                        pass
                                else:
                                    pass

                            if callback is not None:
                                cb_msg: typing.Optional[str] = callback(bound, ret)
                                if cb_msg:
                                    raise TypeError(
                                        f"Callback hook validation failed for function {get_name(obj)}: {cb_msg}"
                                    )
                                else:
                                    pass
                            else:
                                pass

                            return ret

                        setattr(wrapper, "__pyod_annotate__", True)
                        return wrapper


def annotate_class(
    cls: typing.Any = None,
    recur: bool = True,
    strict: bool = True,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = None,
    validators: dict[str, typing.Any] = {},
    **kwargs: typing.Any,
) -> typing.Any:
    """Annotate a class to type-check attribute assignments and run callbacks on mutation."""
    effective_validators: dict[str, typing.Any] = dict(validators)
    effective_validators.update(kwargs)

    if cls is None:
        return functools.partial(
            annotate_class, recur=recur, strict=strict, callback=callback, validators=effective_validators
        )
    else:
        if isinstance(cls, bool):
            return functools.partial(
                annotate_class, recur=cls, strict=strict, callback=callback, validators=effective_validators
            )
        else:
            if not ENABLED:
                return cls
            else:
                if not inspect.isclass(cls):
                    warnings.warn(
                        f"annotate_class received non-class object {cls!r}; returning as-is.",
                        stacklevel=2,
                    )
                    return cls
                else:
                    if hasattr(cls, "__annotations__"):
                        resolve_annotations(cls)
                    else:
                        pass

                    effective_recur: bool = recur and (not hasattr(cls, "__pyod_norecur__"))

                    if effective_recur:
                        for attr_name in list(vars(cls)):
                            if attr_name.startswith("_") and attr_name != "__init__":
                                continue
                            else:
                                attr_val: typing.Any = vars(cls)[attr_name]
                                if callable(attr_val) and hasattr(attr_val, "__annotations__"):
                                    try:
                                        setattr(cls, attr_name, annotate_function(attr_val))
                                    except Exception:
                                        pass
                                else:
                                    pass
                    else:
                        pass

                    initial_setter: typing.Callable[..., None] = cls.__setattr__

                    @functools.wraps(initial_setter)
                    def new_setter(self: typing.Any, name: str, value: typing.Any) -> None:
                        all_ann: dict[str, typing.Any] = all_annotations(type(self))

                        if any(isinstance(v, str) for v in all_ann.values()):
                            resolve_annotations(type(self))
                            all_ann = all_annotations(type(self))
                        else:
                            pass

                        if name in all_ann:
                            ann: typing.Any = all_ann[name]
                            if typing.get_origin(ann) not in CLASSVAR_ORIGINS:
                                ok, msg = type_match(value, ann)
                                if not ok:
                                    raise TypeError(
                                        f"Cannot assign attribute '{name}' = {value!r} on instance of class {get_name(type(self))}: expected type {ann!r}, failure reason: {msg}"
                                    )
                                else:
                                    pass
                            else:
                                pass
                        else:
                            if strict and (not name.startswith("_")):
                                raise AttributeError(
                                    f"Attribute '{name}' on instance of class {get_name(type(self))} is unannotated and strict mode is active. Annotate the attribute or prefix with '_' for private attributes."
                                )
                            else:
                                pass

                        if name in effective_validators:
                            vmsg: typing.Optional[str] = _run_validator(effective_validators[name], value)
                            if vmsg:
                                raise TypeError(
                                    f"Validator validation failed for attribute '{name}' on instance of class {get_name(type(self))} with value {value!r}: {vmsg}"
                                )
                            else:
                                pass
                        else:
                            pass

                        initial_setter(self, name, value)

                        if callback is not None:
                            cb_msg: typing.Optional[str] = callback(self, name, value)
                            if cb_msg:
                                raise TypeError(
                                    f"Callback hook validation failed for attribute '{name}' on instance of class {get_name(type(self))}: {cb_msg}"
                                )
                            else:
                                pass
                        else:
                            pass

                    setattr(cls, "__setattr__", new_setter)
                    setattr(cls, "__pyod_annotate__", True)
                    return cls


def annotate_module(
    mod: typing.Optional[types.ModuleType] = None,
    *,
    recur: bool = True,
    strict_classes: bool = True,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = None,
) -> types.ModuleType:
    """Annotate all public functions and classes defined in the given module."""
    if mod is None:
        frame: inspect.FrameInfo = inspect.stack()[1]
        caller_mod_name: str = frame[0].f_globals.get("__name__", "__main__")
        target_mod: typing.Optional[types.ModuleType] = sys.modules.get(caller_mod_name)
        if target_mod is None:
            raise RuntimeError(f"annotate_module could not locate caller module '{caller_mod_name}'.")
        else:
            mod = target_mod
    else:
        pass

    if not isinstance(mod, types.ModuleType):
        raise TypeError(f"annotate_module expected a ModuleType instance, got {mod!r}.")
    else:
        mod_name: str = mod.__name__

        for name, obj in list(vars(mod).items()):
            if name.startswith("_"):
                continue
            else:
                if getattr(obj, "__module__", None) != mod_name:
                    continue
                else:
                    try:
                        if inspect.isfunction(obj):
                            setattr(mod, name, annotate_function(obj, callback=callback))
                        elif inspect.isclass(obj):
                            setattr(mod, name, annotate_class(obj, recur=recur, strict=strict_classes, callback=callback))
                        else:
                            pass
                    except Exception as exc:
                        warnings.warn(
                            f"annotate_module failed to annotate member '{name}' in module '{mod_name}': {exc}",
                            stacklevel=2,
                        )

        return mod


def pyoload(
    obj: typing.Any = None,
    *,
    recur: bool = True,
    strict: bool = True,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = None,
    validators: dict[str, typing.Any] = {},
    max_iter: typing.Optional[int] = None,
    **kwargs: typing.Any,
) -> typing.Any:
    """Unified dispatcher for pyoload annotations across functions, classes, and modules."""
    effective_validators: dict[str, typing.Any] = dict(validators)
    effective_validators.update(kwargs)

    if obj is None:
        return functools.partial(
            pyoload,
            recur=recur,
            strict=strict,
            callback=callback,
            validators=effective_validators,
            max_iter=max_iter,
        )
    else:
        if not ENABLED:
            return obj
        else:
            if inspect.isclass(obj):
                return annotate_class(obj, recur=recur, strict=strict, callback=callback, validators=effective_validators)
            elif inspect.isfunction(obj) or inspect.ismethod(obj):
                return annotate_function(obj, callback=callback, max_iter=max_iter, validators=effective_validators)
            elif isinstance(obj, types.ModuleType):
                return annotate_module(obj, recur=recur, strict_classes=strict, callback=callback)
            else:
                warnings.warn(
                    f"pyoload received unsupported object type {type(obj)!r} for object {obj!r}; returning object unchanged.",
                    stacklevel=2,
                )
                return obj


def gt(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator ensuring val > n."""
    def _v(val: typing.Any) -> typing.Optional[str]:
        if val > n:
            return None
        else:
            return f"expected value > {n!r}, got {val!r}"
    return _v


def lt(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator ensuring val < n."""
    def _v(val: typing.Any) -> typing.Optional[str]:
        if val < n:
            return None
        else:
            return f"expected value < {n!r}, got {val!r}"
    return _v


def ge(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator ensuring val >= n."""
    def _v(val: typing.Any) -> typing.Optional[str]:
        if val >= n:
            return None
        else:
            return f"expected value >= {n!r}, got {val!r}"
    return _v


def le(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator ensuring val <= n."""
    def _v(val: typing.Any) -> typing.Optional[str]:
        if val <= n:
            return None
        else:
            return f"expected value <= {n!r}, got {val!r}"
    return _v


def non_empty(val: typing.Any) -> typing.Optional[str]:
    """Validator ensuring len(val) > 0 or truthy."""
    try:
        if len(val) > 0:
            return None
        else:
            return "value must not be empty"
    except TypeError:
        if val:
            return None
        else:
            return "value must not be empty"


def positive(val: typing.Any) -> typing.Optional[str]:
    """Validator ensuring val > 0."""
    if val > 0:
        return None
    else:
        return f"expected positive value, got {val!r}"


def negative(val: typing.Any) -> typing.Optional[str]:
    """Validator ensuring val < 0."""
    if val < 0:
        return None
    else:
        return f"expected negative value, got {val!r}"


def non_zero(val: typing.Any) -> typing.Optional[str]:
    """Validator ensuring val != 0."""
    if val != 0:
        return None
    else:
        return "value must not be zero"


def finite(val: typing.Any) -> typing.Optional[str]:
    """Validator ensuring float val is finite (not NaN, not Inf)."""
    import math
    try:
        if math.isfinite(val):
            return None
        else:
            return f"expected finite float value, got {val!r}"
    except TypeError:
        return f"value {val!r} of type {type(val).__name__} is not a number"


def regex(pattern: str, flags: int = 0) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator matching string val against regex pattern."""
    compiled: _re.Pattern = _re.compile(pattern, flags)
    def _v(val: typing.Any) -> typing.Optional[str]:
        if isinstance(val, str) and compiled.fullmatch(val):
            return None
        else:
            return f"value {val!r} does not match regex pattern {pattern!r}"
    return _v


def predicate(
    fn: typing.Callable[[typing.Any], bool],
    message: str = "predicate condition failed",
) -> typing.Callable[[typing.Any], typing.Optional[str]]:
    """Return a validator executing boolean predicate fn(val)."""
    def _v(val: typing.Any) -> typing.Optional[str]:
        if fn(val):
            return None
        else:
            return message
    return _v


class PyoloadModule(types.ModuleType):
    """Callable module object for pyoload."""

    def __init__(self) -> None:
        super().__init__(__name__)
        object.__setattr__(self, "_real_module", sys.modules[__name__])
        sys.modules[__name__] = self
        init()

    def __getattr__(self, attr: str) -> typing.Any:
        return getattr(object.__getattribute__(self, "_real_module"), attr)

    def __setattr__(self, attr: str, val: typing.Any) -> None:
        if attr.startswith("_"):
            object.__setattr__(self, attr, val)
        else:
            setattr(object.__getattribute__(self, "_real_module"), attr, val)

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        return pyoload(*args, **kwargs)

    def __repr__(self) -> str:
        return f"<module 'pyoload' v{__version__} (callable)>"


PyoloadModule()
