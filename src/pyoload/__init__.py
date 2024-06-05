"""
pyoload is a little python script to incorporate some features of
 typechecking and casting in python.
"""

from functools import partial
from functools import wraps
from inspect import _empty
from inspect import isclass
from inspect import signature
from types import NoneType
from types import UnionType
from typing import Any
from typing import Callable
from typing import GenericAlias
from typing import Type

import sys


class AnnotationError(ValueError):
    """
    base exception for most pyoload errors
    """


class AnnotationErrors(AnnotationError):
    """
    Hosts a list of AnnotationError
    """


class InternalAnnotationError(Exception):
    """
    **internal**
    raised by overloads on type mismatch
    """


class CastingError(TypeError):
    """
    Error during casting
    """


class OverloadError(TypeError):
    """
    Error in or during overload
    """


class AnnotationResolutionError(AnnotationError):
    """
    Annotations could not be resolved or evaluated.
    """

    _raise = False


class PyoloadAnnotation:
    """
    A parent class for pyoload extra annotations as `Cast` and `Values`
    """


class Values(PyoloadAnnotation, tuple):
    """
    A tuple subclass which holds several values as possible annotations
    """

    def __call__(self: "Values", val: Any) -> bool:
        """
        Checks if the tuple containes the specified value.

        :param val: the value to be checked

        :returns: if the value `val` is contained in `self`
        """
        return val in self

    def __str__(self):
        return "Values(" + ", ".join(map(repr, self)) + ")"

    __repr__ = __str__


def get_name(funcOrCls: Any) -> str:
    """
    Gives a class or function name, possibly unique gotten from
    it's module name and qualifier name

    :param funcOrCls: The object who's name to return

    :returns: modulename + qualname
    """
    return funcOrCls.__module__ + "." + funcOrCls.__qualname__


class Check:
    """
    A class basicly abstract which holds registerred checks in pyoload
    """

    checks_list = {}

    def __init_subclass__(cls: Any):
        """
        register's subclasses as chexks
        """
        if hasattr(cls, "name"):
            name = cls.name
        else:
            name = cls.__name__
        Check.register(name)(cls())

    @classmethod
    def register(
        cls: Any,
        name: str,
    ) -> Callable[[Callable[[Any, Any], NoneType]], Callable]:
        """
        returns a callable which registers a new checker method

        :param cls: the Check class
        :param name: the name to be registerred as.

        :returns: a function which registers the check under the name
        """
        names = [x for x in name.split(" ") if x.strip() != ""]
        for name in names:
            if name in cls.checks_list:
                raise Check.CheckNameAlreadyExistsError(name)

        def inner(func: Callable[Any, Any]) -> Callable:
            for name in names:
                cls.checks_list[name] = func
            return func

        return inner

    @classmethod
    def check(cls: Any, name: str, params: Any, val: Any) -> None:
        """
        Performs the specified check with the specified params on
        the specified value

        :param cls: pyoload.Check class
        :param name: The registerred name of the check
        :param params: The parameters to pass to the check
        :param val: The value to check

        :returns: `None`
        """
        check = cls.checks_list.get(name)
        if check is None:
            raise Check.CheckDoesNotExistError(name)
        check(params, val)

    class CheckNameAlreadyExistsError(ValueError):
        """
        The check name to be registerred already exists
        """

    class CheckDoesNotExistError(ValueError):
        """
        The specified check does not exist
        """

    class CheckError(Exception):
        """
        Error occurring during check call.
        """


@Check.register("len")
def len_check(params, val):
    if isinstance(params, int):
        if not len(val) == params:
            raise Check.CheckError(f"length of {val!r} not eq {params!r}")
    elif isinstance(params, tuple) and len(params) > 0:
        mi = ma = None
        mi, ma = params
        if mi is not None:
            if not len(val) > mi:
                raise Check.CheckError(f"length of {val!r} not gt {mi!r}")
        if ma is not None:
            if not len(val) < ma:
                raise Check.CheckError(f"length of {val!r} not lt {mi!r}")


@Check.register("lt")
def lt_check(param, val):
    if not val < param:
        raise Check.CheckError(f"{val!r} not lt {param!r}")


@Check.register("le")
def le_check(param, val):
    if not val <= param:
        raise Check.CheckError(f"{val!r} not gt {param!r}")


@Check.register("ge")
def ge_check(param, val):
    if not val >= param:
        raise Check.CheckError(f"{val!r} not ge {param!r}")


@Check.register("gt")
def gt_check(param, val):
    if not val > param:
        raise Check.CheckError(f"{val!r} not gt {param!r}")


