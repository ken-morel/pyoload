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
.. image:: https://img.shields.io/badge/stackoverflow-Ask%20questions-blue.svg
  :target: https://stackoverflow.com/questions/tagged/pyoload
.. image:: https://readthedocs.org/projects/pyoload/badge/?version=latest
    :target: https://pyoload.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

=======
pyoload
=======

pyoload has two main functions

----------------
pyoload.annotate
----------------

Is used as a decorator on the function.

.. code-block:: python

  from pyoload import annotate
  @annotate
  def twice(a:int) -> int:
      return a * 2
  b = twice(4)

The annotate creates a wrapper over the decorated function which checks in for argument types over each function call using :python:`pyoload.matchType(val, spec)`.
The original function is kept in the :python:`.__pyod_annotate__` attribute.

----------------
pyoload.overload
----------------

Implements function overloading in python via a simple decorator

.. code-block:: python

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


When an overload is registerred, the function name in the form `functionModuleName.functionQualName` is goten using `pyoload.get_name(funcOrClass)` an annotate is gotten using `pyoload.annotate(func, True)`
and a new list of overloads is created and stored in `pyoload.__overloads__` dictionarry under it's name. A reference to the list of annotated overloads is stored in the functions `.__pyod_overloads__`.

When the function is called, the wrapper tries all the functions registerred to that name to catch a `pyoload.InternalAnnotationError`. If none ran succesfully, it raises an `pyoload.OverloadError`.

-------
Casting
-------

All `pyoload.annotate` and `pyoload.overload` both support Cast objects
instances of `pyoloas.Cast`.
It uses recursive casting with integrated support for dictionaries, e.g:
:python:`dict[int,tuple[list[float] | float]]`
for a dictionarry mapping of integers to list of floats or floats.

.. note::
  When a union, e.g `int | str` is passed to Cast, it tries to cast in each of
  the specified types in the listed order, that is

  ```python
  cast = pyoload.Cast(int|str)
  print(repr(cast(3i)))
  ```

  Will print `'3i'` as `3i` can not be converted to a complex

--------------------
Accepted annotations
--------------------

In addition to supporting normal plain types,
pyoload includes support for generic aliasses of iterable types and some other classes:

- :python:`pyoload.Values(iterable)`
  e.g `Values("+-*/")` or `Values(range(6))`
- :python:`pyoload.Cast(type)`
  Instructs pyoload to cast to the specified type
- A string
  The string contents will be evaluated as soon as first function call.


.. role:: python
  :language: python
  :syntax: python
