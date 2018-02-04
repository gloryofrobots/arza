
Prototypes for experimental programming languages.
Each language exists in separate branch instead of separate repository and the master branch contains only this README.
Also each branch has it's own README with more detailed language description.
For more information you can go to ```./test/{LANGNAME}/``` and examine tests and some simple programs. 

Arza is my latest and most developed language at this moment. I intent to write native interpreter for Arza or for one of it's descendants later.

- [Arza](https://github.com/gloryofrobots/langs/tree/arza) 
- [Obin](https://github.com/gloryofrobots/langs/tree/obin)
- [Lalan](https://github.com/gloryofrobots/langs/tree/lalan)


#### Common features for all branches

* All code written in Python (the result is easy to experiment with but very slow interpreter)
* Functional
* Unpure
* Eager
* Immutable
* Dynamic
* Experimental syntaxes
* Persistent data structures (lists, tuples, maps)
* Pattern matching inspired by Erlang and ML
* Lexical clojures and lambdas
* Usual number of primitives (if-else, let-in, try-catch)
* User defined operators
* User defined types
* Various level of support for currying and partial application
* Custom operators
* Stackless virtual machine
* Asymmetric coroutines


#### [Arza](https://github.com/gloryofrobots/langs/tree/arza)

* Laconic indentation aware syntax inspired by F# light, Python and Lisp 
* Powerfull predicate multiple dispatch generic functions
* Interfaces supporting multiple dispatch paradigm
* Support for partial application via special syntax


```
// some seq module functions 
fun span(predicate, coll)
    | (p, []) =
        let c = empty(coll)
        in (c, c)
    | (p, xs@[x, ...xs1]) =
        if not(p(x)) then
            (empty(coll), xs)
        else
            let (ys, zs) = span(p, xs1)
            in (x::ys, zs)

fun sort(f, s) =
    let
        fun _merge
            | ([], ys) = ys
            | (xs, []) = xs
            | (x::xs, y::ys) =
                if f(x, y) then x :: _merge(xs, y::ys)
                else y :: _merge(x::xs, ys)

        fun _sort
            | [] = []
            | s @ [x] = s
            | xs =
                let (ys, zs) = split(xs)
                in _merge(_sort(ys), _sort(zs))

    in _sort(s)


fun sort_asc(s) = sort(`<=`, s)

fun sort_desc(s) = sort(`>=`, s)

// list range_by 

fun range_by (first of Int, last of Int, step of Int) =
    let fun _range_by
        | (N, X, D, L) when N >= 4 =
            let
                Y = X - D
                Z = Y - D
                W = Z - D
            in
                _range_by(N - 4, W - D, D, W :: Z :: Y :: X :: L)

        | (N, X, D, L) when N >= 2 =
            let Y = X - D
            in _range_by(N - 2, Y - D, D, Y :: X :: L)

        | (1, X, _, L) = X :: L

        | (0, _, _, L) = L
    --------------------------------------------------
    in
        if step > 0 and first - step <= last or
            step < 0 and first - step >= last then

            let n = ((last - first + step) / step) - 1
            in _range_by(n, (step * (n - 1) + first), step, [])

        elif step == 0 and first == last then
            _range_by(1, first, step, [])
        else
            throw (#InvalidRange, first, last, step)

// Arza generic functions and interfaces
// declare interface with generic functions

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

def add(c of Complex, i of Int) when i == 0 = c
	
// You can use any value expression in predicate including function call
interface Fav =
    get_favorite(c1, c2)

type Car (speed)

fun faster(v1, v2) = v1.speed > v2.speed

def get_favorite(c1 of Car, c2 of Car) when faster(c1, c2)  = c1
def get_favorite(c1 of Car, c2 of Car) = c2
```

#### [Obin](https://github.com/gloryofrobots/langs/tree/obin)

* Indentation-aware syntax inspired by F#, Haskell and Python
* Juxtaposition used for function application
* Automatic currying
* Union types (like ADT, but in dynamic language their usefulness somewhat diminished)
* Lazy evaluation via special syntax
* Smart way of handling ambidextra operators
* Single dispatch polymorphism with ability to create interfaces and open methods separatly from each other
```
fun foldl
    | f acc [] -> acc
    | f acc hd::tl -> foldl f (f hd acc) tl

fun foldr
    | f acc [] -> acc
    | f acc hd::tl -> f hd (foldr f acc tl)


fun split s
    | [] -> ([], [])
    | s@[x] -> (s, [])
    | x::y::xs ->
        (l, r) = split xs
        (x::l, y::r)

fun sort f s ->
    fun _merge s1 s2
        | [] ys -> ys
        | xs [] -> xs
        | x::xs y::ys ->
            if f x y then x :: _merge xs (y::ys)
            else y :: _merge (x::xs) ys

    fun _sort s
        | [] -> []
        | s @ [x] -> s
        | xs ->
            (ys, zs) = split xs
            _merge (_sort ys) (_sort zs)

    _sort s
----------------------------------------

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
--------------------------
```

#### [Lalan](https://github.com/gloryofrobots/langs/tree/lalan)

* Clean syntax inspired by Lua and OCaml (whitespace unaware, common syntax for basic expressions)
* Using parentheses for creating blocks of expression, similar to {} blocks in C or Java
* Support for partial application via special syntax
* Name binding only via let-in expression
* Single dispatch based on protocols, with ability to reuse methods from one protocol in definition of other

```
fun add(x,y) = x + y

// more the one expression can be enclosed in parenthesis
// the result of such expression is the result of last expression
fun add_and_print(x,y) =
(
    io:print("x + y", x + y)
    x + y
)
fun foldl
    | (f, acc, []) = acc
    | (f, acc, hd::tl) = foldl(f, f(hd, acc), tl)


fun foldr
    | (f, acc, []) = acc
    | (f, acc, hd::tl) = f(hd, foldr(f, acc, tl))

fun split
    | [] = ([], [])
    | s@[x] = (s, [])
    | x::y::xs =
        let (l, r) = split(xs)
        in (x::l, y::r)


fun sort(f, s) =
    let
        fun _merge
            | ([], ys) = ys
            | (xs, []) = xs
            | (x::xs, y::ys) =
                if f(x, y) then x :: _merge(xs, y::ys)
                else y :: _merge(x::xs, ys)

        fun _sort
            | [] = []
            | s @ [x] = s
            | xs =
                let (ys, zs) = split(xs)
                in _merge(_sort(ys), _sort(zs))

    in _sort(s)

fun enum_from(num) =
    let co = coro:spawn(
        fun(yield, _from) =
            let
                fun _looper(num) =
                (
                   yield(num)
                   _looper(num + 1)
                )
            in
            (
                yield(_from)
                _looper(_from)
            )
        )
    in
    (
        co(num)
        co
    )

```


