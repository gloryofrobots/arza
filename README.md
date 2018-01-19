# Obin programming language

This repository contains prototype for experimental dynamically typed functional language

## Goal

To experiment with syntax and stackless virtual machine.
It is not a production system.
Obin is written in relatively 'slow' python language with not many speed optimisations.

To run the interpeter:
```
python targetobin.py test/obin/main.obn
```
or better use pypy

Currently, compilation via RPython toolchain is not supported, but it can be done with some efforts.
There are no REPL for obin at the moment.

## Features

* Indentation-aware syntax inspired by F#, Haskell and Python
* Persistant data structures (lists, tuples, maps)
* Pattern matching
* Lexical clojures and lambdas
* Usual amount of primitives (if-else, let-in, try-catch)
* User defined operators
* User defined types
* Traits and interfaces
* Single dispatch generic functions
* Partial application
* Stackless virtual machine
* Assymetric coroutines

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
- [Currying](#currying)
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

Obin uses indentation-aware syntax inspired by F# [#light] and Haskell.
Tokens [**if** **else** **elif**  **match** **try** **catch**
**let** **in** **fun** **interface** **generic** **type** **->** **|**]
trigger offside line.
Once an offside line has been set, all the expressions must align with the line,
until it is removed by dedent to previous line or by **end** token.

```
// Call function print from module io with result of if expression
io:print if 1 == 2 then
            False
         elif 2 == 3 then False
         else
            True

io:print if 1 == 2 then
            False
     elif 2 == 3 then False // Compile error: elif and else must align with if
         else
            True

```

Indentation ignored inside () {} []
```
// Complex expression mixing both indentation-free and indentation-aware layouts
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
                                            q res => res + if q > n - g then   // even while if inside () inner expressions must be aligned
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



New line in expressions outside of indention-free layouts terminates them,
except when last token in line is user defined operator or one of ":: ::: : . = or and"
```
X = sqrt 4  // expression terminates on new line
- 2        // compiles as X = (sqrt 4); -2;
X = sqrt 4 - // compiles as  X = sqrt 4 - 2
      2

false =
  True and
       False
```

Obin uses juxtaposition for function application. Obin syntax often looks like lisp without first layer of parens

```
func1 arg1 arg2 (func2 arg3 (func4 arg5 arg6) arg7) arg8 arg9
```

Obin functions are curried by default.

Some extreme syntax examples which will compile without errors
```
x =   1
    + 2
    + 3
    + 4


y = x
        + 3
            + 2 +
    5


let x = 222
    y = 333 in affirm:is_equal x 222
               affirm:is_equal y 333


match (1,2,3) with | (x,y,z) -> 2
                    | _ -> 1


match if 2 == 1 then
            2
      else
        3
      end
with
    | 2 -> 3
    | 3 -> 2


match fun _ x ->
            1
        end
with
    | Y ->
        (fun _ t
            | (a,b) -> a + b end
            (1 + 1, 2 + 2))
    | _ -> 2

(
    (x => x)
    (
        fun _ x ->
            1
        end
        , 3
        , 1
        , 4
        , 5
    )
)

(1
, fun _ x | 5 -> 25
            | 6 -> 45
, fun _ x
    | 5 -> 25
    | 6 -> 45
, (x => x)
// dedent terminates fun and because of the free indentation inside parens
// third element of the tuple evaluates to ((x => x) 45)
45)
```

### Predefined types and literals
```
// this is comment

// Bool type
True
False

// Integer type
1002020020202

// Float type
2.023020323

// String type
"I am string"

"""
I am M
ultilin
            e string
"""

// Symbol type
#atomic_string_created_onLyOnce

// Tuple type
() (1,2,3)

// List type
[1,2,3,4] 1::2::3::4::[]

// LazyVal type
x = delay 1 + 2

// LazyCons type
1:::2:::3:::4:::5

// Map type
{x=(1,2), y=(2,3)}

// Function type
x y => x + y

fun add_and_mul x y ->
    z = x + y
    z + x * y

// Datatype type
type Point x y

// Union type
type Option
    | None
    | Some val

```

### Data structures
```
// Many obin data structures are borrowed from [Pixie language](https://github.com/pixie-lang/pixie).
// All of the predefined data structures are persistent

// accessing fields
//<variable>.<name | integer>
t = (1,2,3)
t.0 + t.1 = 3 = t.2

//<name>.[<expression>]
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
//<varname>.{ <key>=<expression>* }

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
// = is not an assignment but pattern matching operator
// so variables can be bound to values only once in lexical scope.
// You can use let-in expression if you need to bind same variable name to another value.

X = 1
X = 1 // not an error - same value
X = 2 // runtime error

// Data structures are immutable

// Mutable variables are supported via ':= !' operators.
// Current implementation is built on top of coroutines and is extremely slow.

import var
v = var:var 2
!v = 2
v := 3
!v = 3
```

### Functions

```
// Function expressions in obin have three forms

// 1) Simple
fun <function_name> <arg>+  ->
    <expressions>

// result of the function is a result of last expression

// Example
fun any p l ->
    disjunction (map p l)

fun all p l ->
    conjunction (map p l)

//2) Case function with multiple clauses. All clauses must have same arity.

fun <function_name>
    | <pattern>+ [when guard] ->
        <expressions>
    | <pattern>+ [when guard] ->
        <expressions>
    ...

// transforms to match-with expression by the compiler

// Example
fun foldl
    | f acc [] -> acc
    | f acc hd::tl -> foldl f (f hd acc) tl


fun reverse coll ->
    fun _reverse
        | [] result -> result
        | hd::tl result -> (_reverse tl (hd :: result))

    _reverse coll (empty coll)

//3) Recursive two level function
// This kind of function allows to check argument types or other conditions only at first step of recursion

fun <function_name> <arg>+
    | <pattern>+ [when guard] ->
        <expressions>
    | <pattern>+ [when guard] ->
        <expressions>
    ...

// this function transforms in compile time to
fun <function_name> <arg>+
    (fun <function_name>
        | <pattern>+ [when guard] ->
            <expressions>
        | <pattern>+ [when guard] ->
            <expressions>
        ...
    ) <arg>+ // call inner function with outer function arguments
    // inner function has the same name as outer, so if inner is recursive it can't call outer

// initial arguments of outer function are visible through the entire recursive process

// Example
fun scanl func accumulator coll
    | f acc [] -> acc :: empty coll
    | f acc hd::tl -> acc :: scanl f (f hd acc) tl)

