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

raises `pyoload.AnnotationError` when


