[![Release status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/mai)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main&cache=3000)](https://coveralls.io/github/ken-morel/pyoload?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pyoload/badge/?version=latest)](https://pyoload.readthedocs.io)
[![Pypi downloads](https://img.shields.io/pypi/dd/pyoload)](https://pypi.org/project/pyoload)
[![Pypi downloads](https://img.shields.io/pypi/dw/pyoload)](https://pypi.org/project/pyoload)

# pyoload

Hy pythonista! I'm happy to present to you `pyoload`, as from my words:

  A python module for extended and recursive type checking and casting of
  function arguments and class attributes during runtime

Here we use some of the beautiful and clean features offered by python, including
decorators and descriptors to help you type check during runtime

Here are some simple usage examples to fill this pypi page.

## annotate

This decorator function uses the power of `inspect.signature` to check the arguments
passed to the function using it's annotations with support for default values, generic aliase
and annotations adding some more annotation types for convenience, lower some code.

```python
from pyoload import *

@annotate
def foo(
    a: str,     # this has an annotation
    b=3,        # this uses a default value
    c: int = 0  # here both
) -> tuple[str, int]:  # The return type
    ...
```

```python
from pyoload import *

@annotate
def foo(
    b=dict[str | int, float],     # here a GenericAlias
    c: Cast(list[int]) = '12345'  # here a recursive cast
):  # No return type
    ...
```

## multimethod

This uses the same principles as annotate but allows multiple dispatching
(a.k.a runtime overloading?) of functions.

```python
from pyoload import *

@multimethod
def foo(a, b):
    print("two arguments")

@multimethod
def foo(a: Values((1, 2, 3))):
    print('either 1, 2 or 3')

@foo.overload
def _(a: Any):
    raise ValueError()
```

## annotations

These are what pyoload adds to the standard annotations:

> [!NOTE]
> The added annotations are still not mergeable with the standard types.

### `pyoload.Values`

A simple `tuple` subclass, use them as annotation and it will validate only
included values.
```python
@annotate
def foo(bar: Values(range(5))):
    ...
```

### `pyoload.Cast`

This performs recursive casting of the passed arguments into the specified type
It supports `dict` generic aliases as `dict[str, int | str] ` and tries cast in
the specified order when the type is a Union.

```python
@annotate
def foo(bar: Cast(tuple[int | str])):
    print(bar)

foo((3, "3"))  # (3, 3)
foo((3j, " "))  # ('3j', ' ')
```

### `pyoload.Checks`

Permits You tou use custom checker methods, e.g

```python
from pyoload import *

test = lambda val: True  # put your check here

def foo(a: Checks(func=test):
    ...
```

If the check name is prepended with a `_`, it will be negated, and an exception
is raised if it fails.
You can register your own checks using `Check.register`, as

```python
@Check.register('mycheck')
def _(param, value):
    print(param, value)

Checks(mycheck='param')('val')  # Will raise error on check failure

@annotate
def foo(a: Checks(mycheck='param')):
    ...
```

Checks can be used as annotations;
called using `pyoload.Checks` as `Checks(foo=bar)(val)`; or
Invoked directly using `pyoload.Checks` as:
`Check.check(name, param, arg)`

#### len

Receives as argument an integer value specified the expected length or
a slice in which the length should be found

#### gt, lt, eq

Compares grater than, less than and aqual to from the parameter
to the value.

#### func

Uses a function for validation, the function could return a boolean
or raise an error.
It could be passed directly as positional arguments to pyoload.Checks
as: `Checks(func1, func2, foo=bar, foo2=bar2)`

### Checked and casted attributes

`CheckedAttr` and `CastedAttr`, are simple descriptors which will perform
the casting or checks on assignment.

```python
from pyoload import *

class address:
    number = CastedAttr(tuple[int])
    
```

The values are checked or casted on assignment

> [!NOTE]
> The attributes will return `None` if not yet initialized
