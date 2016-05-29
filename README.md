# Obin programming language

Obin is a small unpure functional programming language with immutable datastructures.
It exists currently only as prototype written in python and i dont plane to develop it further.

## Currently implemented features
* Modern expressive functional syntax which resembles something between Erlang and F#.
* Handwritten, extensible operator precedence parser with support of indentation layouts and juxtaposition operator
* Module system as a cross between Python, Haskell and Lua
* Polymorphism engine similar to Clojure protocols but with possibility to dispatch not only on first argument
* Automatic carrying with simple push and pop model
* Stackless stack based virtual machine
* Persistant data structures (lists, vectors, maps), shamelessly stolen from [Pixie](https://github.com/pixie-lang/pixie). 
* Pattern matching, let-in blocks, clojures, try-catch-finally, abstract data types
* Assymetric coroutines
 

Syntax example
```
fun foldr func accumulator coll
    | f acc [] -> acc
    | f acc hd::tl -> f hd (foldr f acc tl)

type Maybe
    | Nothing
    | Just v
    
type Point2 x y

type Vec2 p1 p2

trait Add for self
    def add self a

implement Add for Point2
    def add self other
        | _ p2 of Point2 -> Point2 (self.x + p2.x) (self.y + p2.y)
        | _ i of Int -> Point2 (self.x + i) (self.y + i)
        | _ v of Vec2 -> add (Vec2 self self) v

implement Eq for Point2
    def == self other of Point2 ->
            self.x == other.x and self.y == other.y
    def != self other of Point2 -> not (self == other)

```

## Known problems
* Error reporting is very bad, it does more harm than good now
* Obin has problem with prefix operator - 
    For example if you type
    io:print -1 it will be interpreted as sexpr (- io:print 1) you need to type
    io:print (-1) instead
* Custom operators can be created but they will be exported only from prelude, if declared in other module they will remain local
* lack of macrosses
  
Obin scripts are placed in test/obin
* \_\_lib__ folder contains stdlib
* tests folder contains testing scripts
* 
Some code (big enums, repeating blocks) generated in manual mode from scripts in obin_py/generators, but using them are not necessary.
To run interpreter
```
cd obin_py 
python  targetobin.py test/obin/main.obn
```
Program will run painfully slowly with stock python so I recomend using pypy instead
You may need pypy toolchain in the path see ```obin_py/runobin.sh``` for details.
Obin does not compiles with RPython, but it can be done with some effort.


Obin may not have any practical interest but it may be usefull for people who begin to study compilers and virtual machines
Project split into two folders obin_c and obin_py. Folder obin_c is obsolete, I keep it with hope of return to the project at some time.


I abandon project because of
1. Such language (immutable and functional aka Erlang) needs large ecosystem and well suited for complicated parallel programming but I plan it as a small embeddable language, so I don't have confidence now that i am designing something usefull
2. Automatic carrying is very error prone in dynamic languages, but without it syntax with juxtaposition has little sense
3. I understand that minimal and expressive syntax are also terse and very hard to read with screen readers and accesibility is very important for me.
4. I want to experiment with type systems and may be switch to another language
