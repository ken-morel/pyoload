==================================================
What's new
==================================================

Lot's have been done since I started the project
to when I write this doc now, about

.. image:: https://wakatime.com/badge/user/dbe5b692-a03c-4ea8-b663-a3e6438148b6/project/ab01ce70-02f0-4c96-9912-bafa41a0aa54.svg


These are the highlights

--------------------------------------------------
pyoload v2.0.0
--------------------------------------------------

1. Greatly worked on the docs to make them more undetsandable and increase coverage.
2. Renamed overload to multiple dispatch or multimethod as required, since
   As from :ref:`Overload or multimethod`.
3. Added new options to :ref:`pyoload.Checks` such as registerring under multiple names.
4. Increased the pytest coverage to ensure the full functionality of `pyoload`
   on the several supported python versions.
5. Greatly improved performance using `inspect.Signature`. Providing support
   for partial annotating of function.(Yes, from v2.0.0 some annotations may be ommited).
6. Added helper methods for interacting with annotated functions,
   They include

   - :ref:`pyoload.annotable`
   - :ref:`pyoload.unannotable`
   - :ref:`pyoload.is_annotable`
   - :ref:`pyoload.is_annotated`

   Those methods will help you prevent some functions from being annotated.

7. Improved support for python 3.9 and 3.10
8. renamed functions as the previous `pyoload.typeMatch` to :ref:`pyoload.type_match` to follow
   the snake case system of nomenclature.
9. :ref:`pyoload.type_match` returns a tuple of the matchin status and errors
   which may have lead to type mismatch, thosse errors are added to traceback
   to ease debugging.
10. Now most classes implement `__slots__` to improve memory size.