@Check.register("eq")
def eq_check(param, val):
    if not val == param:
        raise Check.CheckError(f"{val!r} not eq {param!r}")


@Check.register("func")
def func_check(param, val):
    if not param(val):
        raise Check.CheckError(f"{param!r} call returned false on {val!r}")


@Check.register("type")
def matches_check(param, val):
    if not typeMatch(val, param):
        raise Check.CheckError(f"{val!r} foes not match type {param!r}")


@Check.register("isinstance")
def instance_check(param, val):
    if not isinstance(val, param):
        raise Check.CheckError(f"{val!r} not instance of {param!r}")


class Checks(PyoloadAnnotation):
    """
    Pyoload annotation holding several checks called on typechecking.
    """

    def __init__(
        self: PyoloadAnnotation,
        **checks: dict[str, Callable[[Any, Any], NoneType]],
    ) -> Any:
        """
        crates the check object,e.g

        >>> class foo:
        ...    bar: pyoload.Checks(gt=4)

        :param checks: the checks to be done.

        :returns: self
        """
        self.checks = checks

    def __call__(self: PyoloadAnnotation, val: Any) -> None:
        """
        Performs the several checks contained in `self.checks`

        :param val: The value to check
        """
        for name, params in self.checks.items():
            Check.check(name, params, val)

    def __str__(self: Any) -> str:
        ret = "<Checks("
        for k, v in self.checks.items():
            ret += f"{k}={v!r}, "
        ret = ret[:-2] + ")>"
        return ret

    __repr__ = __str__


class CheckedAttr(Checks):
    """
    A descriptor class providing attributes which are checked on assignment
    """

    name: str
    value: Any

    def __init__(
        self: Any,
        **checks: dict[str, Callable[[Any, Any], NoneType]],
    ) -> Any:
        """
        Creates a Checked Attribute descriptor whick does checking on each
        assignment, E.G

        >>> class foo:
        ...     bar = CheckedAttr(gt=4)

        :param checks: The checks to perform
        """
        super().__init__(**checks)

    def __set_name__(self: Any, obj: Any, name: str, typo: Any = None):
        """
        sets the name of the attribute
        """
        self.name = name
        self.value = None

    def __get__(self: Any, obj: Any, type: Any):
        """
        returns the value in `self.value`
        """
        return self.value

    def __set__(self: Any, obj: Any, value: Any):
        """
        Performs checks then assigns the new value
        """
        self(value)
        self.value = value


class Cast(PyoloadAnnotation):
    """
    Holds a cast object which describes the casts to be performed
    """

    @staticmethod
    def cast(val: Any, totype: Any) -> Any:
        """
        The gratest deal.
        Recursively casts the given value to the specified structure or type
        e.g

        >>> Cast.cast({ 1: 2}, dict[str, float])
        {'1': 2.0}

        :param val: the value to cast
        :param totype: The type structure to be casted to.

        :returns: An instance of the casting type
        """
        if isinstance(totype, GenericAlias):
            if totype.__origin__ == dict:
                if len(totype.__args__) == 2:
                    kt, vt = totype.__args__
                elif len(totype.__args__) == 1:
                    kt, vt = Any, totype.__args__[1]
                return {Cast.cast(k, kt): Cast.cast(v, vt) for k, v in val.items()}
            else:
                sub = totype.__args__[0]
                return totype.__origin__([Cast.cast(v, sub) for v in val])
        if isinstance(totype, UnionType):
            errors = []
            for subtype in totype.__args__:
                try:
                    return Cast.cast(val, subtype)
                except Exception as e:
                    errors.append(e)
            else:
                raise errors
        else:
            return totype(val) if not isinstance(val, totype) else val

    def __init__(self: PyoloadAnnotation, type: Any):
        """
        creates a casting object for the specified type
        The object can then be used anywhere for casting, e.g

        >>> caster = Cast(dict[str, list[tuple[float]]])
        >>> raw = {
        ...     4: (
        ...         ['1.5', 10],
        ...         [10, '1.5'],
        ...     )
        ... }
        >>> caster(raw)
        {'4': [(1.5, 10.0), (10.0, 1.5)]}

        :param type: The type to which the object will cast

        :returns: self
        """
        self.type = type

    def __call__(self: PyoloadAnnotation, val: Any):
        """
        Calls to the type specified in the object `.type` attribute

        :param val: the value to be casted

        :return: The casted value
        """
        try:
            return Cast.cast(val, self.type)
        except Exception as e:
            raise CastingError(
                f"Exception({e}) while casting: {val!r} to {self.type}",
            ) from e

    def __str__(self):
        return f"pyoload.Cast({self.type!s})"


