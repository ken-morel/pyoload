[![Release status](https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ken-morel/pyoload/releases)
[![PyPI package](https://badge.fury.io/py/pyoload.svg)](https://pypi.org/project/pyoload)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pyoload)](https://pypi.org/project/pyoload)
[![Build Status](https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ken-morel/pyoload/tree/main)
[![Coverage Status](https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main&cache=3000)](https://coveralls.io/github/ken-morel/pyoload?branch=main)
[![Documentation Status](https://readthedocs.org/projects/pyoload/badge/?version=latest)](https://pyoload.readthedocs.io)
[![Pypi downloads](https://img.shields.io/pypi/dd/pyoload)](https://pypi.org/project/pyoload)
[![Pypi downloads](https://img.shields.io/pypi/dw/pyoload)](https://pypi.org/project/pyoload)
[![wakatime](https://wakatime.com/badge/github/ken-morel/pyoload.svg)](https://wakatime.com/badge/github/ken-morel/pyoload)

# pyoload 4.0

Runtime type-checking for Python with zero impact on production code.

- **Zero overhead when disabled:** When disabled, decorators return original functions and classes immediately with zero wrapper overhead.
- **Zero lock-in:** Standard Python type annotations are used. No proprietary type structures are placed inside your function signatures or classes.
- **Callable module:** `@pyoload` can be used directly as a decorator (`import pyoload; @pyoload`).

---

## Quick Start

```python
import pyoload

pyoload.enable()   # Enable runtime type checking (Disabled by default)

@pyoload
def add(a: int, b: int) -> int:
    return a + b

add(1, 2)    # Pass
add("x", 2)  # TypeError: Argument 'x' provided for parameter 'a' of function __main__.add does not match expected annotation <class 'int'>

@pyoload
class Point:
    x: int
    y: int
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

p = Point(1, 2)
p.x = "bad"  # TypeError: Cannot assign attribute 'x' = 'bad' on instance of class __main__.Point
```

---

## Activation & Scope Control

Activation is toggled via functions or context managers:

```python
pyoload.enable()      # Enables type-checking
pyoload.disable()     # Disables type-checking (zero overhead)
pyoload.is_enabled()  # Returns True if active
pyoload.init()        # Reads PYOLOAD_ENABLED / PYOLOAD_MODE environment variables
```

### Temporary Scope Overrides

Temporarily toggle type-checking within a `with` block:

```python
with pyoload.disabled():
    # Type-checking is temporarily disabled in this block
    fast_data_processing()

with pyoload.enabled():
    # Type-checking is temporarily enabled in this block
    untrusted_input_handler()
```

---

## API Reference

### Unified Dispatcher: `@pyoload` / `pyoload.pyoload`

Automatically dispatches to functions, classes, or modules:

```python
@pyoload
def compute(x: int) -> int:
    return x * 2

@pyoload
class User:
    name: str

import my_module
pyoload(my_module)
```

### `pyoload.annotate_function`

Annotates a specific function or method. Accepts single validators or lists/tuples of validators per parameter:

```python
@pyoload.annotate_function(
    age=[pyoload.ge(18), pyoload.le(120)],
    name=pyoload.non_empty,
    return_=pyoload.non_empty,
)
def register(age: int, name: str) -> str:
    return f"{name}:{age}"
```

### `pyoload.annotate_class`

Annotates instance attribute assignments (`__setattr__`). Supports standard classes and `@dataclass` instances:

```python
@pyoload.annotate_class(strict=True, age=pyoload.ge(0))
class Person:
    age: int
    def __init__(self, age: int):
        self.age = age
```

### Callbacks (`callback`)

Pass a custom hook callback to perform custom validation or cross-attribute checks:

```python
# Function callback: receives (bound_arguments, return_value)
def check_div(bound, ret):
    if bound.arguments.get("b") == 0:
        return "division by zero"

@pyoload(callback=check_div)
def divide(a: float, b: float) -> float:
    return a / b

# Class callback: receives (instance, attr_name, new_value)
def check_range(instance, name, val):
    if instance.min_val > instance.max_val:
        return "min_val cannot exceed max_val"

@pyoload(callback=check_range)
class Range:
    min_val: int
    max_val: int
```

---

## Utility & Validator Helpers

- `pyoload.is_valid(val, spec)` — Returns `True` if `val` matches `spec`, `False` otherwise.
- `pyoload.gt(n)` / `pyoload.ge(n)` — Value must be greater than / greater or equal to `n`.
- `pyoload.lt(n)` / `pyoload.le(n)` — Value must be less than / less or equal to `n`.
- `pyoload.positive` / `pyoload.negative` / `pyoload.non_zero` — Numeric constraints.
- `pyoload.finite` — Value must be a finite float (not NaN or Inf).
- `pyoload.non_empty` — Value must not be empty.
- `pyoload.regex(pattern)` — String value must match regex pattern.
- `pyoload.predicate(fn, message)` — Custom boolean predicate.