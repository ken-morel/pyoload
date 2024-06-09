
Welcome to pyoload v |version| documentation!
===================================

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
  :target: https://coveralls.io/github/ken-morel/pyoload?branch=main
.. image:: https://readthedocs.org/projects/pyoload/badge/?version=latest
  :target: https://pyoload.readthedocs.io
  :alt: Documentation Status
.. image:: https://img.shields.io/pypi/dd/pyoload
  :target: https://pypi.org/project/pyoload
  :alt: Pypi downloads
.. image:: https://ken-morel-api.up.railway.app/counters/pyoload-docs/add.svg
  :target: https://portfolio-ken-morel-projects.vercel.app/
  :alt: Hit count

Hy pythonista, here is `pyoload`, what is?

  A python module to integrate function arguments typechecking, and multiple
  dispatching in python.

It uses the beauty and ease of use of decorators and python scopes to provide
an easy to use tool. here some quick examples.

.. code-block:: python

    source

    python
    from pyoload import *

    @annotate
    def greater_than(a: int | float, b: int | float) -> bool:
        return a > b

    @multimethod
    def foo(a, b=3, c: int = 5):
        ...

    @multimethod
    def foo(a: int, b: Cast(str)):
        ...

    @multimethod
    def foo(a) -> Cast(str):
        return repr(a)

  foo(4)


You could look at the title lower for more documentation.

.. toctree::
  :maxdepth: 1

  examples
  usage
  api
  installation
  whatsnew
  report
  genindex
  modindex
  oload-or-multi
