"""
Pyload to help you debug your modules by adding some runtime type checking.

Built to support builting python types and those from :py:`typing` module.
"""


import collections.abc
import enum
import functools
import inspect
import os
import sys
import types
import typing
import warnings


class Mode(enum.Enum):
    DEBUG = enum.auto()
    DEV = enum.auto()
    PROD = enum.auto()


MODE = Mode.PROD


def dev():
    global MODE
    MODE = Mode.DEV


def debug():
    global MODE
    MODE = Mode.DEBUG


def prod():
    global MODE
    MODE = Mode.PROD


def init():
    if (mode := os.getenv("PYOLOAD_MODE")) is not None:
        if mode.lower() == "prod":
            prod()
        elif mode.lower() == "debug":
            debug()
        elif mode.lower() == "dev":
            dev()
        else:
            raise ValueError(
                f"Wrong value for env var 'PYOLOAD_MODE', {mode!r}"
            )


def get_name(funcOrCls: typing.Any) -> str:
    """
    Get a class or function name.

    Possibly unique gotten from
    it's module name and qualifier name.
    >>> def foo():
    ...     pass
    ...
    >>> get_name(foo)
    '__main__.foo'
    >>> get_name(get_name)
    'pyoload.get_name'
    >>> get_name(print)
    'builtins.print'
    """
    mod = funcOrCls.__module__
    try:
        name = funcOrCls.__qualname__
    except AttributeError:
        name = type(funcOrCls).__qualname__
    return mod + "." + name


def type_match(
    val: typing.Any,
    spec: typing.Type,
    max_iter=None,
) -> tuple[bool, typing.Optional[str]]:
    """
    Recursively checks if :py:`val` matches type :py:`spec`.

    :param val: The value to typecheck
    :param spec: The type specifier

    :returns: A tuple of the match status and the optional comment.
    """
    if isinstance(val, bool) and spec is int:
        return (False, None)
    try:
        return (isinstance(val, spec), None)
    except TypeError:
        pass

    if spec is typing.Any:
        return (True, None)

    if typing.get_origin(spec) in (typing.Union, types.UnionType):
        message = None
        for sub_type in typing.get_args(spec):
            matches, message = type_match(val, sub_type)
            if matches:
                return True, message
        else:
            return (False, message)
    elif isinstance(spec, types.GenericAlias):
        orig = typing.get_origin(spec)
        if not isinstance(val, orig):
            return (False, "Value does not match base type")

        if orig in (dict, collections.abc.Mapping):
            args = typing.get_args(spec)
            if len(args) == 2:
                key_type, keyvalue_type = args
            elif len(args) == 1:
                key_type, keyvalue_type = args[0], typing.Any
            n = 0
            for key, keyvalue in val.items():
                key_matched, message = type_match(key, key_type)
                if not key_matched:
                    return (
                        False,
                        f"Key {key!r} did not match key type in {spec!r}"
                        + f"({message!r}).",
                    )
                value_matched, message = type_match(keyvalue, keyvalue_type)
                if not value_matched:
                    return (
                        False,
                        f"Key value {keyvalue!r} did not match key type in"
                        + f" {spec!r}({message!r}).",
                    )
                n += 1
                if max_iter is not None and n >= max_iter:
                    return (True, None)
            else:
                return (True, None)
        elif orig is tuple and len(type_args := typing.get_args(spec)) > 1:
            if not isinstance(val, tuple):
                return (
                    False,
                    f"Value {val!r} is not a tuple so cannot be {spec!r}",
                )
            if len(type_args) != len(val):
                return (
                    False,
                    f"Value cannot be a {spec!r}, unmatching value number."
                    + f"(Note e.g tuple[int, str] is considered as:"
                    + " (1, 'r'), (78, 'wel'), ...)",
                )
            for idx, (sub_value, sub_type) in enumerate(zip(val, type_args)):
                matches, message = type_match(sub_value, sub_type)
                if not matches:
                    return (
                        False,
                        f"Sub tuple item ({sub_value!r}) did not respective"
                        + f" tuple type(#{message})",
                    )
            else:
                return (True, None)
        elif orig in (
            list,
            tuple,
            collections.abc.Iterable,
        ):  # it was an Iterable
            sub = typing.get_args(spec)[0]
            for idx, item in enumerate(val):
                matches, message = type_match(item, sub)
                if not matches:
                    return (
                        False,
                        f"Iterable item {idx} did not match spec in {spec!r}"
                        + f"(#{message})",
                    )
            else:
                return (True, None)
        else:
            raise NotImplementedError(
                f"pyoload does not implement type: {spec}"
            )
    if spec is any:
        raise TypeError(
            "`any` is not a type!, May be have you confused `Any` and `any`"
        )
    raise NotImplementedError(f"pyoload does not implement type: {spec}")


