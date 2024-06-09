"""
`pyoload` is a python module which will help you type check your function
arguments and object attribute types on function call and attribute assignment.

It supports the various builtin data types supported by :py:`isinstance` and
adds support for:
- :py:`typing.GenericAlias`
- :py:`pyoload.PyoloadAnnoation` subclasses as:
  - :py:`pyoload.Cast`
  - :py:`pyoload.Values`
  - :py:`pyoload.Checks`

:Authors:
  ken-morel

:Version: 2.0.0
:Dedication: To the pythonista.
"""

from functools import partial
from functools import wraps
from inspect import _empty
from inspect import getmodule
from inspect import isclass
from inspect import isfunction
from inspect import ismethod
from inspect import signature
from typing import Any
from typing import Callable
from typing import GenericAlias
from typing import Type
from typing import Union
from typing import get_args
from typing import get_origin

NoneType = type(None)
try:
    from types import UnionType
except ImportError:
    UnionType = Union


class AnnotationError(ValueError):
    """
    base exception for most pyoload errors is raised when a non-subclassable
    error occurs.
    """


class AnnotationErrors(AnnotationError):
    """
    Hosts a list of `AnnotationError` instances.
    """


class InternalAnnotationError(Exception):
    pass


class CastingError(TypeError):
    """
    Error during casting, holds the actual error
    """


class OverloadError(TypeError):
    """
    Error in or during overload calling.
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

        >>> isPrimaryColor = Values(('red', 'green', 'blue'))
        >>> isPrimaryColor
        Values('red', 'green', 'blue')
        >>> isPrimaryColor('red')
        True
        >>> isPrimaryColor('orange')
        False
        >>> isPrimaryColor(4)
        False

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

    >>> def foo():
    ...     pass
    ...
    >>> get_name(foo)
    '__main__.foo'
    >>> get_name(get_name)
    'pyoload.get_name'
    >>> get_name(print)
    'builtins.print'

    :param funcOrCls: The object who's name to return

    :returns: modulename + qualname
    """
    mod = funcOrCls.__module__
    name = funcOrCls.__qualname__
    return mod + "." + name