// Compiles into
fun scanl func accumulator coll ->
    (fun scanl
        | f acc [] -> acc::(empty coll) // coll contains initial value from first call
        | f acc hd::tl -> acc :: (scanl f (f hd acc) tl)
    end) func accumulator coll

// Lambda expression can be created with => operator
x => x
x y z => x + y + z

// they are often placed inside parens
seq:foldl (x y => x + y) 0 [1,2,3,4,5]

// on the left hand side of => operator any valid pattern is allowed
tail = hd::tl => tl
head = [hd, ...t] => hd
fullname = {name, surname} => name ++ " " ++ surname

// If you need multiple statement function in some expression, use 'fun' instead.
// Fun expression requires name, use _ if you don't need one:

seq:foldl (fun _ x y ->
              io:print "x + y" x y
              x + y
           end) 0 [1,2,3,4,5]

```

### Currying
Obin functions are curried by default
```
// Prelude functions inspired by F#
fun |> x f -> f x
fun <| f x -> f x
fun >> f g x -> g (f x)
fun << f g x ->  f (g x)
fun twice f -> f >> f
fun flip f x y -> f y x

// Usage

fun add x y -> x + y
add1 = add 1
(add1 2) = 3

// used with operators
((`-` 1) 2) (-1)
// flipped operator
((flip `-` 1)  2) =  1

l = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

