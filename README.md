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

# Big syntax Example

```
// this is comment
// multiline string literal
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
// keyword(prefix, infixr, infixl) operator, function name, precedence
// Custom operators

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

// Types
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
 | (left, top, right, bottom) of Rect -> left.x + right.y // . operator can access field from type instanve by field name

// Generic functions
// Generic function provides single dispatch

// == is name and x y is args of generic
// ` before x means that function will dispatch on its first argument
generic == `x y

generic max `first second
// or you can declare them in one layout

generic
    != `x y
    <= `x y
    mod `x y
    - `x y
    + `x y
    * `x y
    / `x y

    // dispatch argument at last position
    put key value `self
    at key `self
    del obj `self
    elem key `self

// Interfaces
// Interface determines if type implements one or more generic funtions
// generic functions used in interface must be declared at this point

// This is current list of standart prelude interfaces
interface
    PartialEq (==)
    Eq (!=, ==)
    Ord(<, <=, >, >=, cmp, max, min)
    Num (-, +, *, /, mod, negate)
    Pow(**)
    Str (str)
    Displayed (str, repr)
    Len (len)
    Sized (len, is_empty)
    Collection(put, at, del, elem)
    ReadOnlyCollection(at, elem)
    Seq(first, rest)
    Emptiable(empty)
    Consable(cons)
    Prependable(prepend)
    Appendable(append)
    Concatable(++)
    Dict(keys, values, put, at, del, elem)
    Indexed(index_of)
    Seqable(to_seq)
    Sliceable(slice, drop, take)
    Bounded(lower_bound, upper_bound)
    Ranged(range, range_by, range_from, range_from_by)
    Ref(!)
    MutRef(!, :=)


//operators implementation
//F# like currying operators
fun |> x f -> f x
fun <| f x -> f x
fun >> f g x -> g (f x)
fun << f g x ->  f (g x)

// operator as polymorphic function
trait MutRef for self of Ref
    def := self value
    
// almost all base operators like + - * / ..., are polymorphic functions
type Data value
extend Data
   with MutRef
     def := self value -> obin:mutable:put self #value value

trait Val for self
    def val self

type Option
    | Some val
    | None

extend Option
    with Val
        def val self ->
            match self with
                | x of Some -> x.val
                | x of None -> x

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

// simple right fold 
fun foldr func accumulator coll
    | f acc [] of Seq -> acc
    | f acc (hd::tl) of Seq -> f hd (foldr f acc tl)

// () is unit type (empty tuple). Every function must have at least one argument
fun test () ->
   // indentation is important but layouts are flexible
   // here lambda got called immediately 
   io:print (lam x y z ->
               a = x + y z
               b = a + 42
               b * 24
             end 1 2 3)
    // tuples
    (x,y,z) = (1,2.334353252,3)
    // lists
    let x::xs = [1,2,3,4,5] in
        affirm:is_equal x 1
        affirm:is_equal xs [2,3,4,5]
    //maps strings, and symbols
    Alice = {name="Alice", symbol_name = #Alice }
    Alice.name == ALice.symbol_name
    
    // = is not assignment, but matching, like in Erlang
    a = 1 // 1
    a = 2 // throws  
    1 = 1 // 1
    2 = 1 // throws 
    
    // Varname @ pattern binds result of pattern to variable Varname
    {a=[x,y,...z], B @ b="I am B", c of Float, D@d={e=(x,y,...zz)}} =
                               {a=[1,2,3,4,5], b="I am B", c=3.14, d={e=(1,2,3,4,5)}}
                    

    // If in call syntax function arguments lay on multiple lines,
    // we can use operator ` .` as in f . arg1 . arg2 which is the same as Haskell's $, 
    // but does not creates clojures or partial functions, instead it operates on ast level
    // Spaces are very important,
    // for example human.name translates to (obin:lang:at human #name)  and human . name to (human name)
    affirm:is_equal try
                        throw (1,2,"ERROR")
                    catch
                        | err @ (1, y, 3) -> #first
                        | (1,2, "ERROR@") -> #second
                        | err @ (1, 2, x) -> #third
                    finally ->
                        (#fourth, err, x)
                    end . // -> this is obin syntax for multiline arguments
                    (#fourth, (1, 2, "ERROR"), "ERROR")
    
    // another way to express multiline call is to use parens in lisp fashion
    (affirm:is_equal 
          (lam x y z
            | 1 2 3 -> 11
            | 2 4 5 -> 22
          end
                    1
                        2

                         3) 11)
    // conditions and layouts
    affirm:is_false if 5 == 4 then True else False
    affirm:is_equal (if 13 == 12 then 42 * 2 else if 13 == 14 then 12 * 2 else 1 end end) 1
    affirm:is_equal if x == 13 then 1 + 1
                    elif x == 14 then 2 + 2
                    elif x == 15 then 3 + 3
                    else 4 + 4 end . // -> ` .` syntax for multiline
                    8
    // pattern matching
    // function signature is mandatory
    fun f2 a | 0 -> 1
             | 1 -> 2
             | 2 -> 3
    
    match (1,2,3) with | (x,y,z) -> 2
                       | _ -> 1
                       
    fun prefix_of coll1 coll2
        | [hd, ...pre_tail] hd::tail -> prefix_of pre_tail tail
        | [] s -> True
        | [_, ..._] s -> False
    --------------------------------------------------
    // more than five ----- dashes interpreted as `end` token
    // [el, el2, ...tl] is equivalent to el1::el2::tl in pattern matching,
    // but it can be also used for tuples (el1, el2, ...tl)

// end here is not necessarry, it will be inserted automatically according to indentation layout
end 
// many more examples, such as abstract data types, lazy evaluation, transducers, traits
// can be found in obin_py/tests/obin
```

## Known problems
* Error reporting is very bad, it does more harm than good
* Obin has problem with prefix operator - 
    For example if you type
    ```io:print -1 ``` it will be interpreted as sexpr (- io:print 1)
    you need to  ```io:print (-1)``` instead
* Custom operators can be created but they will be exported only from prelude, if declared in other module they will remain local to it
* Lack of macros
* Lack of tail call elimination and other optimizations common to functional languages
* Because every function call in obin is trampolined as one VM loop iteration, there are no way to easily call obin code from native code
* Many things need to be optimized for speed and memory


Obin scripts are placed in test/obin, where
* obin_py/test/obin/\_\_lib__ folder contains obin stdlib
* obin_py/test/tests folder contains testing scripts

Some code (big enums, repeating blocks) generated from scripts in obin_py/generators.
Generation is not automatic, I manually run some script and copy paste it's stdout.

To run interpreter
```
cd obin_py 
python targetobin.py test/obin/main.obn
```
Program will run painfully slowly with stock python so I recomend using pypy instead
You may need pypy toolchain in the path. Look at ```obin_py/runobin.sh``` for details.
Obin does not compiles with RPython currently, but it can be done with some effort.


Obin may not have any practical interest but it may be usefull for people who begin to study compilers and virtual machines
Project split into two folders obin_c and obin_py. Folder obin_c is obsolete, I keep it with hope of return to the project at some time.