class CastedAttr(Cast):
    """
    A descriptor class providing attributes which are casted on assignment
    """

    name: str
    value: Any

    def __init__(self: Cast, type: Any) -> Cast:
        """
        >>> class Person:
        ...     age = CheckedAttr(gt=0)
        ...     phone = CastedAttr(tuple[int])
        ...     def __init__(self, age, phone):
        ...         self.age = age
        ...         self.phone = phone
        ...
        >>> temeze = Person(17, "678936798")
        >>>
        >>> print(temeze.age)
        17
        >>> print(temeze.phone)
        (6, 7, 8, 9, 3, 6, 7, 9, 8)
        >>>
        >>> mballa = Person(0, "123456")
        Traceback (most recent call last):
          ...
        pyoload.Check.CheckError: 0 not gt 0
        """
        super().__init__(type)

    def __set_name__(self: Any, obj: Any, name: str, typo: Any = None):
        """def __set_name__(self: Any, obj: Any, name: str, typo: Any = None)
        setd the name of the attribute
        """
        self.name = name
        self.value = None

    def __get__(self: Any, obj: Any, type: Any):
        """def __get__(self: Any, obj: Any, type: Any)
        returns the value in `self.value`
        """
        return self.value

    def __set__(self: Any, obj: Any, value: Any):
        """def __set__(self: Any, obj: Any, value: Any)
        Performs checks then assigns the new value
        """
        self.value = self(value)


def typeMatch(val: Any, spec: Any) -> bool:
    """
    recursively checks if type matches

    :param val: The value to typecheck
    :param spec: The type specifier

    :return: A boolean
    """
    if spec == any:
        raise TypeError("May be have you confused `Any` and `any`")

    if spec == Any or spec is None or val is None:
        return True
    if isinstance(spec, Values):
        return spec(val)
    elif isinstance(spec, Checks):
        try:
            spec(val)
        except Check.CheckError:
            return False
        else:
            return True
    elif isinstance(spec, GenericAlias):
        if not isinstance(val, spec.__origin__):
            return False

        if spec.__origin__ == dict:
            if len(spec.__args__) == 2:
                kt, vt = spec.__args__
            elif len(spec.__args__) == 1:
                kt, vt = Any, spec.__args__[1]
            else:
                return True

            for k, v in val.items():
                if not typeMatch(k, kt) or not typeMatch(v, vt):
                    return False
            else:
                return True
        else:
            sub = spec.__args__[0]
            for val in val:
                if not typeMatch(val, sub):
                    return False
            else:
                return True
    else:
        return isinstance(val, spec)


def get_module(obj: Any):
    """
    gets the module to which an object, function or class belongs
    e.g

    >>> class foo:
    ...     def bar(self):
    ...         pass
    ...
    >>> get_name(foo)
    '__main__.foo'
    >>> get_name(foo.bar)
    '__main__.foo.bar'

    :param obj: the object

    :returns: the module
    """
    return sys.modules[obj.__module__]


def resolveAnnotations(obj: Type | Callable) -> None:
    """
    Evaluates all the stringized annotations of the argument

    :param obj: The object of which to evaluate annotations

    :returns: None
    """
    if isclass(obj) or hasattr(obj, "__class__"):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(
                        v,
                        dict(vars(get_module(obj))),
                        dict(vars(obj)),
                    )
                except Exception as e:
                    raise AnnotationResolutionError(
                        (
                            f"Exception: {e!s} while resolving"
                            f" annotation {e}={v!r} of object {obj!r}"
                        ),
                    ) from e
    elif callable(obj):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(v, obj.__globals__)
                except Exception as e:
                    raise AnnotationResolutionError(
                        f"Exception: {k!s} while resolving"
                        f" annotation {v!r} of function {obj!r}",
                        f"globals: {obj.__globals__}",
                    ) from e
    else:
        raise AnnotationError(f"unknown resolution method for {obj}")


