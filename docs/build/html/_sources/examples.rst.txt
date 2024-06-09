==================================================
examples
==================================================

-------------------------------------------------------------------------------
Person address (:python:`pyoload.Cast`, :python:`pyoload.CheckedAttr`)
-------------------------------------------------------------------------------
.. code-block:: python

  from pyoload import *
  class Person:
      name = CheckedAttr(len=3)
      phone = CastedAttr(tuple[int])
      def __init__(self, name, phone):
          self.name = name
          self.phone = phone


>>> temeze = Person('17R', "678936798")
>>>
>>> print(temeze.age)  # 17
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Person' object has no attribute 'age'
>>> print(temeze.phone)  # (6, 7, 8, 9, 3, 6, 7, 9, 8)
(6, 7, 8, 9, 3, 6, 7, 9, 8)
>>>
>>> mballa = Person(0, "123456")
Traceback (most recent call last):
  ...
TypeError: object of type 'int' has no len()





--------------------------------------------------
Adding examples
--------------------------------------------------

Thinking of better, more realistic or more practical examples which you may
want to retail, will be happy to add it, report it as an issue please.

:ref:`report`
