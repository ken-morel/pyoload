==================================================
usage
==================================================

--------------------------------------------------
:python:`pyoload.annotate()`
--------------------------------------------------

It is a simple decorator.

.. code-block:: python

  from pyoload import *

  @annotate
  def foo(arg1: typ1, ...) -> RetType:
      ...

- The return type is optional.
- The parameter annotations must be specified.
- It raises a :python:`pyoload.AnnotationError` when type mismatch

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:python:`.__pyod_annotate__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The raw function which was annotated.

--------------------------------------------------
:python:`pyoload.overload`
--------------------------------------------------

It is another decorator

It accepts all the arguments of annotate.

The return function support these arguments:

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:python:`.__pyod_annotate__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The raw function which was annotated.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:python:`.__pyod_overloads__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The list of the annotated overloads of the function

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
:python:`.__pyod_overloads_name__`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The dictionary key under which the overloads was registered.

--------------------------------------------------
:python:`pyoload.Cast(Type)`
--------------------------------------------------

It receives a type as argument, it is the type
in which the object will cast.

>>> from pyoload import Cast
>>> caster = Cast(dict[str, list[tuple[float]]])
>>> object = {237: (['1.0', 5], (5.0, 6.0))}
>>> caster(object
){'237': [(1.0, 5.0), (5.0, 6.0)]}