(l |> (seq:filter) even
   |> (seq:map) (`+` 1)
   |> seq:map (flip `-` 2)) = [-1, 1, 3, 5, 7]


square = (x => x * x)
triple = `*` 3
(l  |> seq:filter even
    |> seq:map (`+` 1)
    |> seq:map (flip `-` 2)
    |> seq:map (triple >> square))  = [9, 9, 81, 225, 441]

((seq:filter even
    >> seq:map (`+` 1)
    >> seq:map (flip `-` 2)
    >> seq:map (triple >> square)) l) =  [9, 9, 81, 225, 441]
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

// Most operators are just functions from prelude (except from . .{ .( .[ : :: ::: and or as of @ requiring special treatment)
// prefix operator (operator, function_name)
prefix - negate
prefix ! !

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
```


### Expressions
#### if-elif-else

```
//Inspired by python but else is mandatory

if <expression> then
    <expressions>
*elif <expression> then
    <expressions>
...
else
    <expressions>

if one of the branches succeeds result of it's last expression will be result of entire if expression
```


#### match-with
Obin doesn't have loops so pattern matching and recursion used for iteration
##### Pattern matching in functions

```
fun <funcname> [arguments]
    | <pattern> [when guard] -> <body>
    | <pattern1> [when guard1] -> <body1>
    ...
```
Function arguments are sequentially matched against patterns. If a match succeeds and the optional guard is true,
the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

##### Match expression
```
match <expr> with
    | <pattern> [when guard] -> <body>
    | <pattern1> [when guard1] -> <body>
    ...
```
The expression <expr> is evaluated and the patterns  are sequentially matched against the result
If a match succeeds and the optional guard is true, the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

##### Supported patterns
```
// Patterns are the same for function clauses and match expressions

// -> <body> part below is ommitted
fun f arg1 arg2
    // integers floats symbols strings
    | 1 2.32323
    | "Hello" #World

    // Booleans
    | False True

    // Unit (empty tuple)
    | () ()

    // underscore binds to anything
    | _ _

    // variable name binds value to variable
    | x Y

    // [] destructs all types implementing Seq interface
    // () all types implementing Indexed interface
    // ...varname destructs rest of the data structure
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
    | a (x, y, z) when z == 3 and y == 2 and x == 1 and not (a == True)
    | a (x, y, z) when z == 4
    | a (x, y, z)
```
##### Examples

```
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
    | (a of Bool) (b of String) c -> #second
    | a of Bool b c when b + c == 40 -> #third

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

// all patterns, but without whem guard can be placed by the left hand side of = operator
(x,y,z) = (1,2,3)
{x, y=[1, 2, (d,e) of MyType, a, b, ...rest], z @ 1=42} =
    {x=17, y=[1,2, (MyType 3 4), 4, 5, 7, 8, 9], 1=42}
```

#### let-in

```
let
    <expressions>
in
    <expression>
```
Nested, lexically-scoped, list of declarations
The scope of the declarations is the <expressions> and the result is the <expression> evaluated in this scope

```
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
```


#### try-catch-finally-throw
**throw** **try** **catch** **finally**, common for many languages

```
// Any value can be used as exception

throw <expression>


try
    <expressions>
catch <expression> ->
    <expressions>
*finally // finally is optional
    <expressions>


try
    <expressions>
catch
    | <pattern> [when guard] ->
        <expressions>
    ...
*finally // finally is optional
    <expressions>


//Examples

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
        throw (e2, e3)


// With pattern matching in catch
try
    throw (1,2,"ERROR")
catch
    | err @ (1, y, 3) -> #first
    | (1,2, "ERROR@") -> #second
    | err @ (1, 2, x) -> #third
