from typing import Any, GenericAlias
from types import UnionType
from functools import wraps, partial
from inspect import isclass

import sys


class AnnotationError(ValueError):
    pass


class AnnotationErrors(AnnotationError):
    pass


class InternalAnnotationError(Exception):
    pass


class CastingError(TypeError):
    pass


class OverloadError(TypeError):
    pass


class AnnotationResolutionError(AnnotationError):
    _raise = False


class Values(tuple):
    """wrapper class in case of several value"""

    def __call__(self, val):
        return val in self

    def __str__(self):
        return 'Values(' + ', '.join(map(repr, self)) + ')'

    __repr__ = __str__


Vs = Values


def get_name(funcOrCls):
    return funcOrCls.__module__ + '.' + funcOrCls.__qualname__


class Check:
    checks_list = {}

    def __init_subclass__(cls, subclass):
        cls.register(cls.name, cls.__call__)

    @classmethod
    def register(cls, name):
        if name in cls.checks_list:
            raise Check.CheckNameAlreadyExistsError(name)

        def inner(func):
            cls.checks_list[name] = func
        return inner

    @classmethod
    def check(cls, name, params, val):
        print(cls, name, params, val)
        check = cls.checks_list.get(name)
        if check is None:
            raise Check.CheckDoesNotExistError(name)
        check(val, params)

    class CheckNameAlreadyExistsError(ValueError):
        pass

    class CheckDoesNotExistError(ValueError):
        pass

    class CheckError(Exception):
        pass


@Check.register('len')
def len_check(params, val):
    print(params, val)
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


@Check.register('lt')
def lt_check(param, val):
    if not val < param:
        raise Check.CheckError()


@Check.register('le')
def le_check(param, val):
    if not val <= param:
        raise Check.CheckError()


@Check.register('ge')
def ge_check(param, val):
    if not val >= param:
        raise Check.CheckError()


@Check.register('gt')
def gt_check(param, val):
    if not val > param:
        raise Check.CheckError()


@Check.register('func')
def func_check(param, val):
    if not param(val):
        raise Check.CheckError()


@Check.register('match_')
def matches_check(param, val):
    if not typeMatch(val, param):
        raise Check.CheckError()


class Checks:
    def __init__(self, **checks):
        self.checks = checks
        print(f'{checks=}')

    def __call__(self, val):
        print(self.checks, val)
        for name, params in self.checks.items():
            Check.check(name, params, val)

    def __str__(self):
        ret = '<Checks('
        for k, v in self.checks.items():
            ret += f'{k}={v!r}, '
        ret = ret[:-2] + ')>'
        return ret

    __repr__ = __str__


class Cast:
    @staticmethod
    def cast(val, totype):
        if isinstance(totype, GenericAlias):
            if totype.__origin__ == dict:
                if len(totype.__args__) == 2:
                    kt, vt = totype.__args__
                elif len(totype.__args__) == 1:
                    kt, vt = Any, totype.__args__[1]
                print(f"{totype=} {kt=} {vt=}")
                return {
                    Cast.cast(k, kt): Cast.cast(v, vt) for k, v in val.items()
                }
            else:
                sub = totype.__args__[0]
                return totype.__origin__([
                    Cast.cast(v, sub) for v in val
                ])
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

    def __init__(self, type):
        """
        creates a casting object for the specified type
        """
        self.type = type

    def __call__(self: 'Cast', val: Any):
        '''
        Calls to the type specified in the object `.type` attribute
        :param self: The cast onject
        :param val: the value to be casted

        :return: The casted value
        '''
        try:
            return Cast.cast(val, self.type)
        except Exception as e:
            raise CastingError(
                f'Exception({e}) while casting: {val!r} to {self.type}',
            ) from e


def typeMatch(val: Any, spec: type) -> bool:
    '''
    recursively checks if type matches
    :param val: The value to typecheck
    :param spec: The type specifier

    :return: A boolean
    '''
    if spec == Any or spec is None or val is None:
        return True
    if isinstance(spec, Values):
        return spec(val)
    elif isinstance(spec, Checks):
        print(val)
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
    '''
    gets the module to which an object, function or class belongs
    :param obj: the object
    :returns: the module
    '''
    return sys.modules[obj.__module__]


