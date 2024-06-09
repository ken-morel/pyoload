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


--------------------------------------------------
annotables and unnanotables
--------------------------------------------------

Not wanting a specific function be annotated?, :ref:`pyoload.annotable` and
:ref:`pyoload.unannotable` will mark your function with a special attribute which
will prevent :ref:`pyoload.annotate` from having effect on them, and to return
the empty functions.

`pyoload.is_annotable` is the function used by pyoload to check for the
unnanotable marks paused by :ref:`pyoload.unannotable`

.. note::

  The functions marked py :ref:`pyoload.unannotable` could still be annotated
  if the :py:`force=True` argument specified.

--------------------------------------------------
Checks
--------------------------------------------------

`pyoload` provides this method for writing your own checks and use them
anywhere in your code.

##################################################
howto? classes
##################################################

to register a class as a check, simply subclass :ref:`pyoload.Check`,
The class will be instantiated, and it's instances should be callables.
- The name of the check will be taken from the instances `.name` attribute
  or the classes name if the `.name` attribute not present.
- The class instance will then be used as a function and called with the value
  as argument.

.. note::

  If the `.name` attribute is not implemented and the classes name is used.
  **the class name is not lowercased**


.. code-block:: python

  from pyoload import *

  class MyCheck(Check):
      count = 0
      def __call__(self, param, value):
          MyCheck.count += 1
          assert MyCheck.count > value

  @annotate
  def foo(a: Checks(MyCheck=0)):
      return True

>>> foo(1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 726, in wrapper
    raise AnnotationErrors(errors)
pyoload.AnnotationErrors: [AnnotationError("Value: 1 does not match annotation: <Checks(MyCheck=0)> for argument 'a' of function __main__.foo")]
>>> foo(1)
True
>>> foo(2)
True
>>> foo(4)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\pyoload\src\pyoload\__init__.py", line 726, in wrapper
    raise AnnotationErrors(errors)
pyoload.AnnotationErrors: [AnnotationError("Value: 4 does not match annotation: <Checks(MyCheck=0)> for argument 'a' of function __main__.foo")]
>>> MyCheck.count
4

##################################################
howto? functions
##################################################

Functions are registered with the implicit :py:`Check.register`,
here the same logic as above

.. code-block:: python

  from pyoload import *

  count = 0
  @Check.register('MyCheck')
  def _(param, val):
      global count; count += 1
      assert count > val
