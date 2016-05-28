# Obin programming languate

Obin is a small unpure functional programming language with immutable datastructures.
It exists currently only as prototype written in python and i dont plane to develop it further.

## Currently implemented features
* modern expressive functional syntax which resembles something between Erlang and F#.
  for example foldr
    fun foldr func accumulator coll
	| f acc [] -> acc
	| f acc hd::tl -> f hd (foldr f acc tl)

* handwritten, extensible operator precedence parser with support of indentation layouts and juxtaposition operator
* pattern matching at the language core
* module system as a cross between Python, Haskell and Lua
* polymorphism engine similar to Clojure protocols but with possibility to dispatch not only on first argument
* automatic carrying with simple push and pop model
* stackless stack based virtual machine
* persistant data structures, shamelesly stolen from [Pixie](https://github.com/pixie-lang/pixie) lists, vectors, maps
* pattern matching, let-in blocks, clojures, try-catch-finally, abstract data types
* assymetric coroutines

## Known problems
* Error reporting is very bad, it do more harm than good now
* Obin has problem with prefix operator - 
    For example if you type
    io:print -1 it will be interpreted as sexpr (- io:print 1) you need to type
    io:print (-1) instead
* Custom operators can be created but they will be exported only from prelude.
  If declared in other module they will remain local
* lack of macros, I just don't have time for them
  
Obin scripts are placed in test/obin
* __lib__ folder contains stdlib
* tests folder contains testing scripts

Obin may not have any practical interest but it may be usefull for people who study compilers and virtual machines
Project split into two folders obin_c and obin_py. Folder obin_c is obsolete

To run interpreter
cd obin_py 
python  targetobin.py test/obin/main.obn
but it will run painfully slowly with stock python so are use pypy most of the time
Obin does not compiles with RPython, but it can be done with some effort.

I abandon project because of
1. Such language (immutable and functional aka Erlang) needs large ecosystem and well suited for complicated parallel programming
   but I plan it as a small embeddable language, so I don't have confidence now that i am designing a good thing
2. Automatic carrying is very error prone in dynamic languages, but without it lightweiht juxtaposition driven syntax has little sense
3. I understand that minimal and expressive syntax are also terse and very hard to read with screen readers and accesibility is very important for me.
4. I want to experiment with type systems and may be create another language later
