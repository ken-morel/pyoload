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
.. image:: https://img.shields.io/pypi/dm/pyoload
  :alt: downloads
==================================================
pyoload
==================================================

`pyoload` provides an intuitive and easy way to add type and value checking
to function arguments and class attributes.

view `readthedocs <https://pyoload.readthedocs.io>`_ for an extended documentation

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

```python
from pyoload import *
from pathlib import Path
@annotate
def add_eof(eof: str, file: Cast(Path)) -> int:
    '''
    :param eof: the string to append
    :param file: the file to add content to
    :returns: the new file size
    '''
    data = file.read_text()
    return file.write_text(data + eof)

print(add_eof)
# <function add_eof at 0x017B2D48>
print(add_eof.__pyod_annotate__)
# <function add_eof at 0x0109D7F8>
print(add_eof('@EOF@', 'del.txt'))
# 17


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
