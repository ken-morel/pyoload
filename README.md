# pip-package-template-docker

[![Release Status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main)](https://coveralls.io/github/ken-morel/pyoload?branch=main)

pyoload has two main functions

annotate
========
Is used as a decorator on the function.
```python

from pyoload import annotate

@annotate
def twice(a:int) -> int:
    return a * 2

b = twice(4)
```
The annotate creates a wrapper over the decorated function which checks in for argument types over each function call using `pyoload.matchType(val, spec)`.
The original function is kept in the `.__pyod_annotate__` attribute.

overload
========
Implements function overloading in python via a simple decorator

```python
from pyoload import overload
import math
cache = {}

tan_is_real = lambda v: not (v + 90) % 180 == 0

@overload
def tan(num:Validator(tan_is_real, opposite=True)):
    raise ValueError(num)

@overload
def tan(num:int|float) -> float:
    return math.tan(num(

tan(6)
```

When an overload is registerred, the function name in the form `functionModuleName.functionQualName` is goten using `pyoload.get_name(funcOrClass)` an annotate is gotten using `pyoload.annotate(func, True)`
and a new list of overloads is created and stored in `pyoload.__overloads__` dictionarry under it's name. A reference to the list of annotated overloads is stored in the functions `.__pyod_overloads__`.

When the function is called, the wrapper tries all the functions registerred to that name to catch a `pyoload.InternalAnnotationError`. If none ran succesfully, it raises an `pyoload.OverloadError`.

Accepted annotations
====================

In addition to supporting normal plain types,
pyoload includes support for generic aliasses of iterable types and some other classes:

- `pyoload.Values(iterable)`
  e.g `Values("+-*/")` or `Values(range(6))`
- `pyoload.Cast(type)`
  Instructs pyoload to cast to the specified type
- A string
  The string contents will be evaluated as soon as first function call.
