"""
Type stubs for pyoload 4.0.
"""

import types
import typing

__version__: str
ENABLED: bool

MUTABLE_DEFAULT_TYPES: set[type]
CLASSVAR_ORIGINS: set[typing.Any]
MAPPING_ORIGINS: set[typing.Any]
SEQUENCE_ORIGINS: set[typing.Any]

class override_state:
    target_state: bool
    previous_state: bool
    def __init__(self, target_state: bool) -> None: ...
    def __enter__(self) -> override_state: ...
    def __exit__(
        self,
        exc_type: typing.Optional[type],
        exc_val: typing.Optional[BaseException],
        exc_tb: typing.Optional[types.TracebackType],
    ) -> None: ...

def disabled() -> override_state: ...
def enabled() -> override_state: ...

def enable() -> None: ...
def disable() -> None: ...
def is_enabled() -> bool: ...
def init() -> None: ...

def get_name(obj: typing.Any) -> str: ...
def is_annotated(func: typing.Callable[..., typing.Any]) -> bool: ...
def all_annotations(klass: type) -> dict[str, typing.Any]: ...
def is_typeddict(tp: typing.Any) -> bool: ...
def is_protocol(tp: typing.Any) -> bool: ...
def protocol_members(proto: type) -> frozenset[str]: ...
def resolve_annotations(obj: typing.Any) -> None: ...

def type_match(
    val: typing.Any,
    spec: typing.Any,
    max_iter: typing.Optional[int] = ...,
) -> tuple[bool, typing.Optional[str]]: ...

def is_valid(
    val: typing.Any,
    spec: typing.Any,
    max_iter: typing.Optional[int] = ...,
) -> bool: ...

_F = typing.TypeVar("_F", bound=typing.Callable[..., typing.Any])
_C = typing.TypeVar("_C", bound=type)
_V = dict[str, typing.Any]

@typing.overload
def annotate_function(obj: _F) -> _F: ...
@typing.overload
def annotate_function(
    obj: None = ...,
    *,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = ...,
    max_iter: typing.Optional[int] = ...,
    validators: _V = ...,
    **kwargs: typing.Any,
) -> typing.Callable[[_F], _F]: ...

@typing.overload
def annotate_class(cls: _C) -> _C: ...
@typing.overload
def annotate_class(
    cls: None = ...,
    recur: bool = ...,
    strict: bool = ...,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = ...,
    validators: dict[str, typing.Any] = ...,
    **kwargs: typing.Any,
) -> typing.Callable[[_C], _C]: ...

def annotate_module(
    mod: typing.Optional[types.ModuleType] = ...,
    *,
    recur: bool = ...,
    strict_classes: bool = ...,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = ...,
) -> types.ModuleType: ...

@typing.overload
def pyoload(obj: _F) -> _F: ...
@typing.overload
def pyoload(obj: _C) -> _C: ...
@typing.overload
def pyoload(
    obj: None = ...,
    *,
    recur: bool = ...,
    strict: bool = ...,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = ...,
    validators: dict[str, typing.Any] = ...,
    max_iter: typing.Optional[int] = ...,
    **kwargs: typing.Any,
) -> typing.Callable[[typing.Any], typing.Any]: ...

def gt(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...
def lt(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...
def ge(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...
def le(n: typing.Any) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...
def non_empty(val: typing.Any) -> typing.Optional[str]: ...
def positive(val: typing.Any) -> typing.Optional[str]: ...
def negative(val: typing.Any) -> typing.Optional[str]: ...
def non_zero(val: typing.Any) -> typing.Optional[str]: ...
def finite(val: typing.Any) -> typing.Optional[str]: ...
def regex(pattern: str, flags: int = ...) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...
def predicate(
    fn: typing.Callable[[typing.Any], bool],
    message: str = ...,
) -> typing.Callable[[typing.Any], typing.Optional[str]]: ...

@typing.overload
def __call__(obj: _F) -> _F: ...
@typing.overload
def __call__(obj: _C) -> _C: ...
@typing.overload
def __call__(
    obj: None = ...,
    *,
    recur: bool = ...,
    strict: bool = ...,
    callback: typing.Optional[typing.Callable[..., typing.Optional[str]]] = ...,
    validators: dict[str, typing.Any] = ...,
    max_iter: typing.Optional[int] = ...,
    **kwargs: typing.Any,
) -> typing.Callable[[typing.Any], typing.Any]: ...