class Check:
    """
    A class basicly abstract which holds registerred checks in pyoload
    A new check can be registerred by subclassing whith a non-initializing
    callable class, the name will be gotten from the classes :py:`.name`
    attribute or the basename of the class if not present.

    A :py:`Check.CheckNameAlreadyExistsError` is raised if the check is already
    registerred.
    """

    checks_list = {}

    def __init_subclass__(cls: Any):
        """
        register's subclasses as checks
        """
        if hasattr(cls, "name"):
            name = cls.name
        else:
            name = cls.__name__
        obj = cls()
        obj.__qualname__ = cls.__qualname__
        Check.register(name)(obj)

    @classmethod
    def register(
        cls: Any,
        name: str,
    ) -> Callable[[Callable[[Any, Any], NoneType]], Callable]:
        """
        returns a callable which registers a new checker method

        used as:

        >>> @Check.register('integer_not_equal neq') # can register on multiple
        ... def _(param, val):                      # names seperated by spaces
        ...     '''
        ...     :param param: The parameter passed as kwarg
        ...     :param val: The value passed as argument
        ...     '''
        ...     assert param != val  # using assertions
        ...     if not isinstance(param, int) or isinstance(val, int):
        ...         raise TypeError()  # using typeError, handles even unwanted
        ...     if param == val:        # errors in case wrong value passed
        ...         raise Check.CheckError(f"values {param=!r} and {val=!r} no\
t equal")
        ...
        >>> Checks(neq=3)
        <Checks(neq=3)>
        >>> Checks(neq=3)(3)
        Traceback (most recent call last):
          File "C:\\pyoload\\src\\pyoload\\__init__.py", line 172, in check

          File "<stdin>", line 8, in _
        AssertionError

        The above exception was the direct cause of the following exception:

        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "C:\\pyoload\\src\\pyoload\\__init__.py", line 291, in __call__
            '''

          File "C:\\pyoload\\src\\pyoload\\__init__.py", line 174, in check
            for name in names:
            ^^^^^^^^^^^^^^^^^^^
        pyoload.Check.CheckError


        :param cls: the Check class
        :param name: the name to be registerred as.

        :returns: a function which registers the check under the name
        """
        names = [x.strip() for x in name.split(" ") if x.strip() != ""]
        for name in names:
            if name in cls.checks_list:
                raise Check.CheckNameAlreadyExistsError(name)

        def inner(func: Callable) -> Callable:
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
        :param name: One of the registerred name of the check
        :param params: The parameters to pass to the check
        :param val: The value to check

        :returns: :py:`None`
        """
        check = cls.checks_list.get(name)
        if check is None:
            raise Check.CheckDoesNotExistError(name)
        try:
            check(params, val)
        except (AssertionError, TypeError) as e:
            raise Check.CheckError(e) from e

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


class BuiltinChecks:
    """
    This class holds the check definitions and callables for the varios builtin
    checks.
    """

    @staticmethod
    @Check.register("len")
    def len_check(params: Union[int, slice], val):
        """
        This check performs a length check, and may receive as parameter
        an integer, where in search for equity between the length and the
        integer, on a :py:`slice` instance where it tries to fit the length
        in the slice provided parameters, which are optional.
        Note:
          it is been evaluated as :py:`slice.start <= val < slice.stop`
        """
        if isinstance(params, int):
            if not len(val) == params:
                raise Check.CheckError(f"length of {val!r} not eq {params!r}")
        elif isinstance(params, slice):
            if params.start is not None:
                if not len(val) >= params.start:
                    raise Check.CheckError(
                        f"length of {val!r} not gt {params.start!r} not in:"
                        f" {params!r}"
                    )
            if params.stop is not None:
                if not len(val) < params.stop:
                    raise Check.CheckError(
                        f"length of {val!r} not lt {params.stop!r} not in:"
                        f" {params!r}",
                    )
        else:
            raise Check.CheckError(f"wrong {params=!r} for len")

    @staticmethod
    @Check.register("lt")
    def lt_check(param: int, val: int):
        """
        performs `lt(lesser than)` check
        """
        if not val < param:
            raise Check.CheckError(f"{val!r} not lt {param!r}")

    @staticmethod
    @Check.register("le")
    def le_check(param: int, val: int):
        """
        performs `le(lesser or equal to)` check
        """
        if not val <= param:
            raise Check.CheckError(f"{val!r} not gt {param!r}")

    @staticmethod
    @Check.register("ge")
    def ge_check(param: int, val: int):
        """
        performs `ge(greater or equal to)` check
        """
        if not val >= param:
            raise Check.CheckError(f"{val!r} not ge {param!r}")

    @staticmethod
    @Check.register("gt")
    def gt_check(param: int, val: int):
        """
        performs `gt(greater than)` check
        """
        if not val > param:
            raise Check.CheckError(f"{val!r} not gt {param!r}")

    @staticmethod
    @Check.register("eq")
    def eq_check(param: int, val: int):
        """
        Checks the two passed values are equal
        """
        if not val == param:
            raise Check.CheckError(f"{val!r} not eq {param!r}")

    @staticmethod
    @Check.register("func")
    def func_check(param: Callable[[Any], bool], val: Any):
        """
        Uses the function passed as parameter.
        The function should return a boolean
        """
        if not param(val):
            raise Check.CheckError(f"{param!r} call returned false on {val!r}")

    @staticmethod
    @Check.register("type")
    def matches_check(param, val):
        """Uses `type_match(val, param)` to check the value"""
        m, e = type_match(val, param)
        if not m:
            raise Check.CheckError(f"{val!r} foes not match type {param!r}", e)

    @staticmethod
    @Check.register("isinstance")
    def instance_check(param, val):
        """uses :py:`isinstance(val, param)` to check the value"""
        if not isinstance(val, param):
            raise Check.CheckError(f"{val!r} foes no instance of {param!r}")


class Checks(PyoloadAnnotation):
    """
    Pyoload annotation holding several checks called on typechecking.
    """

    __slots__ = ("checks",)

    def __init__(
        self: PyoloadAnnotation,
        __check_func__=None,
        /,
        **checks: dict[str, Callable[[Any, Any], NoneType]],
    ) -> Any:
        """
        crates the check object,e.g

        >>> class foo:
        ...    bar: pyoload.Checks(gt=4)

        :param checks: the checks to be done.

        :returns: self
        """
        if __check_func__ is not None:
            checks['func'] = __check_func__
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

    __slots__ = ("name", "value")
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
        self.name = name
        self.value = None

    def __get__(self: Any, obj: Any, type: Any):
        return self.value

    def __set__(self: Any, obj: Any, value: Any):
        self(value)
        self.value = value


class Cast(PyoloadAnnotation):
    """
    Holds a cast object which describes the casts to be performed
    """

    __slots__ = ("type",)

    @staticmethod
    def cast(val: Any, totype: Any) -> Any:
        """
        **The gratest deal.**
        Recursively casts the given value to the specified structure or type
        e.g

        >>> Cast.cast({ 1: 2}, dict[str, float])
        {'1': 2.0}

        :param val: the value to cast
        :param totype: The type structure to be casted to.

        :returns: An instance of the casting type
        """
        if totype == Any:
            return val
        if isinstance(totype, GenericAlias):
            args = get_args(totype)
            if get_origin(totype) == dict:
                if len(args) == 2:
                    kt, vt = args
                elif len(args) == 1:
                    kt, vt = args[0], Any
                return {Cast.cast(k, kt): Cast.cast(v, vt) for k, v in val.items()}
            else:
                sub = args[0]
                return get_origin(totype)([Cast.cast(v, sub) for v in val])
        if get_origin(totype) is Union or get_origin(totype) is UnionType:
            errors = []
            for subtype in get_args(totype):
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

    __slots__ = "value"
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
        >>> mballa = Person(0, "123456")
        Traceback (most recent call last):
          ...
        pyoload.Check.CheckError: 0 not gt 0
        """
        super().__init__(type)

    def __set_name__(self: Any, obj: Any, name: str, typo: Any = None):
        self.value = None

    def __get__(self: Any, obj: Any, type: Any):
        return self.value

    def __set__(self: Any, obj: Any, value: Any):
        self.value = self(value)