def resove_annotations(obj: typing.Callable):
    """Evaluate all the stringized annotations of the argument."""
    if not hasattr(obj, "__annotations__"):
        raise TypeError(
            f"object {obj=!r} does not have `.__annotations__`",
        )
    if None in obj.__annotations__.values():
        for k, v in obj.__annotations__.items():
            if v is None:
                obj.__annotations__[k] = types.NoneType
    if inspect.isfunction(obj):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(
                        v, obj.__globals__, dict(vars(inspect.getmodule(obj)))
                    )
                except Exception as e:
                    raise Exception(
                        f"Annotation of attribute `{k}`of {get_name(obj)}"
                        + " could not be resolved.",
                        e,
                    ) from e
    elif inspect.isclass(obj) or hasattr(obj, "__class__"):
        if not inspect.isclass(obj):
            objclass = type(obj)
        else:
            objclass = obj
        namespace = dict(vars(objclass))
        bases = set(objclass.__bases__)
        bases.add(objclass)
        while len(bases) > 0:
            base = bases.pop()
            namespace.update(vars(inspect.getmodule(base)))
            if hasattr(base, "bases"):
                bases.update(set(base.bases))
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(v, namespace)
                except Exception as e:
                    raise Exception(
                        f"Annotation of attribute `{k}` of {get_name(obj)}"
                        + " could not be resolved.",
                        e,
                    ) from e
    else:
        raise ValueError(f"Cannot resolve annotations of {obj!r}")


def is_annoted(func: typing.Callable) -> bool:
    """Determine if a function has been annotated."""
    return hasattr(func, "__pyod_annotate__")


WARNED_ABOUT_NO_RETURN_TYPE = set()


def annotate(
    obj: typing.Optional[typing.Callable] = None,
    *,
    max_iter: typing.Optional[int] = None,
    validators: dict[
        str, typing.Callable[[typing.Any], typing.Optional[str]]
    ] = {},
) -> typing.Callable:
    """
    Wrap over and typechecks arguments on each call.

    :param obj: the object to annotate
    :param max_iter: max iterations to perform in case of iterables.
    :param comments: A mapping from parameter names to optional explicative
    comments about annotation.
    """
    if not callable(obj) or not hasattr(obj, "__annotations__"):
        warnings.warn(f"Annotate was passed {obj!r} named {get_name(obj)}.")
        return obj
    if is_annoted(obj):
        return obj
    if MODE is MODE.DEBUG and inspect.isclass(obj):
        warnings.warn(
            f"Class {obj!r}({get_name(obj)}) may have been passed to"
            + " pyoload.annotate instead of annotate_class."
        )
        return annotate_class(obj, recur=recur)
    try:
        resove_annotations(obj)
    except Exception:
        pass
    finally:
        signature = inspect.signature(obj)
    for param in signature.parameters.values():
        if param.default is inspect._empty:
            continue
        matches, msg = type_match(param.default, param.annotation)
        if not matches:
            warnings.warn(
                f"Default value for parameter {param.name} of function"
                f" {get_name(obj)} does not match it's annotation, {msg}"
            )
            if MODE is Mode.DEBUG and param.name in validators:
                msg = validators[param.name](param.default)
                if msg:
                    warnings.warn(
                        f"Default value for parameter {param.name} of function"
                        f" {get_name(obj)} failed validation, {msg}"
                    )

    @functools.wraps(obj)
    def wrapper(*call_posargs, **call_kwargs):
        nonlocal signature, obj
        if str in map(type, obj.__annotations__.values()):
            resove_annotations(obj)
            signature = inspect.signature(obj)
        try:
            args = signature.bind(*call_posargs, **call_kwargs)
        except TypeError as e:  # inspect got argument error
            try:
                obj(*call_posargs, **call_kwargs)
            except Exception as se:
                raise se from e
            else:
                raise TypeError(
                    f"Exception while binding args to" + f"{get_name(obj)}",
                    e,
                ) from e
        for parameter, argument in args.arguments.items():
            param = signature.parameters.get(parameter)
            if param.annotation is inspect._empty:
                continue
            matches, message = type_match(argument, param.annotation)
            if not matches:
                raise TypeError(
                    f"Argument: {argument!r} does not match annotation for"
                    + f" parameter {parameter!r}:{param.annotation!r}"
                    + f" of function {get_name(obj)} (#{message})"
                )
            if MODE is Mode.DEBUG and parameter in validators:
                msg = validators[parameter](argument)
                if msg:
                    raise ValueError(
                        f"Argument for parameter {parameter} of function"
                        f" {get_name(obj)} failed validation, {msg}"
                    )

        ret = obj(*call_posargs, **call_kwargs)

        if signature.return_annotation is not inspect._empty:
            matches, message = type_match(ret, signature.return_annotation)
            if not matches:
                raise ValueError(
                    f"return value: {ret!r} does not match return type:"
                    + f" {signature.return_annotation!r}"
                    + f" of function {get_name(obj)} (#{message})",
                )
            if MODE is Mode.DEBUG and "return" in validators:
                msg = validators["return"](ret)
                if msg:
                    raise ValueError(
                        f"Return value of function"
                        f" {get_name(obj)} failed validation, {msg}"
                    )
        elif (
            ret is not None
            and get_name(obj) not in WARNED_ABOUT_NO_RETURN_TYPE
        ):
            warnings.warn(
                f"Function {get_name(obj)}"
                + " returned a value but had no return annotation."
            )
            WARNED_ABOUT_NO_RETURN_TYPE.add(get_name(obj))
        return ret

    return wrapper


