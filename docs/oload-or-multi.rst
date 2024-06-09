==================================================
Overload or multimethod?, Overloading or multiple dispatching
==================================================

We see many people like me confuse between the two or did not know the second
one, but what the difference?

--------------------------------------------------
Overloading
--------------------------------------------------

Overloading is a feature available in multiple statically typed programing
languages as C++ and Java where the function definition to be used is inferred
from the argument types **During Compilation** and not during runtime.

The compiler knows what function to call since it knows what type of arguments
are passed.

--------------------------------------------------
Multiple dispatching
--------------------------------------------------

This is a feature available though in some languages as C#, Common Lisp and cecil.

Here during runtime the correct definition to be used is inferred from
evaluating the current types of the passed arguments and/or their number.
See https://en.wikipedia.org/wiki/Multiple_dispatch
