[![Release status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/mai)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main&cache=3000)](https://coveralls.io/github/ken-morel/pyoload?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pyoload/badge/?version=latest)](https://pyoload.readthedocs.io)
[![Pypi downloads](https://img.shields.io/pypi/dd/pyoload)](https://pypi.org/project/pyoload)
[![Pypi downloads](https://img.shields.io/pypi/dw/pyoload)](https://pypi.org/project/pyoload)

# pyoload

pyoload is a little initiative to integrate tools for typechecking and
casting in python functions and classes.

# usage

## `pyoload.annotate`

Simple decorator over functions and classes

### functions

e.g

```python
from pyoload import *

@annotate
def foo(bar: int) -> str:
    ...

@annotate
def bar(foo: str):
    ...
```

raises `pyoload.AnnotationError` when type mismatch

### classes

When annotating a class, pyoload wraps the classes `__setattr__` with
a typechecker function which typechecks the passed value on each assignment.

It also calls annotate on each of it's methods, except the class has a
`__annotate_norecur__` attribute.

Newer from version 1.1.3, pyoload ignores attributes with no annotations and does not check
them.

```python
from pyoload import *

@annotate
class Person:
    age: 'int'

    def __init__(self: Any, age: int, name: str):
        self.age = age
        self.name = name


djamago = Person(15, 'djamago')

print(djamago.__annotations__)  # {'age': <class 'int'>}
```

## `pyoload.multimethod`

When decorating a function it:
- annotates the function with the special kwarg `is_overload=True`
- gets the function's name using `pyoload.get_name` and if needed
  creates a new dictionarry value in
  `pyoload.__overloads__[name]` where it stores all ~~overloads~~dispatches and stores a copy in
  the function's `.__pyod_overloads__` attribute.

And on each call it simply loops through each function entry, while
it catches a `pyoload.InternalAnnotationError` which is raised when
the special `is_overload` is set to true

> [!TIP]
> you may raise `pyoload.InternalAnnotationError` inside ~~an overloaded
  function~~a multimethod after carrying out some other checks and pyoload will switch to the
  next oveload.

```python
@overload
def foo(a: int):
    ...

@overload
def foo(b: str, c: float):
    ...

@foo.overload
def foo_hello(d: dict[str, list[int]]):
    ...
```


## type checking with `pyoload.typeMatch(val, type)`

this function simply finds type compatibility between the passes arguments

the type could be:
- a class
- a Union e.g `int|str`
- a generic alias e.g `dict[str, int]`
- a subclass of `pyoload.PyoloadAnnotation` as:
  - `pyoload.Checks`
  - `pyoload.Values`



## Casting with `pyoload.Cast`

Most pyoload decorators support `pyoload.Cast` instances,
When used as an annotation the value is casted to the specified type.

```python
def foo(a: str):
    print(repr(a))

foo(3.5)  # '3.5'
```

### casting recursion

Using recursion it supports Generic Aliases of `dict` and builtin iterable
types as `list` and `tuple`.

```python
from pyoload import Cast

caster = Cast(dict[str, list[tuple[float]]]) # a dictionary of names of
                                             # places[str] to a list of their
                                             # (x, y) coordinates
                                             #             [list[tuple[float]]]

raw = {
    4: (
        ['1.5', 10],
        [10, '1.5'],
    )
}
print(caster(raw))  # {'4': [(1.5, 10.0), (10.0, 1.5)]}
```

> Note
  When `pyoload.Cast` receives a Union as `int|str` it tries to
  cast to the listed forms in the specific order, thus if we have
  `test = (3j, 11.0)` and `caster = Cast(tuple[float|str])` casting with
  `caster(test)` will give `('3j', 11.0)`, since complex `3j` can not be
  converted to float, and `pyoload.Cast.cast` will fallback to `str`

## writing checks pyoload.Checks

It provides a simple API for writing custom functions for checking.

```python
from pyoload import *

Check.register('is_equal')
def isnonecheck(param, value):
    print(f'{param=}, {value=}')
    if param != value:
        raise Check.CheckError(f'{param!r} not equal to {value!r}')

@annotate
def foo(bar: Checks(is_equal=3)):
    pass

foo(3)  # param=3 value=3
foo('4')

Traceback (most recent call last):
  File "C:\pyoload\src\del.py", line 77, in <module>
    foo('4')
  File "C:\pyoload\src\pyoload\__init__.py", line 514, in wrapper
    raise AnnotationErrors(errors)
pyoload.AnnotationErrors: [AnnotationError("Value: '4' does not match annotation: <Checks(is_equal=3)> for argument 'bar' of function __main__.foo")]
```

It provides builtin checkes as: lt, gt, ge, le, eq, `func:Callable`,
`type:Any|PyoloadAnnotation`

## using `pyoload.CheckedAttr` and `pyoload.CastedAttr`

`pyoload` provides:
- `pyoload.CheckedAttr` A descriptor which does the type checking on
  assignment, and
- `pyoload.CastedAttr` Another descriptor Which stores a casted copy of the values it is assigned

```python
class Person:
    age = CheckedAttr(gt=0)
    phone = CastedAttr(tuple[int])

    def __init__(self, age, phone):
        self.age = age
        self.phone = phone

temeze = Person(17, "678936798")

print(temeze.age)  # 17
print(temeze.phone)  # (6, 7, 8, 9, 3, 6, 7, 9, 8)

mballa = Person(0, "123456")
Traceback (most recent call last):
  File "C:\pyoload\src\del.py", line 92, in <module>
    mballa = Person(0, "123456")
             ^^^^^^^^^^^^^^^^^^^
  File "C:\pyoload\src\del.py", line 84, in __init__
    self.age = age
    ^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 264, in __set__
    self(value)
  File "C:\pyoload\src\pyoload\__init__.py", line 227, in __call__
    Check.check(name, params, val)
  File "C:\pyoload\src\pyoload\__init__.py", line 132, in check
    check(params, val)
  File "C:\pyoload\src\pyoload\__init__.py", line 187, in gt_check
    raise Check.CheckError(f'{val!r} not gt {param!r}')
pyoload.Check.CheckError: 0 not gt 0
```


[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/G2G4XYJU6)
