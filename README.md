# Obin programming language

This repository contains prototype for experimental dynamically typed functional language
## Goal
To experiment with syntax and stackless virtual machine.
It is not a production system.
Obin written in interpreted language Python with not many speed optimisations

Running interpeter
```
python targetobin.py test/obin/main.obn
```
or better use pypy

Currently, compilation via RPython toolchain not supported but it can be done with some efforts

## Features
* Modern expressive functional syntax resembling something between Erlang and F#.
* Handwritten, extensible, operator precedence parser with support of indentation layouts and juxtaposition operator
* User defined operators
* Builtin single dispatch engine with some interesting features (separation on trait,interface, generic function; dispatch not only on first argument)
* Support for partial application
* Stackless virtual machine
* Persistant data structures (lists, vectors, maps)
* Pattern matching, user defined types, union types, let-in, if-elif-else, clojures, try-catch-finally
* Assymetric coroutines

## Guide

### Syntax
Obin uses laconic layout based syntax inspired from F# [#light] and Haskell.
This syntax looks like Python but it is more powerful and allow you to use for example function expressions or if-else expressions inside other expressions
in condition that indentation rules is correct

```
// Call function print from module io with result of if expression
io:print if 1 == 2 then
            False
         elif 2 == 3 then False
         else
            True
```
in this example if creates offside line, Once an offside line has been set, all the expressions must align
with the line until it will be removed by dedent to previous line or special end token
Tokens capable of creating own layouts: if, else, elif,  match, try, catch, |, let, in, fun, interface, generic, type, ->
Tokens capable of removing layouts: end, -----[-]* (more than five dashes)
Offside lines not working inside () {} [], so for example this function interprets without error
```
fun nine_billion_names_of_god_the_integer () ->
    (string:join
        (seq:map
            (n => string:join_cast
               (seq:map (g =>
                            fun _loop n g ->
                                if g == 1 or n < g then 1
                                else
                                    (seq:foldl
                                        (
                                            q res => res + if q > n - g then
                                                              0
                                                           else
                                                            (_loop (n-g) q)
                                        )
                                        1
                                        (range 2 g))
                                end // end token removes if layout and adds readability
                            end n g) (range 1 n)) " ") // end token terminates function layout and allows to call function with arguments (n g)
            (range 1 25))
         "\n")
```
New line in expressions outside of free layout parens ( ) terminates them,
except when last token in line is user defined operator or one of ":: ::: : . = or and"

Obin uses juxtaposition for function application. Obin syntax often looks like lisp without first layer of parens

```
func1 arg1 arg2 (func2 arg3 (func4 arg5 arg6) arg7) arg8 arg9
```