def resolveAnnotations(obj: Any) -> None:
    '''
    Evaluates all the stringized annotations of the argument

    :param obj: The object
    :returns: None
    '''
    if isclass(obj) or hasattr(obj, '__class__'):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(
                        v,
                        dict(vars(get_module(obj))), dict(vars(obj)),
                    )
                except Exception as e:
                    raise AnnotationResolutionError(
                        f'Exception: {e!s} while resolving'
                        f' annotation {e}={v!r} of object {obj!r}',
                    ) from e
    elif callable(obj):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(v, obj.__globals__)
                except Exception as e:
                    raise AnnotationResolutionError(
                        f'Exception: {k!s} while resolving'
                        f' annotation {v!r} of function {obj!r}',
                        f'globals: {obj.__globals__}'
                    ) from e


def annotate(func: callable, oload: bool = False) -> callable:
    '''
    returns a wrapper over the passed function
    which typechecks arguments on each call
    :param func: the function to annotate
    :param oload: internal

    :return: the wrapper function
    '''
    if isclass(func):
        return annotateClass(func)
    anno = func.__annotations__
    if len(anno) == 0:
        return func

    @wraps(func)
    def wrapper(*args, **kw):
        names = tuple(anno.keys())
        if any(isinstance(x, str) for x in anno.values()):
            resolveAnnotations(func)
        vals = {}
        try:
            if func.__defaults__:
                for i, v in enumerate(reversed(func.__defaults__)):
                    vals[names[-1 - i]] = v
            for i, v in enumerate(args):
                vals[names[i]] = v
            vals.update(kw)
        except IndexError as e:
            raise AnnotationError(
                f'Was function {get_name(func)} properly annotated?',
            ) from e

        errors = []
        for k, v in vals.items():
            if isinstance(anno[k], Cast):
                vals[k] = anno[k](v)
                continue
            print(v)
            if not typeMatch(v, anno[k]):
                if oload:
                    raise InternalAnnotationError()
                errors.append(
                    AnnotationError(
                        f'Value: {v!r} does not match annotation: {anno[k]!r}'
                        f' for argument {k!r} of function {get_name(func)}',
                    ),
                )
        if len(errors) > 0:
            raise AnnotationErrors(errors)

        ret = func(**vals)
        if 'return' in anno:
            if not typeMatch(ret, anno['return']):
                raise AnnotationError(
                    f"return value {ret!r} does not match annotation: "
                    f"{anno['return']} of function {get_name(func)}",
                )
        return ret
    wrapper.__pyod_annotate__ = func
    return wrapper


__overloads__ = {}


def overload(func: callable, name: str | None = None):
    '''
    returns a wrapper over the passed function
    which typechecks arguments on each call
    and finds the function instance with same name which does not raise
    an `InternalAnnotationError` exception
    :param func: the function to annotate
    :param oload: internal

    :return: the wrapper function
    '''
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
                f'No overload of function: {get_name(func)}'
                ' matches types of arguments',
            )
        return val

    wrapper.__pyo_overloads__ = __overloads__[name]
    wrapper.__pyo_overloads_name__ = name

    return wrapper


def annotateClass(cls):
    '''
    Annotates a class object, wrapping and replacing over it's __setattr__
    and typechecking over each attribute assignment.
    If no annotation for the passed object found it sets it to `type(val)`
    '''
    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = {}
    if isinstance(cls, bool):
        return partial(annotate, recur=cls)
    recur = not hasattr(cls, '__annotate_norecur__')
    setter = cls.__setattr__
    if recur:
        for x in dir(cls):
            if hasattr(getattr(cls, x), '__annotations__'):
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

    def new_setter(self, name, value):
        if any(isinstance(x, str) for x in self.__annotations__.values()):
            resolveAnnotations(self)

        if name not in self.__annotations__:
            if value is not None:
                self.__annotations__[name] = type(value)
        elif not typeMatch(value, self.__annotations__[name]):
            raise AnnotationError(
                f'value {value!r} does not match annotation'
                f'of attribute: {name!r}:{self.__annotations__[name]!r}'
                f' of object of class {get_name(cls)}',
            )
        return setter(self, name, value)
    cls.__setattr__ = new_setter
    return cls


__version__ = '1.1.0'
