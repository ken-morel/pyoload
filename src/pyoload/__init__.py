from typing import Any, GenericAlias, Union
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


g_n = get_name


class Validator:
    def __init__(self, func):
        if not callable(func):
            raise TypeError(self.__class__.__init__.__qualname__)
        self.func = func

    def __call__(self, val):
        try:
            return self.func()
        except Exception as e:
            raise AnnotationError(
                f'{type(e)} while using validator method: {get_name(self.func)}' +
                f'\n{e!s}',
            ) from e


Vf = Validator


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
                raise e
        else:
            return totype(val) if not isinstance(val, totype) else val

    def __init__(self, type):
        self.type = type

    def __call__(self, val):
        try:
            return Cast.cast(val, self.type)
        except Exception as e:
            raise CastingError(
                f'Exception({e}) while casting: {val!r} to {self.type}',
            ) from e


def typeMatch(val, spec):
    if spec == Any or spec is None or val is None:
        return True
    if isinstance(spec, Values):
        return spec(val)
    elif isinstance(spec, Validator):
        return spec(val)
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



def get_module(obj):
    return sys.modules[obj.__module__]


def resolveAnnotations(obj):
    if isclass(obj) or hasattr(obj, '__class__'):
        for k, v in obj.__annotations__.items():
            if isinstance(v, str):
                try:
                    obj.__annotations__[k] = eval(v, dict(vars(get_module(obj))), dict(vars(obj)))
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


def annotate(func, oload=False):
    """decorator annotates wrapped function"""
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
            if not typeMatch(v, anno[k]):
                if oload:
                    raise InternalAnnotationError()
                errors.append(
                    AnnotationError(
                        f'Value: {v!r} does not match annotation: {anno[k]!r}' +
                        f' for argument {k!r} of function {get_name(func)}',
                    ),
                )
        if len(errors) > 0:
            raise AnnotationErrors(errors)

        ret = func(**vals)
        if 'return' in anno:
            if not typeMatch(ret, anno['return']):
                raise AnnotationError(
                    f"return value {ret!r} does not match annotation: {anno['return']} of function {get_name(func)}",
                )
        return ret
    return wrapper


__overloads__ = {}


def overload(func, name=None):
    if isinstance(func, str):
        return partial(overload, name=func)
    if name is None or not isinstance(name, str):
        name = get_name(func)
    if name not in __overloads__:
        __overloads__[name] = []
    __overloads__[name].append(annotate(func, True))
    func.__overloads__ = __overloads__[name]

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
                f'No overload of function: {get_name(func)} matches types of arguments',
            )
        return val
    return wrapper


def annotateClass(cls):
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
                f'value {value!r} does not match annotation' +
                f'of attribute: {name!r}:{self.__annotations__[name]!r} of object of class {get_name(cls)}',
            )
        
        return setter(self, name, value)
    cls.__setattr__ = new_setter
    return cls


__version__ = '1.0.2'
