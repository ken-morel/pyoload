[![Release status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/mai)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main&cache=3000)](https://coveralls.io/github/ken-morel/pyoload?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pyoload/badge/?version=latest)](https://pyoload.readthedocs.io)
[![Pypi downloads](https://img.shields.io/pypi/dd/pyoload)](https://pypi.org/project/pyoload)
[![Pypi downloads](https://img.shields.io/pypi/dw/pyoload)](https://pypi.org/project/pyoload)

# pyoload

This adds some runtime type checking and warnings when enabled. It is disabled
by default.

Pyoload permits you to add runtime checking to classes on instance attribute
assignment and functions.

## usage

pyoload provides two basic methods:
- `pyoload.annotate`:       decorator over functions or methods.
- `pyoload.annotate_class`: decorator over classes.
All wrapped by `pyoload()` which checks what to be called.

```py
import pyoload

pyoload.debug()

@pyoload
def foo(a: int, b, c: str) -> tuple[str, int]:
    return ("ab", 23)

@pyoload
class myclass:
    pass
```

## pyolaod modes

Pyoload includes three modes of enum type `pyoload.Mode` and where the current
mode is in `pyoload.MODE`.

* **DEBUG**: Shows warnings, comments, exceptions activate via `pyoload.debug()`
* **DEV**  : Does not call upon validatore
* **PROD**(*DEFAULT*): `@pyoload` simply does nothing.

## Adding validators

You may add validators to check values furthermore.

```py
def validator(value) -> Optional[str]:
    if value.is_ok():
        return None
    else:
        return "Value is not Ok! pass a value which is Ok please."

@pyoload(comments=dict(val=validator))
def func(val):
    pass
```