# Obin programming language

This repository contains prototype for experimental dynamically typed functional language


## Features
* Modern expressive functional syntax that resembles something between Erlang and F#.
* Handwritten, extensible, operator precedence parser with support of indentation layouts and juxtaposition operator
* User defined operators
* Builtin single dispatch engine with some interesting features (separation on trait,interface, generic function; dispatch not only on first argument)
* Support for partial application
* Stackless virtual machine
* Persistant data structures (lists, vectors, maps)
* Pattern matching, user defined types, union types, let-in, if-elif-else, clojures, try-catch-finally
* Assymetric coroutines

## Syntax
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
New line in expressions outside of free layout parens ( ) terminate expressions
except when last token in line is operator or one of(::, :::, :, ., =, or, and) 

Obin uses juxtaposition for function application. Obin syntax often looks like lisp without first layer of parens

```
func1 arg1 arg2 (func2 arg3 (func4 arg5 arg6) arg7) arg8 arg9
```

Obin functions not curried by default (mainly because in dynamic language currying may cause a lot of annoying runtime errors)
<!--- , shamelessly stolen from [Pixie](https://github.com/pixie-lang/pixie). --->

## Predefined types and literals
```
// this is comment
fun type_test () ->
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
    fun f x y ->
        z = x + y
        z + x * y
```

## Functions
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

```
