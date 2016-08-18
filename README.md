# Lalan programming language

This repository contains prototype for experimental dynamically typed functional language

## Goal

To experiment with syntax and stackless virtual machine.
It is not a production system.
Lalan written in relatively 'slow' language python with not many speed optimisations.

Running interpeter
```
python targetlalan.py test/lalan/main.lal
```
or better use pypy

Currently, compilation via RPython toolchain does not supported but it can be done with some efforts.
There are no REPL for lalan at the moment

## Features

* Original and clean syntax inspired by Lua and OCaml
* Persistent data structures (lists, tuples, maps)
* Pattern matching
* Lexical clojures and lambdas
* Usual number of primitives (if-else, let-in, try-catch)
* User defined operators
* User defined types
* Traits and interfaces
* Single dispatch generic functions
* Special syntax and custom operator for partial application
* Stackless virtual machine
* Asymmetric coroutines

## TODO

* Macros
* REPL
* Tail call optimisations
* Total speed optimisations
* Production ready C++ version

## Guide

- [Syntax](#syntax)
- [Predefined types and literals](#predefined-types-and-literals)
- [Data structures](#data-structures)
- [Immutability](#immutability)
- [Functions](#functions)
- [Partial application](#partial-application)
- [Operators](#operators)
- [Expressions](#expressions)
  - [if-elif-else](#if-elif-else)
  - [match-with](#match-with)
  - [let-in](#let-in)
  - [try-catch-finally-throw](#try-catch-finally-throw)
- [Types](#types)
- [Single dispatch](#single-dispatch)
  - [Generics](#generics)
  - [Interfaces](#interfaces)
  - [Extend type](#extend)
  - [Traits](#traits)
- [Modules and bootstrap](#modules-and-bootstrap)
  - [Loading order](#loading-order)
  - [Import and export](#import-and-export)


### Syntax

Lalan uses original syntax inspired by Lua and OCaml
Expression syntax similar to convenient scripting languages with infix and prefix operators and
function calls via ```f(...)```. But instead of using some kind of block separators ({} or begin end)
Lalan allows one or more expressions inside parens (exp1 exp2 expe).
Result of such group expression will be the result of last expression.
This simple rule provides organic coexistence of serial and single expressions.
```
fun add(x,y) = x + y
fun add_and_print(x,y) =
(
    io:print("x + y", x + y)
    x + y
)
```

Name binding can be done only inside *let-in* statement, I believe it pushes programmer to good code quality
```
fun f(x,y) =
    let z = x + y
    in z + x + y

// series of expressions inside let and in

fun f(x,y) =
    let
        z = x + y
        w = read_from_file()
    in
    (
        io:print("z and w", z, w)
        let k = w / z
        in k + x + y
    )
```
Most of the functions can be written with such *let-in* technique

There are three main kinds of expressions
* Top level expressions (import, export, from, fun, let, trait, interface, generic, type, prefix, infixl, infixr)
* Pattern matching expressions inside function signature, after let expression or in match expression
* Value expressions usually occur after = token and always evaluates to some value

There are no end of expression token in Lalan.
Parser grabs expressions one by one from stream of tokens.
Every expression terminates by lack of left binding power.
This idea comes from Lua language.
```
fun f () =
(
    1 + 1  2 + 2
)
f() == 4

```
However this technique creates problem with ambidextra operators
(operator having have both prefix and infix binding powers)
Examples of such operators are *-* and *(*
To resolve parsing conflicts Lalan uses new lines as terminators
```
fun f() =
(
    //lambda expression
    ((x, y) = x + y)
    // parser treats `(` as prefix expression because of new line
    (1, 41)
)
f() == (1, 41)

fun f2() =
(
    // parser treats `(` as infix expression and interprets this expression as call to lambda with arguments (1, 41)
    ((x, y) = x + y)(1, 41)
)
f2() == 42
```

#### Import and export

```
// this is comment
// By default all names except operators can be imported outside
// You can limit it with export expression
let CONST = 41
fun f_ab () = CONST + 1
fun f_ab_2 = f_ab()

export (f_ab, f_ab_2, CONST)

// to import module use it's name relative to program.lal with / replaced by :
// to import modules from __std__ directory simply use their name

import seq
import io

// Afterwards, all exported names from this modules available as qualified names
let _ = io:print(seq:reverse([1,2,4,5]))

// import other module

import my:modules:module1

// only last part of module identifier used as qualifier

let three = module1:add(1, 2)

// use aliases to resolve name conflicts

import my:modules:module1 as mod1
import my:module1 as mod1_1

let x = mod1:add(mod1_1:add(1, 2), 3)

// import only required qualified names
import my:module1 (f1 as f1_1, f2 as f2_1)
let _ = module1:f1_1()
let _ = module1:f2_1()

import my:modules:module1 as mod1 (f1, f2)
let _ = mod1:f1()
let _ = mod1:f2()

import my:module1 as mod1 (f1 as f1_1, f2 as f2_1)
let _ = mod1:f1_1()
let _ = mod1:f2_1()

// hiding names
import my:modules:module1  hiding (CONST)
let _ = module1:f1()
let _ = module1:f2()

import my:modules:module1 as mod1 hiding (f1)
let _ = mod1:f2()
let _ = mod1:CONST

import tests:lib_az:abc:module_ab as ab5 hiding (f_ab, CONST)

/// UNQUALIFIED IMPORT
// import specified unqualified names
from my:modules:module1  import (f1, f2, CONST as const)
let _ = f1()
let x = f2() + const

// import all unqualified names from module

from my:modules:module1 import _

// hiding specific names
from my:modules:module1 hide (CONST)
let x = f1() * f2()
```

#### Operators

```
// real code from prelude.lal
// operators noted in comments defined internally for special treatment
// operator_type(operator_symbol, function_name, binding_power)

infixr (:=, :=, 10)
// infix @ as of -> 15
infixl (<|, <|, 15)
infixl (|>, |>, 20)
// infix or -> 25
infixl (<<, <<, 25)
infixl (>>, >>, 25)
// infix and -> 30
infixl (<, <, 35)
infixl (>, >, 35)
infixl (>=, >=, 35)
infixl (<=, <=, 35)
infixl (==, ==, 35)
infixl (!=, !=, 35)
infixl (++, ++, 40)
infixl (+, +, 40)
infixl (-, -, 40)
infixl (*, *, 50)
infixl (/, /, 50)
prefix (-, negate, 55)
// infix :: -> 60
infixl (**, **, 60)
// prefix # -> 70
prefix (!, !, 70)
infixl (.., .., 95)
// infix ( .( .{ .[ -> 95
prefix (&, &, 96)
// infix . : -> 100

// when parser transforms expressions with operators to call expressions
2 - 2 -> -(2, 2)
-2 -> negate(2)

// to use operator as prefix function put it between ``
// foldr(`+`, l2, l1)
// to use function as infix operator put it between `` too
// 4 `mod` 2 = 0

// Operators defined in prelude.lal are global to all modules and environments
// Operators defined in other module are local to this module and can't be exported
```
#### Module let expression
In Lalan *let* is the only way to bind name to variable.
But except for that let expression actually performs pattern matching
Value can be bind to name only once.
Top level let expression is different from let-in expression allowed in value expressions
```
// grammar
// let <pattern> = <value_expression>
// let `(` {<pattern> = <value_expression>} `)`

// single expression
let x = 1
//error here
let x = 2
// no error, x already 1
let x = 1
// using any possible pattern
let _ = f()
let () = io:print(42)
let x::xs = [1,2,3,4,5]

// group expression

let
(
    x = 1
    _ = f()
    () = io:print(42)
    x::xs = [1,2,3,4,5]
)
```

#### Function expression
```
//simple function
fun <name> `(`{arg_pattern}`)` [ when  <value_expression>]= <value_expression> |

// case function with multiple signatures
fun <name>
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <value_expression>}

// compound single - case function, see below for explanation
fun <name> `(`{arg_pattern}`)`
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <value_expression>}


// Function expression in lalan have three forms
//
// Simple
fun <name> `(`[arg_pattern]`)` [ when  <value_expression>]= <value_expression> |

fun any(p, l) =
    disjunction(map(p, l))

fun all(p, l) =
    conjunction(map(p, l))

fun print_2_if_greater(val1, val2) when val1 > val2 =
(
    io:print("first", val1)
    io:print("second", val2)
)

// Case function with multiple clauses. All clauses required to have the same arity.

fun <name>
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <value_expression>}

// Examples
fun foldl
    | (f, acc, []) = acc
    | (f, acc, hd::tl) = foldl(f, f(hd, acc), tl)

// if after | token there are only one argument and it is not tuple enclosing parentheses might be omitted
fun to_str
    | 0 = "zero"
    | 1 = "one"
    | 2 = "two"
    // tuples must be enclosed anyway
    | (()) = "empty tuple"



// Recursive two level function
// This kind of function allows to check argument types or other conditions only at first step of recursion

fun <name> `(`{arg_pattern}`)`
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <value_expression>}


// this function transforms in compile time to
fun <name> `(`{arg_pattern}`)` =
    let
        // inner case - function
        fun <name>
            {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <value_expression>}
    in
        // call inner function with outer function arguments
        <name>`(`{arg_pattern}`)`
    // inner function has the same name as outer, so if inner is recursive it can't call outer
// initial arguments of outer function visible through entire recursive process

// Example
fun scanl(func, accumulator, coll)
    | (f, acc, []) = acc :: empty(coll)
    | (f, acc, hd::tl) = acc :: scanl(f, f(hd, acc), tl)

// Compiles into
fun scanl(func, accumulator, coll) =
    let
        fun scanl
            | (f, acc, []) = acc :: empty(coll) // coll contains initial value from first call
            | (f, acc, hd::tl) = acc :: scanl(f, f(hd, acc), tl)
    in scanl(func, accumulator, coll)

```

#### Type expression
```
type <name> {field `,`} |
type ( {<name> {field `,`}} )

type Name
// Fieldless singleton type
type Nothing
// Constructor type
type Point(x, y)

//group expression
type
(
    Point (x, y)
    Square(width, height)
    Rect(left, top, right, bottom)
)

// creating type instances
let p = Point(24.5, 25.7)
let r = Rect(p, Point(12, 34), Point(34, 54), Point(31, 12))

let True = p `kindof` Point
let True = p `kindof` Shape
let False = p `kindof` Square
let True = p.x `kindof` Float


// type instances inside match expression or function clauses
match p with
 | (x, y) of Point = x + y // as tuple
 | (left, top, right, bottom) of Rect = left.x + right.y // . operator can access instance field by name
 | {right, top, left, bottom} of Rect = left.x + right.y // as map

```

### Single dispatch (generic, trait, extend) expressions
Single dispatch based on protocols(interfaces, traits) became popular in many modern languages (Clojure, Elixir, Golang. Rust)
Such system usually consists of types and protocols. Protocols consists of one (zero) or more methods
Protocol (all it's methods) can be implemented for specific type. Protocol methods usually dispatch on first argument.


**Clojure example**
```
(defprotocol AProtocol
  "A doc string for AProtocol abstraction"
  (bar [a b] "bar docs")
  (baz [a] [a b] [a b c] "baz docs"))

(deftype MyType [a b c])

(extend-type MyType
  Foo
    (bar [x y] ...)
    (baz ([x] ...) ([x y zs] ...)))
```

It is simple and powerful system but it tightly bounds functions to only one protocol.
Problem occurs when some function must belong to two or more protocols simultaneously
For example, we can have protocol for collection with methods 'at' and 'elem' and protocol for
mutable collection with methods 'at' 'elem' 'put' 'del'.
Mixins or Inheritance can solve this problem but lalan goes the other way.
In lalan generic functions and protocols(interfaces) declared apart from each other
and interfaces combine one or more previously declared generics.
Type doesn't need to signal implementation of interface but needs to implement all generic functions belonging to interface
Lalan generic functions can dispatch on argument in any position


##### Generics
```
// Generic provides dispatch (single) on one of it's arguments

generic <name> '('[`]{arg_name} ')' |
generic '(' {<name> '('[`]{arg_name} ')' } ')'


// ` before argument signals position of 'dispatch' argument (argument on which type dispatch occurs)
// ` might be omitted for generic with only one argument

generic equal(`x, y)
generic negate(x)

// dispatch on last argument
generic cons(value, `seq)

// declare many generics in one layout
generic
(
    mod(`x, y)
    -(`x, y)
    +(`x, y)
    put(key, value, `self)
    at(key, `self)
    del(obj, `self)
)

```

#### Interfaces

```
interface <name> '('{generic_name} ')' |
interface '(' {<name> '(' {generic_name} ')' } ')'


// Interface combines one or more generic functions and can be used for type check in pattern matching
// generic functions must be declared at this point

interface PartialEq (==)

interface
(
    Eq (!=, ==) // shares same == generic

    Seq(first, rest)

    Ord(<, <=, >, >=, cmp, max, min)

    Str (str)

    Collection(put, at, del, elem)

    Dict(keys, values, put, at, del, elem)

    Ref(!)

    MutRef(!, :=)
)
```

#### Extend
```
extend <type>
'('
    {
        let <generic_name> = <value_expression>
        use <traitname> ['(' {generic_name} ')'] |
        def <generic> <function_definition>
    }
')'


// extend type with generic function

type MyList(l)

extend L
(
    def +(self, other)
        | (self, other of List) = MyList(self.l + other)
        | (self, other of MyList) = MyList(self.l + other.l)

    def len(self) = len(self.l)

    def is_empty(self) = is_empty(self.l)

    def first(self) = self

    def rest(self) = self
)

// if interfaces Seq(first, rest), Add(+) and Sized(len) exist
// we can check if type implements them

let mylist = MyList([1,2,3,4,5,6])
let _ =
    match mylist with
        | l of Seq = l
        | _ = ()

or with builtin kindof function
let (
    True = mylist `kindof` MyList
    False = mylist `kindof` Number
    True = mylist `kindof` Seq
    True = mylist `kindof` Sized
    True = mylist `kindof` Add
    True = mylist `kindof` Sub
)
```

#### Traits
Trait is code reuse unit in lalan.
They are simple maps {generic = implementation} and can be used in extend statement
to share common behaviour between different types

```
trait <name>
'('
    {
        let <generic_name> = <value_expression>
        def <generic> <function_definition>
    }
')'



generic
(
    eq(`x, y)
    ne(`x, y)
    le(`x, y)
    lt(`x, y)
    ge(`x, y)
    gt(`x, y)
)
trait Equal
(
    def eq(x, y) = not ne(x, y)
    def ne(x, y) = not eq(x, y)
)

trait Order
(
    let le = (x,y) -> cmp(x, y) != GT
    def lt(x, y) = cmp(x, y) == LT
    def ge(x, y) = cmp(x, y) != LT
    def gt(x, y) = cmp(x, y) == GT
)
extend MyList
(
    // all implementations defined in Equal trait will be attached to MyList
    use Equal

    // only le and ge will be attached to the type
    use Order (le, ge)

    // Trait is a simple map with generics as keys and implementation functions as values
    let lt = Order.[lt]
    def gt(x, y) = Order.[gt](x, y)
)

#### Value expressions

##### Basic expressions
```

fun f() =
(
    // Booleans
    True
    False

    // Integers
    1002020020202
    1
    -42

    // Floats
    2.023020323
    -0.00000001

    // String
    "I am string"

    """
    I am
    Multiline
    string
    """

    // Symbols
    #atomic_string_created_onLyOnce

    // Tuples
    () (1,) (1,2,3)

    // Lists
    [] [1] [1,2,3]
    // Lists can be created via `cons` operator ::
    1::2::3::[]

    // Maps
    {} {x=1} {x=1, y=(2,3), z=f()}

    // Nameless functions
    // Functions in value expressions are always anonymous
    // To create named function use let-in expression
    fun (x, y) =
    (
        io:print(x + y)
        z + x * y
    )

    // Lambda expressions
    (x, y, z) -> x + y + z
    // equivalent to single element tuple (x,) -> x
    x -> x
    // tuple from tuple
    ((x,y,z),) -> x + y + z

    // usage example
    seq:fold((x, y) -> x + y, 0, [1,2,3,4,5])

)



```

##### Data structure operators

Many lalan data structures borrowed from [Pixie language](https://github.com/pixie-lang/pixie).
All of predefined data structures are immutable

```
// accessing fields
// via field name
let
(
    m = {x = 1, y = 2}
    v = m.x + m.y
)
// via index
let
(
    t = (1,2,3)
    v = t.0 + t.1
)
// calculating index or field
let v = t.[0] + t.[2-1]

// same applies to lists
let
(
    l = [1,2,3]
    v = l.0 + l.1
    v1 = l.[0] + l.[2-1]
    v2 = l.[sqrt(4)]
)

// t.0 and l.[2-1] compiles into at(0, t) and  at((2-1), l)
// m.one compiles into at(#one, m)


// creating new collection from old one via .{ operator

let
(
    m = {one=1, two=2, three=-3}

    // m1 will share it's one an two fields with m
    m1 = m.{three=-3, four=4}

    M = {
        line = {
            data = [1,2,3,4],
            index = 1
        },

        id = 12
    }

    // complicated copy creation
    M1 = M.{
        line = M.line.{
            index_2 = M.line.index + 42,
            data = [4, 3, 2, 1]
        },
        id = "ID M1"
    }
    // result
    M1 = {line = {index = 1, index_2 = 43, data = [4, 3, 2, 1]}, id = "ID M1"}

    let l = [1,2,3,4,5].{0=102, 1=103, 4=105} // result [102, 103, 3, 4, 105]
    let l1 = [1,2,3,4,5].{7=7}  // runtime error because of invalid index

```



##### Partial application

```
Lalan provides special syntax for partial application via .( operator

fun sum_3(x, y, z) = x + y + z

let
(
    add_to_1 = sum_3.(1)
    add_to_3_and_4 = sum_3.(3, 4)
    v = add_to_1(1, 2)
    v = add_to_1(1)(2)
    s = add_to_3_and_4(1)
)
// Also there are two operators in prelude responsible for creating curried functions
// prefix
fun &(func) = obin:lang:defpartial(func)
// infix
fun ..(f, g) = obin:lang:defpartial(f)(g)
let
(
   n = seq:map(&`+`(2), [1,2,3])
   // n = [3, 4, 5]
    add_to_1 = sum_3 .. 1
    add_to_3_and_4 = sum_3 .. 3 .. 4

)

// combined with pipe and composition operators currying might be extremely useful
fun |>(x, f) = f(x)
fun <|(f, x) = f(x)
fun >>(f, g) = x -> g(f(x))
fun <<(f, g) = x -> f(g(x))

fun twice(f) = f >> f
fun flip (f, x, y) = f(y, x)

let
(

    l = list:range(0, 10)
    square = (x -> x * x)
    triple = `*` .. 3

    // various ways to create curried functions
    l1 =
        l |> seq:filter.(even)
          |> seq:map.(`+` .. 1)
          |> seq:map.(flip .. `-` .. 2)
          |> seq:map.(triple >> square),

    // with function composition
    l1 = (seq:filter.(even)
             >> seq:map.(`+`.(1))
             >> seq:map.(flip.(`-`,2))
             >> seq:map.(triple >> square))(l),
    l1 =
        l |> seq:filter.(even)
          >> &seq:map(`+` .. 1)
          >> seq:map.(flip.(`-`, 2))
          >> &seq:map(triple >> square)

    // l1 = [9, 9, 81, 225, 441]
)
```

##### if-elif-else

```
// If condition must have else branch and might have zero or many elif branches
// if one of the branches succeeds result of it's last expression will be result of entire if expression

if <value_expression> then <value_expression>
[{elif <value_expression> then <value_expression>}]
else <value_expression>

fun f() =
    // si
    if something() then anything()
    elif something_else() == True then
    // series of expressions inside ()
    // equivalent to {} in C or Java
    (
        io:print("I am here")
        nothing()
    )
    else
        42

// if-elif-else always evaluates to value
let I1 = if 2 == 2 then 2 else 4
let I2 =
    if 2 == 1 then 2
    elif 3 == 4 then 3
    elif {x=1, y=2} == (1,2,3) then 4
    else 5
```


##### Pattern Matching

Pattern matching is a central element in Lalan design
It used in function clauses, let bindings before = token, lambda functions before -> token and
match expressions.
Lalan doesn't have loops so pattern matching and recursion are used to create iteration

In function clauses, arguments are sequentially matched against patterns. If a match succeeds and the optional guard is true,
the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

In match expressions
match <value_expression>
 '|' <pattern>[when guard] = <value_expression>
{'|' <pattern>[when guard] = <value_expression> }

the expression  is evaluated and the patterns  are sequentially matched against the result
If a match succeeds and the optional guard is true, the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

```
// Pattern syntax overview
match some_function()
    // underscore binds to anything
    | _ = something() // bodies are omitted below for clarity

    // integers
    | 1

    // floats
    | 2.32323

    // strings
    | "Hello"

    // symbols
    | #World

    // Booleans
    | False
    | True

    // name binds value to variable
    | x
    | SomeLONG_NAME

    // [] destructs all types implementing Seq interface
    // () destructs all types implementing Indexed interface
    // ... destructs rest of the data structure

    // tuples and others implementing Indexed
    | ()
    | (1)
    | (1,2,3)
    | (a, b, 42, ...rest)
    // lists and others implementing Seq
    | []
    | [1, 2, 3]
    | [1,2,3, x, (a,b,...rest_in_tuple), ...rest_in_list]
    | x::xs
    | 1::2::3::x::rest

    // {} destructs all types implementing Dict interface
    | {}
    | {x}
    | {x="some value", y, z=42}

    // operator `of` restricts value to type or interface

    | x of Int
    | _ of List
    | {field_name} of MyType
    | (first_index, second_index) of MyType

    // operator @ binds value or expression to variable
    | Result @ {genre, LilyName @ "actress"="Lily", age=13}
    | i @ 42

    // when expression can be used to specify condition for identical patterns
    | (a, (x, y, z)) when z == 3 and y == 2 and x == 1 and not (a == True)
    | (a, (x, y, z) when z == 4
    | (a, (x, y, z))

// Examples
fun count
    | 1 = #one
    | 2 = #two
    | 3 = #three
    | 4 = #four

fun f_c2
    | (a of Bool, b of String, c) = #first
    | (a of Bool, b, c) = #second
    | (a, "value", #value) = #third

fun f_c3
    | (0, 1, c) when c < 0 =  #first
    | (a of Bool, b of String, c) = #second
    | (a of Bool, b, c) when b + c == 40 = #third

fun map(f, coll)
    | (f, []) = empty(coll)
    | (f, hd::tl) = f(hd) :: map(f, tl)

// enclosed parenthesis are mandatory when function pattern consists of several comma separated patterns
// or when it written after function name
fun split_on_head_and_tail (x::xs) = (x, xs)

match {name="Bob", surname=("Alice", "Dou"), age=42}
    | {age=41, names} =  (name, age, 0)
    | {name, age=42} =  (name, age, 1)
    | {age=42} =  (age, 2)
    | _ =  42

match (1, 2, 1)
    | (A, x, A)  = (#first, A)
    | (A, x, B)  = (#second, A, B)
    | (3, A) = #third

match {x=1, y="YYYY"} with
    | {x of String, y of Int} = #first
    | {x of Int, y="YY" of String} = #second
    | {x of Int, y="YYYY" of String} = #third


let
(
    // all patterns, but without when guard can be placed by the left hand side of = operator
    (x,y,z) = (1,2,3)

    {x, y=[1, 2, (d,e) of MyType, a, b, ...rest], z @ 1=42} =
        {x=17, y=[1,2, (MyType 3 4), 4, 5, 7, 8, 9], 1=42}
    // also in lambdas
    split = x::xs -> (x, xs)

    get_name = {name} -> name
)
```

#### let-in
Let-in and match expressions are only ways to bind value to name in value_expression
Let-in creates nested, lexically-scoped, list of declarations
The scope of the declarations is the expressions after *let* and before *in*
and the result is the expression after *in*, evaluated in this scope
```
let
    {
        <pattern> = <value_expression>  |
        <function_declaration>
    }
in <value_expression>

Let-in is the only way to create named functions in local function scope

fun reverse(coll) =
    let
         fun _reverse
            | ([], result) = result
            | (hd::tl, result) = _reverse(tl, hd :: result)

    in
        _reverse(coll, empty(coll))

fun suffix_of(suf, s) =
   let
       delta = len(s) - len(suf)
       tl = nth_tail(delta, s)
   in delta >= 0 and tl == suf

// series of expressions after in
fun f() =
    let
        x = 1
        y = 2
        z = sqrt(4)
    in
    (
       io:print("x y z", x, y, z)
       sqrt(z + y + z)
    )

// Lexical scopes in Let-in
fun f() =
    let
        x = 1
        y = 2
    in
    (
        let
            x = 11
            y = 12
        in
        (
            affirm:is_equal(x, 11)
            affirm:is_equal(y, 12)
        )

        affirm:is_equal(x, 1)
        affirm:is_equal(y, 2)
    )

// let evaluates to value as all value expressions
v = let x = 1
        y = 2 in x + y

```

#### try-catch-finally-throw
**throw** **try** **catch** **finally**, common for many languages

```
// Any value can be used as exception

throw <value_expression>

try <value_expression>
catch <pattern> = <value_expression>
[finally <value_expression>]  |

try <value_expression>
catch
    | <pattern> [when guard] = <value_expression>
    [{ <pattern> [when guard] = <value_expression> }]
[finally <value_expression>]


//Examples

try
    try
        1/0
    catch e1 = e1
catch e2 =
    try
    (
        something()
        something_else()
    )
    catch e3 =
        e3

try
    try
        1/0
    catch e1 = e1
    finally
    (
        something()
        something_else()
    )
catch e2 =
    try
        error(#Catch)
    catch e3 = 42
    finally
        (e2, e3)

// With pattern matching in catch
try
    throw (1,2,"ERROR")
catch
    | err @ (1, y, 3) = #first
    | (1,2, "ERROR@") = #second
    | err @ (1, 2, x) = #third
finally =
    (#fourth, err, x)
```

### Modules and bootstrap
Module system is very simple: module = file and there are no packages
Module search path are always relative to startup script and there are no possibility of relative import

Example directory structure
```
+-- program.lal
+-- __std__
|   +-- seq.lal
|   +-- lazy.lal
+-- my
|   +-- modules
|       +-- module1.lal
|       +-- module2.lal
|   +-- module1.lal
|   +-- module3.lal
```
if we run Lalan with
```
python targetlalan.py program.lal
```
Module search path would look something like  [BASEDIR, STD, LALANSTD] where

* BASEDIR = directory in which program.lal is located
* STD = BASEDIR/\_\_std\_\_ - directory with user defined std modules. It will give user easy way to have custom prelude
* LALANSTD = environment variable LALANSTD which must contain path to global stdlib. If LALANSTD is empty, all required modules must be in STD directory

#### Loading order
* prelude.lal. If prelude is absent execution will be terminated. All names declared in prelude would be visible in all other modules
* stdlib modules used by runtime (derive.lal, bool.lal, num.lal, bit.lal, env.lal, string.lal, symbol.lal, vector.lal, list.lal, function.lal, fiber.lal, trait.lal, tuple.lal, map.lal, seq.lal, lazy.lal, datatype.lal)
* running script (in our case program.lal). After loading this sript lalan searches for function named 'main' and executes it. Result of 'main' function would be result of program