Obin functions not curried by default (mainly because in dynamic language currying may cause a lot of annoying runtime errors)
<!--- , shamelessly stolen from [Pixie](https://github.com/pixie-lang/pixie). --->

### Predefined types and literals
```
// this is comment
// Bool
True
False

// Integer
1002020020202

// Float
2.023020323

// String
"I am string"

"""
I am M
ultilin
            e string
"""

// Symbol
#atomic_string_created_onLyOnce

// Tuple
() (1,2,3)

// List
[1,2,3,4] 1::2::3::4::[]

// LazyVal
x = delay 1 + 2

// LazyCons
1:::2:::3:::4:::5

// Map
{x=(1,2), y=(2,3)}

// Function
x y => x + y

fun add_and_mul x y ->
    z = x + y
    z + x * y

```

### Data structures
```
// All of predefined data structures are persistant

// accessing fields
t = (1,2,3)
t.0 + t.1 = 3 = t.2
t.[0] + t.[2-1] = 3 = t.[sqrt 2]

// same aplies to lists
l = [1,2,3]
l.0 + l.1 = 3 = l.2
l.[0] + l.[2-1] = 3 = l.[sqrl 2]

// t.0 and l.[2-1] compiles into
(at 0 t) (at (2-1) l)

m = {one=1, two=2, three=3}
m.one + m.two = m.three

// compiles into
(at #one m) + (at #two m) = (at #three m)

// creating new collection from old one

m1 = m.{three=-3, four=4}

M = {
    line = {
        data = [1,2,3,4],
        index = 1
    },

    id = 12
}

M1 = M.{
    line = M.line.{
        index_2 = M.line.index + 42,
        data = [4, 3, 2, 1]
    },
    id = "ID M1"
}

M1 = {line = {index = 1, index_2 = 43, data = [4, 3, 2, 1]}, id = "ID M1"}

[1,2,3,4,5].{0=102, 1=103, 4=105} = [102, 103, 3, 4, 105]
[1,2,3,4,5].{7=7}  // runtime error because of invalid index

```

### Immutability

```
// Variables can be bind only once
X = 1
X = 1 // not an error - same value
X = 2 // runtime error

// Datastructures are immutable

// Mutable variables supported via := ! operators
// current implementation is buid on top of coroutines and is extremely slow
import var
v = var:var 2
!v = 2
v := 3
!v = 3
```

### Functions
```
// Function in Obin can have one of three forms
// simple
fun function_name arg1 argn ->
    (body)

// where (body) is one or more expressions separated by \n or some special cases

// Example
fun any p l ->
    disjunction (map p l)

fun all p l ->
    conjunction (map p l)

// case function with multiple clauses
// all clauses must have same arity
fun function_name
    | pattern1 pattern ->
        (body1)
    | pattern1 pattern ->
        (body1)

// Example
fun foldl
    | f acc [] -> acc
    | f acc hd::tl -> foldl f (f hd acc) tl


fun reverse coll ->
    fun _reverse
        | [] result -> result
        | hd::tl result -> (_reverse tl (hd :: result))

    _reverse coll (empty coll)

// Recursive two level function
// this is special kind of form which allows to check argument types or other conditions only in first recursive call
fun function_name arg1 argn
    | pattern_1 pattern_n ->
        (body1)
    | pattern_1 pattern_n ->
        (body1)

// this function transforms in compile time to
fun function_name arg1 argn
    (fun function_name
        | pattern_1 pattern_n ->
            (body1)
        | pattern_1 pattern_n ->
            (body1)
     end) arg1 argn  // inner function call
     // function_name now binds to inner function

// initial arguments of outer function visible through entire recursive process

// Example
fun scanl func accumulator coll
    | f acc [] -> acc :: empty coll
    | f acc hd::tl -> acc :: scanl f (f hd acc) tl)

// Compiles into
fun scanl func accumulator coll ->
    (fun scanl
        | f acc [] -> acc::(empty coll) // coll here contains initial value from first call
        | f acc hd::tl -> acc :: (scanl f (f hd acc) tl)
    end) func accumulator coll

/// Lambda expressions
// Lambda expression can be created with => operator
x => x
x y z => x + y + z

// they are often used inside parens
seq:foldl (x y => x + y) 0 [1,2,3,4,5]

// on the left side of => operator can be any valid pattern
// on the right side - single expression
tail = hd::tl => tl
head = [hd, ...t] => hd
fullname = {name, surname} => name ++ " " ++ surname

// if you need multiline function expression use fun instead
// Important fun expression requires name, use _ if you don't need one

seq:foldl (fun _ x y ->
              io:print "x + y" x y
              x + y
           end) 0 [1,2,3,4,5]

```
### Operators

```
"""
Precedence    Operator
    100           : . .{ .( .[
    95           JUXTAPOSITION
    60           :: :::
    55           **
    50           *  /
    40           +  - ++
    35           ==  !=  <  <=  >  >=
    30           and
    25           or << >>
    20           |>
    15           @ as of <|
    10           = :=
"""

// Most operators are just functions from prelude (except from . .{ .( .[ : :: ::: and or as of @)
// prefix operator (operator, function_name)
prefix - negate
prefix & &

// right associative (operator, function name, precedence)
infixr := := 10

// left associative
infixl + + 40
infixl - - 40
infixl * * 50
infixl / / 50

// Almost all operators have lower precedence than function application
// sqrt 4 + 6 = (sqrt 4) + 6
// to use operator as prefix function put it between ``
// foldr `+` l2 l1
// to use function as infix operator put it between `` too
// 4 `mod` 2 = 0
// There are special rules for resolving ambiguity when both prefix and infix precedence defined (subtraction and negate for -) 

(2-1) =  1 // infix because no space between - and left operand
(2 - 1) = 1 // infix because space between both operands

(2- -1) =  3 // prefix because previous token is operator and afterwards infix
(2- - 1) =  3 // same rule applies
(2 - - 1) = 3 // same rule applies

(identity -1) = -1 // prefix because no space between operator and operand

// Operators defined in prelude.obn are global to all modules
// Operators defined in user module are local to this module and can't be exported
// This is artificial limitation
```

### Pattern matching
```
// Obin doesn't has loops so pattern matching and recursion is what used most of the times
// Pattern matching can be used in function clauses or in special match expression
fun f arg1 arg2
    // integers floats symbols strings
    | 1 2.32323
    | "Hello" #World

    // Special values
    | False True

    // Unit (empty tuple)
    | () ()

    // underscore binds to anything
    | _ _

    // variable name binds value to variable
    | x y

    // [] destructs all types implementing Seq interface (generic functions first and rest)
    // () all types implementing Indexed interface
    // ...varname destructs rest of the collection
    // Sequences can also be destructed by :: operator
    | [1,2,3,x, ...rest] (1,2,y) 
    | 1::2::3::x::rest   (a,b,...c)
    
    // {} destructs all types implementing Dict interface
    | {key1="Value", key2, key3=(1,2,3)} {key3, key4}

    // operator `of` restricts value to type or interface
    | x of Int _ of List
    // parens for readability
    | ({key, otherkey} of MyCustomType) (_ of List)

    // opeator @ binds value or subexpression to variable
    | Result @ {genre, LilyName @ "actress"="Lily", age=13}  i @ 42
    // when expression can be used to specify condition for identical patterns
    | a (x, y, z) when z == 3 and y == 2 and x == 1 and not (a `is` True)
    | a (x, y, z) when z == 4
    | a (x, y, z)

// Working examples
fun count
    | 1 -> #one
    | 2 -> #two
    | 3 -> #three
    | 4 -> #four

fun f_c2
    | a of Bool b of String c -> #first
    | a of Bool b c -> #second
    | a b c -> #third

fun f_c3
    | 0 1 c when c < 0 ->  #first
    | a of Bool b of String c -> #second
    | a of Bool b c when b + c == 40 -> #third

// all same rules applie to match expressions

match {name="Bob", surname=("Alice", "Dou"), age=42} with
    | {age=41, names} ->  (name, age, 0)
    | {name, age=42} ->  (name, age, 1)
    | {age=42} ->  (age, 2)
    | _ ->  42

match (1, 2, 1) with
    | (A, x, A)  -> (#first, A)
    | (A, x, B)  -> (#second, A, B)
    | (3, A) -> #third

//from test suite
affirm:is_equal (
    match {x=1, y="YYYY"} with
        | {x of String, y of Int} -> #first
        | {x of Int, y="YY" of String} -> #second
        | {x of Int, y="YYYY" of String} -> #third
) #third

// pattern matching can be used as left part of = expression
(x,y,z) = (1,2,3)
{x, y=[1, 2, (d,e) of MyType, a, b, ...rest], z @ 1=42} =
    {x=17, y=[1,2, (MyType 3 4), 4, 5, 7, 8, 9], 1=42}
```

### Let in bindings

```
// Every let block creates its own lexical scope
// It can be used to avoid limitations of variable immutability

x = 1
y = 2

let
    x = 11
    y = 12
in
    affirm:is_equal x 11
    affirm:is_equal y 12

// it can be used as expression
v = let x = 1
        y = 2 in x + y

affirm:is_equal v 3

// Every let block compiles into anonymous function
```

### Exceptions

```
// usual throw try catch finally blocks
// Anything can be used as exception
try
    try
        1/0
    catch e1 ->
        e1

catch e2 ->
    try
        throw #Catch
    catch e3 ->
        42
    finally ->
        //uncatched
        throw (e2, e3)

// With pattern matching on exception value
try
    throw (1,2,"ERROR")
catch
    | err @ (1, y, 3) -> #first
    | (1,2, "ERROR@") -> #second
    | err @ (1, 2, x) -> #third
finally ->
    (#fourth, err, x)
```

### User defined types
```
// Singleton types without fields
type Nothing

// Union enumeration type
type Ordering
    | LT | GT | EQ

// Complex union type
type Shape
    | X x
    | Y y
    | Point (x, y)              // fields can be expressed as tuple 
    | Square width height       // or juxtaposition
    | Rect left top right bottom
    | Line point1 point2
    | Empty

// creating type instances
p = Point 24.5 25.7
r = Rect p (Point 12 34) (Point 34 54) (Point 31 12)

// Pattern matching on types and field access on type instances
match p with
 | (x, y) of Point -> x + y
 | (left, top, right, bottom) of Rect -> left.x + right.y // . operator can access field from type instance by field name

```

### Obin single dispatch generics
In modern functional languages popular single dispatch mechanism based on protocols 
In such system at first you declare protocol and functions belongs to it
At second you declare one or more types and then you implement protocol for them
In Clojure it will look like
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

It is a very simple and powerful system but it has problem of tightly bounding functions to only one protocol 
What if we need to have one function belongs to two or more protocols at once
For example we can have protocol for collection with methods 'at' and 'elem' and protocol for
mutable collection with methods 'at' 'elem' 'put' 'del'
We can, of course, provide some way of mixing or inheriting protocols, but Obin goes the other way
In obin generic functions and protocols(interfaces) declared separatly
and interfaces combine one or more previously declared generics.
Type doesn't need to signal satisfaction of interface, it will be done automatically at runtime
It only needs to implement generic functions belonging to interface

```
// Generic is a special kind of function provides single dispatch on one of it's arguments

// == is name and x y is args of generic
// ` before x means that function will dispatch on its first argument
generic == `x y

generic max `first second
// or you can declare them in one layout

// declare many generics in one layout
generic
    mod `x y
    - `x y
    + `x y

    // dispatch argument at last position
    put key value `self
    at key `self
    del obj `self
    elem key `self

// Interfaces
// Interface combines one or more generic functions and can be used for type check in pattern matching 
// generic functions must be declared at this point

interface
    PartialEq (==)
    Eq (!=, ==)
    Seq(first, rest)
    Ord(<, <=, >, >=, cmp, max, min)
    Str (str)
    Dict(keys, values, put, at, del, elem)
    Ref(!)
    MutRef(!, :=)

// to extend type with generic function

type MyList l

extend L
    def len self -> len self.l

    def is_empty self -> is_empty self.l

    def first self -> self

    def rest self -> self

if exists interface Seq(first, rest) and Sized(len)
it can be used in pattern matching
mylist = MyList [1,2,3,4,5,6]
match mylist with
    | {l1} of Seq -> ()
    | {l} of Seq -> l

or with builtin kindof function
mylist `kindof` MyList = True
mylist `kindof` Number = False
mylist `kindof` Seq = True
mylist `kindof` Sized = True

// extending every type with its own implementation of generics might be very annoying
// to avoid problem use traits

generic
    eq `x y
    ne `x y
    le `x y
    lt `x y
    ge `x y
    gt `x y

trait Equal
    def eq x y -> not (ne x y)
    def ne x y -> not (eq x y)

trait Order
    def le x y -> (cmp x y) != GT
    def lt x y -> (cmp x y) == LT
    def ge x y -> (cmp x y) != LT
    def gt x y -> (cmp x y) == GT

extend MyList
    // implementations of eq and ne defined in Equal trait will be attached to MyList
    use Equal
    // only le and ge will be attached to the type
    use Order (le, ge)

    // Trait is a simple map with generics as keys and implementation functions as values
    def lt x y -> Order.[lt] x y
    def gt x y -> Order.[gt] x y
```

### Partial application

```
// from prelude.obn

fun partial func ...args ->
    // primitive function
    obin:lang:defpartial_with_arguments func args

// prefix operator for partials
fun & func ->
    // primitive function
    obin:lang:defpartial func

// Functions inspired by F#
fun |> x f -> f x
fun <| f x -> f x
fun >> f g -> (x => g (f x))
fun << f g -> (x => f (g x))
fun flip f x y -> f y x

fun add x y -> x + y
add1 = &add 1

(add1 2) = 3

// used with operators
((&`-` 1) 2) (-1)
// flipped operator
((partial flip `-` 1)  2) =  1

l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

(l |> (&seq:filter) even
   |> (&seq:map) (&`+` 1)
   |> partial seq:map (partial flip `-` 2)) = [-1, 1, 3, 5, 7]


square = (x => x * x)
triple = &`*` 3
(l  |> partial seq:filter even
    |> partial seq:map (partial `+` 1)
    |> partial seq:map (partial flip `-` 2)
    |> partial seq:map (triple >> square))  = [9, 9, 81, 225, 441]

((partial seq:filter even
    >> partial seq:map (partial `+` 1)
    >> partial seq:map (partial flip `-` 2)
    >> partial seq:map (triple >> square)) l) =  [9, 9, 81, 225, 441]

```

### Modules and main function
Module system is very simple
module = file and there no notion of packages
module search path are always relative to running script and there no possibility of relative import

Example if we have
```
+-- program.obn
+-- __std__
|   +-- seq.obn
|   +-- lazy.obn
+-- my
|   +-- modules
|       +-- module1.obn
|       +-- module2.obn
|   +-- module1.obn
|   +-- module3.obn
```
if we run Obin with
```
python targetobin.py program.obn
```
local __std__ directory automatically placed into module search path
which already contains system variable OBINSTD
Obin search file prelude.obn in local __std__ if it exists or in OBINSTD
if not found one it will aborts execution
__std__ directory must have file prelude.obn which will be first loaded file by interpreter
All names declared in prelude would be visible in all other modules
after loading __std__/prelude.obn interpreter loads list of predefined modules such as
list.obn num.obn string.obn ...
afterwards it loads program.obn and then lookups for function named 'main' and executes it
result of 'main' function would be result of program

#### Importing and exporting names
```
// By default all names except operators can be imported outside
// You can limit it with
export (f_ab, f_ab_2, CONST)

fun f1 num -> ()
fun f2 num1 num2 -> ()
CONST = 10
fun f3 () -> ()

// to import module use it name relative to program.obn with / replaced by :
// this modules declared in __std__, no need to specify path

import seq
import io

// all exported names from this modules can be accessed with : operator
// such name often called 'qualified name'

io:print (seq:reverse [1,2,4,5])

// import other module
import my:modules:module1

// all exported names binds to module1:variable_name
// as you see only last part of the module name is used in qualified names

module1:add 1 2

// if there are modules with indentical names alias needs to be used

import my:modules:module1 as mod1
import my:module1 as mod1_1
mod1:add (mod1_1:add 1 2) 3

// import only required qualified names

import my:module1 (f1 as f1_1, f2 as f2_1)
module1:f1_1 ()
module1:f2_1 ()

import my:modules:module1 as mod1 (f1, f2)
mod1:f1 ()
mod1:f2 ()

import my:module1 as mod1 (f1 as f1_1, f2 as f2_1)
mod1:f1_1 ()
mod1:f2_1 ()

// hiding names

import my:modules:module1  hiding (CONST)
module1:f1 ()
module1:f2 ()

import my:modules:module1 as mod1 hiding (f1)
mod1:f2 ()
mod1:CONST

import tests:lib_az:abc:module_ab as ab5 hiding (f_ab, CONST)

/// UNQUALIFIED IMPORT

// import specified unqualified names

from my:modules:module1  import (f1, f2, CONST as const)
f1 ()
f2 ()
const

// import all unqualified names from module

from my:modules:module1 import _

// hiding specific names

from my:modules:module1 hide (CONST)
f1()
f2()
```