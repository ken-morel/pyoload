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
