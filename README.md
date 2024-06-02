[![Release status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/mai)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main)](https://coveralls.io/github/ken-morel/pyoload?branch=mai)
[![Documentation Status](https://readthedocs.org/projects/pyoload/badge/?version=latest)](https://pyoload.readthedocs.io)
[![Pypi downloads](https://img.shields.io/pypi/dm/pyoload)](https://pypi.org/project/pyoload)

# pyoload

pyoload is a little initiative to integrate tools for typechecking and
casting in python functions and classes.

# usage

## `pyoload.annotate`

Simple decorator over functions or classes

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

But if the attribute does not yes have annotations, it gets it using
`type(val)` and adds it to the annotations.

```python
from pyoload import *

@annotate
class Person:
    age: int

    def __init__(self: Any, age: int, name: str):
        self.age = age
        self.name = name


djamago = Person(15, 'djamago')  # {'age': <class 'int'>, 'name': <class 'str'>}

print(djamago.__annotations__)
```

## `pyoload.overload`

When decorating a function it:
- annotates the function with the special kwarg `is_overload=True`
- gets the function's name using `pyoload.get_name` and if needed
  creates a new register dictionarry value in
  `pyoload.__overloads__[name]` and stores a copy in
  the function's `.__pyod_overloads__`

And on each call it simply loops through each function entry, while
it catches a `pyoload.InternalAnnotationError` which is raised when
the special `is_overload` is set to true

> tip
  you may raise :python:`pyoload.InternalAnnotationError` inside an overloaded
  function after carrying out some other checks and pyoload will switch to the
  next oveload.

```python
@overload
def foo(a: int):
    ...

@overload
def foo(b: str, c: float):
    ...

foo.overload
def foo_hello(d: dict[str, list[int]]):
    ...
```

## tyme matches `pyoload.typeMatch(val, type)`

this function simply finds type compatibility between the passes arguments

the type could be:
- a class
- a Union e.g `int|str`
- a generic alias e.g `dict[str, int]`
- a subclass of `pyoload.PyoloadAnnotation` as:
  - `pyoload.Cast`
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

### casting recursiion

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

def foo(bar: Checks(is_equal=3)):
    pass

foo(3)  # param=3 value=3
foo('4')


```