def annotate_class(
    cls: typing.Any,
    recur: bool = True,
    validators: dict[str, typing.Callable] = {},
):
    """
    Annotate a class object, wrapping and replacing over it's __setattr__.

    Typechecking over each attribute assignment.
    If no annotation for the passed object found it ignores it till it is
    found
    it annotates the classes methods except `__pyod_norecur__`
    attribute is defines
    """
    try:
        resove_annotations(cls)
    except Exception:
        pass
    if isinstance(cls, bool):
        return functools.partial(annotate_class, recur=cls)
    recur = not hasattr(cls, "__pyod_norecur__") and recur
    initial_setter = cls.__setattr__
    if recur:
        for x in vars(cls):
            if x[1] == "_" and x != "__init__":
                continue
            if hasattr(getattr(cls, x), "__annotations__"):
                setattr(
                    cls,
                    x,
                    annotate(vars(cls).get(x)),
                )

    @functools.wraps(cls.__setattr__)
    def new_setter(self, name, value):
        if str in map(type, self.__annotations__.values()):
            resove_annotations(self)
        if name in self.__annotations__:
            matches, message = type_match(value, self.__annotations__[name])
            if not matches:
                raise TypeError(
                    f"value {value!r} does not match type spec"
                    f"of attribute: {name!r}:{self.__annotations__[name]!r}"
                    f" of object of class {get_name(cls)}  (#{message})"
                )
        if MODE is Mode.DEBUG and name in validators:
            msg = validators[name](value)
            if msg:
                raise TypeError(
                    f"Value assigned to attribute {name} of object of type"
                    f" {get_name(type(obj))} failed validation, {msg}"
                )
        return initial_setter(self, name, value)

    cls.__setattr__ = new_setter
    return cls


def pyoload(
    obj: typing.Any = None,
    recur: bool = True,
    validators: dict[str, typing.Callable] = {},
) -> typing.Any:
    """
    Check between pyoload methods and uses the appropriate one.

    :param object: The object to annotate.
    :param recur: Should annotate further methods in case of a class.
    :param validators: Better validates arguments.
    """
    if obj is None:
        return functools.partial(pyoload, recur=recur, validators=validators)
    if MODE == Mode.PROD:
        return obj
    if inspect.isclass(obj):
        return annotate_class(obj, recur=recur, validators=validators)
    else:
        return annotate(obj, validators=validators)


class PyoloadModule(types.ModuleType):
    def __init__(self):
        super().__init__(__name__)
        PyoloadModule.module = sys.modules[__name__]
        sys.modules[__name__] = self
        init()

    def __getattr__(self, attr):
        return getattr(PyoloadModule.module, attr)

    def __setattr__(self, attr, val):
        return setattr(PyoloadModule.module, attr, val)

    __call__ = staticmethod(pyoload)


PyoloadModule()
