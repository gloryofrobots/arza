# Arza programming language

Arza is an experimental programming language supporting multiple dispatch and immutable data out of the box.
This is a prototype built in relatively 'slow' language python and is not ready for productin in any way.

## Running
```
python targetarza.py test/arza/main.arza
```
or better use pypy

Currently, compilation via RPython toolchain does not supported but it can be done with some efforts.
There are no working REPL at the moment

## Features

* Original whitespace based syntax inspired by F#, Python and Lisp
* Persistent data structures (lists, tuples, maps)
* Pattern matching
* Lexical clojures and lambdas
* Usual number of primitives (if-else, let-in, try-catch)
* User defined operators
* User defined types
* Powerfull predicate multiple dispatch generic functions
* Interfaces supporting multiple dispatch paradigm
* Tools for code reuse - traits and type mixins
* Special syntax and custom operator for partial application
* Stackless virtual machine
* Asymmetric coroutines

## TODO

* Macros
* REPL
* Tail call optimisations
* Total speed optimisations
* Production ready native version

## Guide

- [Syntax overview](#syntax-overview)
- [Multiple dispatch](#multiple-dispatch)
  - [Interface expression](#interface-expression)
- [Import and export](#import-and-export)
- [Defining operators](#defining-operators)
- [Module let expression](#module-let-expression)
- [Function expression](#function-expression)
- [Type expression](#type-expression)

- [Value expressions](#value-expressions)
  - [Literals](#literals)
  - [Access and update operators](#access-and-update-operators)
  - [Partial application](#partial-application)
  - [if-elif-else expression](#if-elif-else)
  - [Pattern matching](#pattern-matching)
  - [let-in expression](#let-in)
  - [try-catch-finally and throw expressions](#try-catch-finally-throw)

- [Modules and bootstrap](#modules-and-bootstrap)
  - [Loading order](#loading-order)

### Syntax overview
Arza syntax very similar to F# light syntax where indentation 
used as statement and expression delimiter but instead of using simple 
dedents and indents like in Python, Arza uses code layouts 
to determine block borders

```
// layout is similar to pythons four space indent
fun f(x) =
    1
    2
         
// layout begins straight after = token 
fun f(x) = 1
           2

// this would be a syntax error
fun f(x) = 1
    2
```

Most times layouts created with = token
There are special rules for operators to continue expressions from line above,
which differs from F# syntax and more similar to Ruby syntax

```
fun f() =
    1 +
    2 +
    3
// returns 6
```

However this technique creates problem with ambidextra operators
(operator having have both prefix and infix binding powers)
Examples of such operators are *-* and *(*
To resolve parsing conflicts Arza uses new lines as terminators

```
fun f() =
    //lambda expression
    ((x, y) -> x + y)
    // parser treats `(` as prefix expression because of new line
    (1, 41)

f() == (1, 41)

fun f2() =
    // parser treats `(` as infix expression and interprets
    // this expression as call to lambda with arguments (1, 41)
    ((x, y) -> x + y)(1, 41)

f2() == 42
```

If you do not like to use indentation aware syntax at all, you can
enclose any block in ( and )

You can enclose in ( and ) almost any syntax construct and use  free code layout
without worrying about whitespaces. 

```
(fun f() = 
        1
 +
  2 + 3)
  
(interface Map
    fun put
        (key, value, @map)
 fun at
     (key,
      @map)
) 
```

If you need to use nested statements inside such free layout you must enclose each of them in ()

```
// Nine billion names of God the Integer
fun nbn () =
    string:join(
        seq:map(
            fun(n) =
                string:join_cast(
                   seq:map(
                        (fun (g) =
                            //let in block enclosed in ()
                            (let
                                (fun _loop (n, g) =
                                    // if block enclosed in ()
                                    (if g == 1 or n < g then 1
                                    else
                                        seq:foldl(
                                            // fun block enclosed in ()
                                            (fun (q, res) =
                                                // if block enclosed in ()
                                                (if q > n - g  then
                                                    res
                                                else
                                                    res + _loop(n-g, q)
                                                )
                                            ),
                                            1,
                                            list:range(2, g)
                                        )
                                    )
                                )
                            in _loop(n, g)
                            )
                        ),
                        list:range(1, n)
                   ),
                   " "
                ),
           list:range(1, 25)
        ),
        "\n"
    )
```

There are three main kinds of expressions in Arza
* Top level expressions (import, export, from, fun, let, extend,  describe, interface, type, prefix, infixl, infixr)
* Pattern matching expressions inside function signature, after let expression or in match expression
* Value expressions usually occur after = token and always evaluate to some value

Name binding can be done only inside *let-in* statement

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
        io:print("z and w", z, w)
        let k = w / z
        in k +
           x +
           y
```


### Multiple dispatch

Arza provides predicate multiple dispatch for polymorphism. This concept is comperativly rare in languge design.
In recent years more limited approach was implemented in Julia language.
Arza generic functions could be specialized for any arguments and also for simple predicate expressions. 
Essentially, they resemble pattern matching functions in Erlang
but with posiibility to define clauses at different places in code.
Most novative concept in Arza is that programmer can define interfaces along side generic functions.

```
interface CargoRobot =
    //@robot - tells interpreter that all types used as first argument in this generic function will implement
    // CargoRobot interface
    fun move_cargo(@robot, cargo)

    // here type must me used as second arguments
    fun recharge(amount, @robot)
    
// Now declaring Cargo interface
interface Cargo
    // this function has been already declared in CargoRobot interface
    // but Cargo types must be used as second arguments instead of first
    use move_cargo(robot, @cargo)

// Interfaces do not create namespaces. 

fun move(robot, cargo) = 
    move_cargo(robot, cargo)
    recharge(100, robot)
    
// Now define some types
type BaseRobot = (model)

// mixin this type in another
type RobotActual(BaseRobot) = (energy_level)

// this not an inheritance and methods defined for first type do not automatically support second type

type Cargo(type, weight, moved)

// defining methods

def move_cargo(robot of RobotActual, cargo of Cargo) =
    // data is imutable this is operator for creating shared copies 
    // there are no return statement
    // last expression returns automatically
    io:print("moving cargo")

    
    //returning tuple with moved cargo and slightly exosted robot
    (cargo.{moved = True}, 
        // I will implement shortcut for persistent -= operation in future
        robot.{battery=robot.battery-10})
    
    

def recharge(r of Robot) = 
    r.{battery=100}

//Some more examples
interface Add =
    fun add(val1, val2)

// declare type for complex numbers
type Complex(real, imag)

// specialize add for Complex and Int types with def statement

def add(c1 of Complex, c2 of Complex)  =
    Complex(c1.real + c2.real, c1.imag + c2.imag)

def add(i of Int, c of Complex)  =
    Complex(i + c.real, c.imag)

def add(c of Complex, i of Int) =
	add(i, c)
// Such definitions are not restricted to current module, you can define them anywhere, like

import my_module:add
def my_module:add(c of Complex, i of Int) =
	add(i, c)

```

Predicate is a special condition, which narrow the application of a specialization.
Specialisations with predicates have more priority then simple ones

```
def add(c of Complex, i of Int) when i == 0 =
	c

// You can use any normal expression in predicate including function calls

interface Fav =
    fun get_favorite(c1, c2)

type Car (speed)

fun faster(v1, v2) = v1.speed > v2.speed

def get_favorite(c1 of Car, c2 of Car) when faster(c1, c2)  = c1
def get_favorite(c1 of Car, c2 of Car) = c2

```



### Import and export

```
// By default all names except operators can be imported outside
// You can limit it with export expression
let CONST = 41
fun f_ab () = CONST + 1
fun f_ab_2 = f_ab()

export (f_ab, f_ab_2, CONST)

// to import module use it's name relative to program.arza with / replaced by :
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

### Defining operators

```
// real code from prelude.arza
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
// use qualified name to prevent infinite loops in cases of declaring local negate function using prefix -
prefix (-, arza:lang:negate, 55)
// infix :: -> 60
infixl (**, **, 60)
// prefix # -> 70
prefix (!, !, 70)
infixl (.., .., 90)
// infix (  .{ .[ -> 95
prefix (&, &, 96)
// infix . : -> 100


// when parser transforms expressions with operators to call expressions
2 - 2 -> -(2, 2)
-2 -> negate(2)

// to use operator as prefix function put it between ``
// foldr(`+`, l2, l1)
// to use function as infix operator put it between `` too
// 4 `mod` 2 = 0

// Operators defined in prelude.arza are global to all modules and environments
// Operators defined in other module are local to this module and can't be exported
```

### Module let expression

In Arza *let* is the only way to bind name to variable.
But except for that let expression actually performs pattern matching
Value can be bind to name only once.
Top level let expression is different from let-in expression allowed in value expressions
```

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
    x = 1
    _ = f()
    () = io:print(42)
    x::xs = [1,2,3,4,5]
```

### Function expression
```
// Function expression in arza has three possible forms
//
// Simple
fun <name> `(`[arg_pattern]`)` [ when  <value_expression>]= <code_block> 

fun any(p, l) =
    disjunction(map(p, l))

fun all(p, l) =
    conjunction(map(p, l))

fun print_2_if_greater(val1, val2) when val1 > val2 =
    io:print("first", val1)
    io:print("second", val2)

// Case function with multiple clauses. All clauses required to have the same arity.

fun <name>
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <code_block>}

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
    {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <code_block>}


// this function transforms in compile time to
fun <name> `(`{arg_pattern}`)` =
    let
        // inner case - function
        fun <name>
            {`|` `(`{arg_pattern}`)` [ when  <value_expression>] = <code_block>}
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

### Type expression
```
type <name> {field `,`} |
type ( {<name> {field `,`}} )

type Name
// Fieldless singleton type
type Nothing
// Constructor type
type Point(x, y)

type Square (width, height)

// alternative syntax used when type has mixins
type Rect(Square) = (left, top, right, bottom)

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
 | (left, top, right, bottom) of Rect = left.x + right.y // unpacking type like tuple
 | {right, top, left, bottom} of Rect = left.x + right.y // unpacking type like map

```


### Value expressions

#### Literals

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
        io:print(x + y)
        z + x * y

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

#### Access and update operators

Many arza data structures borrowed from [Pixie language](https://github.com/pixie-lang/pixie).
All of predefined data structures are immutable

```
// accessing fields
// via field name
let
    m = {x = 1, y = 2}
    v = m.x + m.y
// via index
let
    t = (1,2,3)
    v = t.0 + t.1
    
// calculating index or field
let v = t.[0] + t.[2-1]

// same applies to lists
let
    l = [1,2,3]
    v = l.0 + l.1
    v1 = l.[0] + l.[2-1]
    v2 = l.[sqrt(4)]

// t.0 and l.[2-1] compiles into at(0, t) and  at((2-1), l)
// m.one compiles into at(#one, m)


// creating new collection from old one via .{ operator

let
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

#### Partial application
```
Arza provides special syntax for partial application via .( operator

fun sum_3(x, y, z) = x + y + z

let
    add_to_1 = sum_3.(1)
    add_to_3_and_4 = sum_3.(3, 4)
    v = add_to_1(1, 2)
    v = add_to_1(1)(2)
    s = add_to_3_and_4(1)
    
// Also there are two operators in prelude responsible for creating curried functions
// prefix
fun &(func) = arza:lang:defpartial(func)
// infix
fun ..(f, g) = arza:lang:defpartial(f)(g)
let
   n = seq:map(&`+`(2), [1,2,3])
   // n = [3, 4, 5]
    add_to_1 = sum_3 .. 1
    add_to_3_and_4 = sum_3 .. 3 .. 4


// combined with pipe and composition operators currying might be extremely useful
fun |>(x, f) = f(x)
fun <|(f, x) = f(x)
fun >>(f, g) = x -> g(f(x))
fun <<(f, g) = x -> f(g(x))

fun twice(f) = f >> f
fun flip (f, x, y) = f(y, x)

let
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
    
    // Using _ holes to create partial application
    l2 = l |> seq:filter(even, _)
    
    put_at_1 = put(1, _, _)
    m1 = put_at_1(42, {})
```

#### if-elif-else

```
// If condition must have else branch and might have zero or many elif branches
// if one of the branches succeeds result of it's last expression will be result of entire if expression

if <value_expression> then <code_block>
[{elif <value_expression> then <code_block>}]
else <code_block>

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


#### Pattern Matching

Pattern matching is a central element in Arza design
It used in function clauses, generic function specializations, let bindings before *=* token, lambda functions before -> token and
match expressions.
Arza doesn't have loops so pattern matching and recursion are used to create iteration

In function clauses, arguments are sequentially matched against patterns. If a match succeeds and the optional guard is true,
the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

In match expressions
match <value_expression>
 '|' <pattern>[when guard] = <code_block>
{'|' <pattern>[when guard] = <code_block> }

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
    // all patterns, but without when guard can be placed by the left hand side of = operator
    (x,y,z) = (1,2,3)

    {x, y=[1, 2, (d,e) of MyType, a, b, ...rest], z @ 1=42} =
        {x=17, y=[1,2, (MyType 3 4), 4, 5, 7, 8, 9], 1=42}
    // also in lambdas
    split = x::xs -> (x, xs)

    get_name = {name} -> name
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
in <code_block>

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
       io:print("x y z", x, y, z)
       sqrt(z + y + z)

// Lexical scopes in Let-in
fun f() =
    let
        x = 1
        y = 2
    in
        let
            x = 11
            y = 12
        in
            affirm:is_equal(x, 11)
            affirm:is_equal(y, 12)

        affirm:is_equal(x, 1)
        affirm:is_equal(y, 2)

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
catch <pattern> = <code_block>
[finally <code_block>]  |

try <value_expression>
catch
    | <pattern> [when guard] = <code_block>
    [{ <pattern> [when guard] = <code_block> }]
[finally <code_block>]


//Examples

try
    try
        1/0
    catch e1 = e1
catch e2 =
    try
        something()
        something_else()
    catch e3 =
        e3

try
    try
        1/0
    catch e1 = e1
    finally
        something()
        something_else()
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
Module system is very simple: module = file without any concept of multimodule package
Module search path are always relative to startup script and there are no possibility of relative import

Example directory structure
```
+-- program.arza
+-- __std__
|   +-- seq.arza
|   +-- lazy.arza
+-- my
|   +-- modules
|       +-- module1.arza
|       +-- module2.arza
|   +-- module1.arza
|   +-- module3.arza
```
if we run Arza with
```
python targetarza.py program.arza
```
Module search path would look something like  [BASEDIR, STD, ARZASTD] where

* BASEDIR = directory in which program.arza is located
* STD = BASEDIR/\_\_std\_\_ - directory with user defined std modules. It will give user easy way to have custom prelude
* ARZASTD = environment variable ARZASTD which must contain path to global stdlib. If ARZASTD is empty, all required modules must be in STD directory

#### Loading order
* prelude.arza. If prelude is absent execution will be terminated. All names declared in prelude would be visible in all other modules
* stdlib modules used by runtime (derive.arza, bool.arza, num.arza, bit.arza, env.arza, string.arza, symbol.arza, vector.arza, list.arza, function.arza, fiber.arza, trait.arza, tuple.arza, map.arza, seq.arza, lazy.arza, datatype.arza)
* running script (in our case program.arza). After loading this sript arza searches for function named 'main' and executes it. Result of 'main' function would be result of the program