def type_match(val: Any, spec: Union[Type, PyoloadAnnotation]) -> tuple:
    """
    recursively checks if type matches

    :param val: The value to typecheck
    :param spec: The type specifier

    :returns: A tuple of the match status and the optional errors
    """
    try:
        return (isinstance(val, spec), None)
    except TypeError:
        pass
    if spec is any:
        raise TypeError("May be have you confused `Any` and `any`")

    if spec is Any or spec is _empty or spec is None or val is None:
        return (True, None)
    if isinstance(spec, Values):
        return (spec(val), None)
    elif isinstance(spec, Checks):
        try:
            spec(val)
        except Check.CheckError as e:
            return (False, e)
        else:
            return (True, None)
    elif isinstance(spec, GenericAlias):
        orig = get_origin(spec)
        if not isinstance(val, orig):
            return (False, None)

        if orig == dict:
            args = get_args(spec)
            if len(args) == 2:
                kt, vt = args
            elif len(args) == 1:
                kt, vt = args[0], Any
            else:
                return (True, None)

            for k, v in val.items():
                k, e = type_match(k, kt)
                if not k:
                    return (k, e)
                v, e = type_match(v, vt)
                if not v:
                    return (False, e)
            else:
                return (True, None)
        else:
            sub = get_args(spec)[0]
            for val in val:
                m, e = type_match(val, sub)
                if not m:
                    return (False, e)
            else:
                return (True, None)


def resove_annotations(obj: Callable) -> None:
    """
    Evaluates all the stringized annotations of the argument

    :param obj: The object of which to evaluate annotations

    :returns: None
    """
    if not hasattr(obj, '__annotations__'):
        raise AnnotationResolutionError(
            f"object {obj=!r} does not have `.__annotations__`",
        )
    if isfunction(obj):
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
    elif isclass(obj) or hasattr(obj, "__class__"):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(
                        v,
                        dict(vars(getmodule(obj))),
                        dict(vars(obj)) if hasattr(obj, '__dict__') else None,
                    )
                except Exception as e:
                    raise AnnotationResolutionError(
                        (
                            f"Exception: {e!s} while resolving"
                            f" annotation {e}={v!r} of object {obj!r}"
                        ),
                    ) from e


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
    if isinstance(func, bool):
        return partial(annotate, force=True)
    if not hasattr(func, "__annotations__"):
        return func
    if isclass(func):
        return annotate_class(func)
    if len(func.__annotations__) == 0:
        return func
    if not is_annotable(func) and not force:
        return func

    @wraps(func)
    def wrapper(*pargs, **kw):
        if str in map(type, func.__annotations__.values()):
            resove_annotations(func)
        sign = signature(func)
        try:
            args = sign.bind(*pargs, **kw)
        except Exception:
            if oload:
                raise InternalAnnotationError()
            else:
                raise
        errors = []
        for k, v in args.arguments.items():
            param = sign.parameters.get(k)
            if param.annotation is _empty:
                continue
            if param.annotation is None:
                continue
            if isinstance(param.annotation, Cast):
                args.arguments[k] = param.annotation(v)
                continue
            if not type_match(v, param.annotation)[0]:
                if oload:
                    raise InternalAnnotationError()
                errors.append(
                    AnnotationError(
                        f"Value: {v!r} does not match annotation:"
                        f" {param.annotation!r} for "
                        f"argument {k!r} of function {get_name(func)}",
                    ),
                )
        if len(errors) > 0:
            raise AnnotationErrors(errors)

        ret = func(**args.arguments)

        if sign.return_annotation is not _empty:
            ann = sign.return_annotation

            if isinstance(ann, Cast):
                return ann(ret)
            m, e = type_match(ret, ann)
            if not m:
                raise AnnotationError(
                    f"return value: {ret!r} does not match annotation:"
                    f" {ann!r} for "
                    f"of function {get_name(func)}",
                    e,
                )
        return ret

    wrapper.__pyod_annotate__ = func
    return wrapper


