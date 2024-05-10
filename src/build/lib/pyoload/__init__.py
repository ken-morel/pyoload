from typing import Any, GenericAlias, Union
from functools import wraps, partial
from inspect import isclass


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


def get_name(funcOrCls):
    return funcOrCls.__module__ + '.' + funcOrCls.__qualname__


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


class Cast:
    @staticmethod
    def cast(val, type):
        if issubclass(type, Union):
            type = type.__args__
        if isinstance(type, tuple):
            for x in type:
                try:
                    return Cast.cast(val, x)
                except Exception:
                    pass
            else:
                raise CastingError()
        return type(val) if not isinstance(val, type) else val

    def __init__(self, type):
        self.type = type

    def __call__(self, val):
        try:
            return Cast.cast(self.type, val)
        except Exception as e:
            raise CastingError(
                f'Exception while casting: {val!r} to {self.type}',
            ) from e


def typeMatch(val, spec):
    if spec == Any or spec is None:
        return True
    if isinstance(val, tuple):
        return isinstance(val, tuple)
    if isinstance(spec, Values):
        return spec(val)
    elif isinstance(spec, Validator):
        return spec(val)
    elif isinstance(spec, GenericAlias):
        if not isinstance(val, spec.__origin__):
            return False
        sub = spec.__args__
        for val in val:
            if not typeMatch(val, sub):
                return False
        else:
            return True
    else:
        return isinstance(val, spec)


def resolveAnnotations(anno, np, scope=None):
    for k, v in anno.items():
        if isinstance(v, str):
            try:
                anno[k] = eval(v, np, np)
            except Exception as e:
                raise AnnotationResolutionError(
                    f'Exception: {e!s} while resolving annotation {v!r} of {scope}',
                ) from e


def annotate(func, oload=False):
    """decorator annotates wrapped function"""
    if isclass(func):
        return annotateClass(func)
    anno = func.__annotations__

    @wraps(func)
    def wrapper(*args, **kw):
        names = tuple(anno.keys())
        if any(isinstance(x, str) for x in anno.values()):
            resolveAnnotations(anno, func.__globals__, get_name(func))
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
    if isinstance(cls, bool):
        return partial(annotate, recur=cls)
    recur = not hasattr(cls, '__annotate_norecur__')
    setter = cls.__setattr__
    anno = cls.__annotations__
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
        if any(isinstance(x, str) for x in anno.values()):
            resolveAnnotations(anno, globals(), get_name(cls))

        if name not in anno:
            anno[name] = type(value)
        if not typeMatch(value, anno[name]):
            raise AnnotationError(
                f'value {value!r} does not match annotation' +
                'of attribute: {name!r}:{anno[name]!r} of object of class {get_name(cls)}',
            )
        else:
            return setter(self, name, value)
    cls.__setattr__ = new_setter
    return cls


__version__ = '1.0.1'