finally ->
    (#fourth, err, x)
```

### Types
```
// Fieldless singleton type
type Nothing

// Constructor type
Point x y

// or with tuple notation
Point (x, y)

// Enumeration type
type Ordering
    | LT | GT | EQ

// Complex variant type
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

p `kindof` Point = True
p `kindof` Shape = True
p `kindof` Square = False
p.x `kindof` Float = True


// inside match expression or function clauses
match p with
 | (x, y) of Point -> x + y // as tuple
 | (left, top, right, bottom) of Rect -> left.x + right.y // . operator can access instance field by name
 | {right, top, left, bottom} of Rect -> left.x + right.y // as map

```

### Single dispatch
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
Mixins or Inheritance can solve this problem but obin goes the other way.
In obin generic functions and protocols(interfaces) declared apart from each other
and interfaces combine one or more previously declared generics.
Type doesn't need to signal implementation of interface but needs to implement all generic functions belonging to interface
Obin generic functions can dispatch on argument in any position


#### Generics
```
// Generic provides dispatch (single) on one of it's arguments

generic
    <name> [`]<arg>+
    ...

// ` before argument signals position of 'dispatch' argument (argument on which type dispatch occurs)
// ` can be ommited on generic with only one argument

generic equal `x y
generic negate x

// dispatch on last argument

generic cons value `seq


// declare many generics in one layout

generic

    mod `x y

    - `x y

    + `x y

    put key value `self

    at key `self

    del obj `self

    elem key `self
```

#### Interfaces

```
interface
    <name> (<generic>+)
    ...


// Interface combines one or more generic functions and can be used for type check in pattern matching
// generic functions must be declared at this point

interface

    PartialEq (==)

    Eq (!=, ==) // shares same == generic

    Seq(first, rest)

    Ord(<, <=, >, >=, cmp, max, min)

    Str (str)

    Collection(put, at, del, elem)

    Dict(keys, values, put, at, del, elem)

    Ref(!)

    MutRef(!, :=)

```

#### Extend
```
extend <type>
    def <generic> <function_definition>


// extend type with generic function

type MyList l

extend L
    def + self other
        | self other of List -> MyList (self.l + other)
        | self other of MyList -> MyList (self.l + other.l)

    def len self -> len self.l

    def is_empty self -> is_empty self.l

    def first self -> self

    def rest self -> self

// if interfaces Seq(first, rest), Add(+) and Sized(len) exist
// we can check if type implements them

mylist = MyList [1,2,3,4,5,6]
match mylist with
    | l of Seq -> ()
    | l of Seq -> l

or with builtin kindof function
mylist `kindof` MyList = True
mylist `kindof` Number = False
mylist `kindof` Seq = True
mylist `kindof` Sized = True
mylist `kindof` Add = True
mylist `kindof` Sub = False
```

#### Traits
Trait is unit for code reuse in obin.
They are simple maps {generic = implementation} and can be used in extend statement
to share common behaviour between different types

```
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
    // all implementations defined in Equal trait will be attached to MyList
    use Equal

    // only le and ge will be attached to the type
    use Order (le, ge)

    // Trait is a simple map with generics as keys and implementation functions as values
    def lt x y -> Order.[lt] x y
    def gt x y -> Order.[gt] x y
```

### Modules and bootstrap
Module system is very simple: module = file and there are no notion of packages
Module search path are always relative to running script and there are no possibility of relative import

Example directory structure
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
Module search path would look something like  [BASEDIR, STD, OBINSTD] where

* BASEDIR = directory in which program.obn is located
* STD = BASEDIR/\_\_std\_\_ - directory with user defined std modules. It will give user easy way to have custom prelude
* OBINSTD = environment variable OBINSTD which must contain path to global stdlib. If OBINSTD is empty, all required modules must be in STD directory

#### Loading order
* prelude.obn. If prelude is absent execution will be terminated. All names declared in prelude would be visible in all other modules
* stdlib modules used by runtime (derive.obn, bool.obn, num.obn, bit.obn, env.obn, string.obn, symbol.obn, vector.obn, list.obn, function.obn, fiber.obn, trait.obn, tuple.obn, map.obn, seq.obn, lazy.obn, datatype.obn)
* running script (in our case program.obn). After loading this sript obin searches for function named 'main' and executes it. Result of 'main' function would be result of program

#### Import and export
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
