.. image:: https://github.com/ken-morel/pyoload/actions/workflows/python-publish.yml/badge.svg
  :alt: Release status
  :target: https://github.com/ken-morel/pyoload/releases
.. image:: https://badge.fury.io/py/pyoload.svg
  :alt: PyPI package
  :target: https://pypi.org/project/pyoload
.. image:: https://img.shields.io/pypi/pyversions/pyoload
  :alt: Supported Python versions
  :target: https://pypi.org/project/pyoload
.. image:: https://github.com/ken-morel/pyoload/actions/workflows/test.yml/badge.svg?branch=main
  :alt: Build Status
  :target: https://github.com/ken-morel/pyoload/tree/mai
.. image:: https://coveralls.io/repos/github/ken-morel/pyoload/badge.svg?branch=main
  :alt: Coverage Status
  :target: https://coveralls.io/github/ken-morel/pyoload?branch=mai
.. image:: https://readthedocs.org/projects/pyoload/badge/?version=latest
  :target: https://pyoload.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

==================================================
pyoload
==================================================

`pyoload` provides an intuitive and easy way to add type and value checking
to function arguments and class attributes.

--------------------------------------------------
usage
--------------------------------------------------

`pyoload` base provides two simple use functions

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`pyoload.annotate`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`pyoload.annotate` used as a decorator over a simple function
it returns a wrapper function which on each call

- get the function's annotations
- resolve the annotations if stringified, on error raises a `pyoload.AnnotationResolutionError`
- check for matches between the passed arguments and annotations with the recursive `pyoload.typeMatch` function
- if all matches, then calls the function, else raises a `pyoload.AnnotationError`
- if the return annotation specified then returns it else raises an annotation error.

Example

>>> from pyoload import *
>>> from pathlib import Path
>>> @annotate
... def add_eof(eof: str, file: Cast(Path)) -> int:
...     '''
...     :param eof: the string to append
...     :param file: the file to add content to
...     :returns: the new file size
...     '''
...     data = file.read_text()
...     return file.write_text(data + eof)
...
>>> print(add_eof)
<function add_eof at 0x017B2D48>
>>> print(add_eof.__pyod_annotate__)
<function add_eof at 0x0109D7F8>
>>> print(add_eof('@EOF@', 'del.txt'))
17


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
`pyoload.overload`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`pyoload.overload` used as a decorator over a simple function
When decorating a function it:

- annotates the function with the special kwarg `is_overload=True`
- gets the function's name using `pyoload.get_name` and if needed creates a new register dictionarry value in `pyoload.__overloads__[name]` and stores a copy in the function's `.__pyod_overloads__`

And on each call it simply loops through each function entry, while
it catches a `pyoload.InternalAnnotationError` which is raised when
the special `is_overload` is set to true

.. tip::

  you may raise `pyoload.InternalAnnotationError` inside an overloaded
  function after carrying out some other checks and pyoload will switch to the
  next oveload.

>>> from pyoload import *
>>> from pathlib import Path
>>> @overload
... def div(a: float|int, b: Checks(eq=0)):
...     raise ZeroDivisionError()
...
checks={'eq': 0}
>>> @overload
... def div(a: int, b: int) -> int:
...     return a // b
...
>>> @overload
... def div(a: float, b: float) -> float:
...     return a / b
...
>>> @overload
... def div(a: Any, b: Any):
...     raise NotImplementedError()
...
>>> print(div.__pyo_overloads__)
[<function div at 0x019C2D48>, <function div at 0x01B5EE38>, <function div at 0x01B65E88>, <function div at 0x01B65F78>]
>>> print(div.__pyod_overloads_name__)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'function' object has no attribute '__pyod_overloads_name__'. Did you mean: '__pyo_overloads_name__'?
>>> print(repr(div(1, 2)))
2
{'eq': 0} 2
<class 'pyoload.Check'> eq 0 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 399, in wrapper
    val = f(*args, **kw)
          ^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 348, in wrapper
    if not typeMatch(v, anno[k]):
           ^^^^^^^^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 225, in typeMatch
    spec(val)
  File "C:\pyoload\src\pyoload\__init__.py", line 146, in __call__
    Check.check(name, params, val)
  File "C:\pyoload\src\pyoload\__init__.py", line 72, in check
    raise Check.CheckDoesNotExistError(name)
pyoload.Check.CheckDoesNotExistError: eq
>>> print(repr(div(1.0, 2.0)))
2.0
{'eq': 0} 2.0
<class 'pyoload.Check'> eq 0 2.0
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 399, in wrapper
    val = f(*args, **kw)
          ^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 348, in wrapper
    if not typeMatch(v, anno[k]):
           ^^^^^^^^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 225, in typeMatch
    spec(val)
  File "C:\pyoload\src\pyoload\__init__.py", line 146, in __call__
    Check.check(name, params, val)
  File "C:\pyoload\src\pyoload\__init__.py", line 72, in check
    raise Check.CheckDoesNotExistError(name)
pyoload.Check.CheckDoesNotExistError: eq
>>> print(repr(div(1.0, 2)))
2
{'eq': 0} 2
<class 'pyoload.Check'> eq 0 2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 399, in wrapper
    val = f(*args, **kw)
          ^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 348, in wrapper
    if not typeMatch(v, anno[k]):
           ^^^^^^^^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 225, in typeMatch
    spec(val)
  File "C:\pyoload\src\pyoload\__init__.py", line 146, in __call__
    Check.check(name, params, val)
  File "C:\pyoload\src\pyoload\__init__.py", line 72, in check
    raise Check.CheckDoesNotExistError(name)
pyoload.Check.CheckDoesNotExistError: eq
>>> print(repr(div('0', 0)))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 399, in wrapper
    val = f(*args, **kw)
          ^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 360, in wrapper
    ret = func(**vals)
          ^^^^^^^^^^^^
  File "<stdin>", line 3, in div
NotImplementedError
>>> print(repr(div('0', 1j)))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 399, in wrapper
    val = f(*args, **kw)
          ^^^^^^^^^^^^^^
  File "C:\pyoload\src\pyoload\__init__.py", line 360, in wrapper
    ret = func(**vals)
          ^^^^^^^^^^^^
  File "<stdin>", line 3, in div
NotImplementedError
