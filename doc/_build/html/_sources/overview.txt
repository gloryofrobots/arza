Overview
========

Arza is an experimental eager functional programming language
with dynamic type system supporting multiple dispatch and immutable data out of the box.

It can be described like Erlang with a lot of syntactic sugar and some new ideas.

Currently it exists only as a prototype written in Python.

I am considering either to add RPython jit generation or to rewrite full interpreter in C.


Most prominent features of arza
-------------------------------

* Laconic whitespace aware syntax inspired by F#, Python with posibility to write code in Lisp style
* Immutable data structures (lists, tuples, maps)
* Pattern matching
* Lexical clojures and lambdas
* Usual number of primitives (if-else, let-in, try-catch)
* User defined operators
* User defined abstract and struct types
* Nominal subtyping
* Multiple dispatch generic functions
* Interfaces supporting multiple dispatch paradigm
* Traits as functions operating on types
* Special syntax for partial application
* Stackless virtual machine
* Asymmetric coroutines
* Symmetric coroutines aka processes 
* Decorators for functions, types and generic specialisations
* Special syntax for modifiing deeply nested immutable structures
* Special support for creating links to parts of immutable structures aka lenses


What is missing for now
-----------------------

* Standart library, currently Arza have only some functions for sequence manipulation
* Tail call optimisation. Interpreter is stackless and it is currently very slow to work with,
  so I decided against compiler complication for now
* No REPL. Interpreter works only with files
* No macroses. I have not decided yet if I want them in the language at all


What are the biggest problems
-----------------------------

* Interpreter is so slow it is painfull to work with.
* Error reporting in some places is very bad
* Language design is still unstable


How to run
----------

::
   
   python targetarza.py program.arza


**However it is much better to use PyPy**

Examples
--------

Examples and tests could be found in :code:`ROOTDIR/test/arza` folder.

Entry point for test suite is :code:`ROOTDIR/test/arza/main.arza`