def unannotate(func: Callable) -> Callable:
    """
    Returns the underlying function returned by :py:`annotate`,
    if not annotated it returns the passed function.

    :param func: the function to unwrap

    :returns: The unwrapped function
    """
    if hasattr(func, "__pyod_annotate__"):
        return func.__pyod_annotate__
    else:
        return func


def unannotable(func: Callable) -> Callable:
    """
    Marks a function to be not annotable, the function will then not be wrapped
    by :py:`annotate` or :py:`multimethod`, except :py:`force=True` argument
    specified.
    """
    func = unannotate(func)
    func.__pyod_annotable__ = False
    return func


def annotable(func: Callable) -> Callable:
    """
    Marks a function to be annotatble by :py:`annotate` and :py:`overload`
    """
    func.__pyod_annotable__ = True
    return func


def is_annotable(func):
    """
    Returns if the function posses the unannotable mark.
    """
    return not hasattr(func, "__pyod_annotable__") or func.__pyod_annotable__


def is_annoted(func):
    """
    Determines if a function has been annotated.
    """
    return hasattr(func, "__pyod_annotate__")


__overloads__: dict[str, list[Callable]] = {}


def multimethod(func: Callable, name: str = None, force: bool = False) -> Callable:
    """
    returns a wrapper over the passed function
    which typechecks arguments on each call
    and finds the function instance with same name which does not raise
    an `InternalAnnotationError` exception.
    if `func` is a string, overload will return another registering function
    which will register to the specified name.

    The decorated function takes some new attributes:
    - __pyod_annotate__: The raw function
    - __pyod_dispatches__: The list of the function overloads
    - multimethod(func: Callable) registers the passed function under the same\
      name.

    :param func: the function to annotate
    :param name: optional name under which to register.
    :param force: overloads even unnanotable functions

    :returns: the wrapper function
    """
    if isinstance(func, str):
        return partial(multimethod, name=func)
    if name is None or not isinstance(name, str):
        name = get_name(func)
    if name not in __overloads__:
        __overloads__[name] = []
    __overloads__[name].append(annotate(func, oload=True, force=force))

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

    wrapper.__pyod_dispatches__ = __overloads__[name]
    wrapper.__pyod_overloads_name__ = name
    wrapper.overload = wrapper.add = partial(overload, name=name)

    return wrapper


overload = multimethod


def annotate_class(cls: Any, recur: bool = True):
    """
    Annotates a class object, wrapping and replacing over it's __setattr__
    and typechecking over each attribute assignment.
    If no annotation for the passed object found it ignores it till it is
    found
    it recursively annotates the classes methods except `__pyod_norecur__`
    attribute is defines
    """

    if isinstance(cls, bool):
        return partial(annotate_class, recur=cls)
    recur = not hasattr(cls, "__pyod_norecur__") and recur
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
        if str in map(type, self.__annotations__.values()):
            resove_annotations(self)

        if name not in self.__annotations__:
            return setter(self, name, value)  # do not check if no annotations
        elif isinstance(self.__annotations__[name], Cast):
            return setter(self, name, self.__annotations__[name](value))

        else:
            m, e = type_match(value, self.__annotations__[name])
            if not m:
                raise AnnotationError(
                    f"value {value!r} does not match annotation"
                    f"of attribute: {name!r}:{self.__annotations__[name]!r}"
                    f" of object of class {get_name(cls)}",
                    e,
                )
        return setter(self, name, value)

    cls.__setattr__ = new_setter
    return cls


__all__ = [
    "annotate",
    "overload",
    "multimethod",
    "Checks",
    "Check",
    "annotable",
    "unannotable",
    "unannotate",
    "is_annotable",
    "is_annoted",
    "resove_annotations",
    "Cast",
    "CastedAttr",
    "CheckedAttr",
    "Values",
    "AnnotationResolutionError",
    "AnnotationError",
]

__version__ = "2.0.0"
__author__ = "ken-morel"
