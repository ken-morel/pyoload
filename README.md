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

## `pyoload.ov`