def annotate(
    func: Callable,
    *,
    force: bool = False,
    oload: bool = False,
) -> Callable:
    """
    returns a wrapper over the passed function
    which typechecks arguments on each call.

    :param func: the function to annotate
    :param force: annotate force even on unannotatables
    :param oload: internal, if set to True, will raise \
    `InternalAnnotationError` on type mismatch

    :returns: the wrapper function
    """
    if isclass(func):
        return annotateClass(func)
    if len(func.__annotations__) == 0:
        return func

    @wraps(func)
    def wrapper(*pargs, **kw):
        if str in map(type, func.__annotations__.values()):
            resolveAnnotations(func)
        try:
            sign = signature(func)
        except Exception:
            if oload:
                raise InternalAnnotationError()
            else:
                raise
        args = sign.bind(*pargs, **kw)
        errors = []
        for k, v in args.arguments.items():
            param = sign.parameters.get(k)
            if param.annotation is None:
                continue
            if isinstance(param.annotation, Cast):
                args.arguments["k"] = param.annotation(v)
                continue
            try:
                isinstance(v, param.annotation)
            except TypeError:
                if not typeMatch(v, param.annotation):
                    if oload:
                        raise InternalAnnotationError()
                    errors.append(
                        AnnotationError(
                            f"Value: {v!r} does not match annotation:"
                            f" {param.annotation!r} for "
                            f"argument {k!r} of function {get_name(func)}",
                        ),
                    )
            else:
                continue
        if len(errors) > 0:
            raise AnnotationErrors(errors)

        ret = func(*pargs, **kw)
        if "return" in func.__annotations__:
            ann = sign.return_annotation
            if ann is _empty:
                return ret
            if isinstance(ann, Cast):
                return ann(ret)
            try:
                isinstance(ret, ann)
            except TypeError:
                if not typeMatch(ret, ann):
                    errors.append(
                        AnnotationError(
                            f"return value: {ret!r} does not match annotation:"
                            f" {ann!r} for "
                            f"of function {get_name(func)}",
                        ),
                    )
        return ret

    wrapper.__pyod_annotate__ = func
    return wrapper


__overloads__: dict[str, list[Callable]] = {}


def overload(func: Callable, name: str | None = None) -> Callable:
    """
    returns a wrapper over the passed function
    which typechecks arguments on each call
    and finds the function instance with same name which does not raise
    an `InternalAnnotationError` exception.
    if `func` is a string, overload will return another registering function
    which will register to the specified name.

    The decorated function takes some new attributes:
    - __pyod_annotate__: The raw function
    - __pyod_overloads__: The list of the function overloads
    - overload(func: Callable) registers the passed function under the same \
      name.

    :param func: the function to annotate
    :param name: optional name under which to register.

    :return: the wrapper function
    """
    if isinstance(func, str):
        return partial(overload, name=func)
    if name is None or not isinstance(name, str):
        name = get_name(func)
    if name not in __overloads__:
        __overloads__[name] = []
    __overloads__[name].append(annotate(func, True))

    @wraps(func)
    def wrapper(*args, **kw):
        for f in __overloads__[name]:
            try:
                val = f(*args, **kw)
            except InternalAnnotationError:
                continue
            else:
                break
        else:
            raise OverloadError(
                f"No overload of function: {get_name(func)}"
                f" matches types of arguments: {args}, {kw}",
            )
        return val

    wrapper.__pyod_overloads__ = __overloads__[name]
    wrapper.__pyod_overloads_name__ = name
    wrapper.overload = partial(overload, name=name)

    return wrapper


def annotateClass(cls: Any):
    """
    Annotates a class object, wrapping and replacing over it's __setattr__
    and typechecking over each attribute assignment.
    If no annotation for the passed object found it ignores it till it is
    found
    it recursively annotates the classes methods except `__pyod_norecur__`
    attribute is defines
    """
    if not hasattr(cls, "__annotations__"):
        cls.__annotations__ = {}
    if isinstance(cls, bool):
        return partial(annotate, recur=cls)
    recur = not hasattr(cls, "__pyod_norecur__")
    setter = cls.__setattr__
    if recur:
        for x in dir(cls):
            if hasattr(getattr(cls, x), "__annotations__"):
                setattr(
                    cls,
                    x,
                    annotate(
                        getattr(
                            cls,
                            x,
                        ),
                    ),
                )

    @wraps(cls.__setattr__)
    def new_setter(self: Any, name: str, value: Any) -> Any:
        if any(isinstance(x, str) for x in self.__annotations__.values()):
            resolveAnnotations(self)

        if name not in self.__annotations__:
            return setter(self, name, value)  # do not check if no annotations
        elif isinstance(self.__annotations__[name], Cast):
            return setter(self, name, self.__annotations__[name](value))
        elif not typeMatch(value, self.__annotations__[name]):
            raise AnnotationError(
                f"value {value!r} does not match annotation"
                f"of attribute: {name!r}:{self.__annotations__[name]!r}"
                f" of object of class {get_name(cls)}",
            )
        return setter(self, name, value)

    cls.__setattr__ = new_setter
    return cls


__version__ = '2.0.0'
__author__ = 'ken-morel'
