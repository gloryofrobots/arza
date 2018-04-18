# Arza programming language

Arza is an experimental programming language supporting multiple dispatch and immutable data out of the box.
This is a prototype built in relatively 'slow' language python and is not ready for productin in any way.

## To run 
```
python targetarza.py test/arza/main.arza
```
or better use pypy

Currently, compilation via RPython toolchain not supported but it can be done with some effort.
There are no working REPL at the moment

## Features

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
* Asymmetric and symetric coroutines
* Symmetric coroutines aka processes 
* Decorators for functions, types and generic specialisations
* Special syntax for modifiing deeply nested immutable structures
* Special support for creating links to parts of immutable structures aka lenses


To learn more you can read documentation