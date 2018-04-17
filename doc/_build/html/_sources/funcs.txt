
Functions and partial application
=================================

.. highlight:: arza

Functions
---------

Functions are the most important part of any functional language.

In Arza function syntax somewhat similar to ML but has distinctly Erlangish attributes.
Main difference from Erlang is that in Arza arity is not part of the function definition.
So you can't create functions with same name and different arity.
This is conscious choice in language design. For example instead of defining three functions for ranges

::

    fun range(to)
    fun range(from, to)
    fun range(from, to, by)


Better to  name different processes differently

::

    fun range(to)
    fun range_from(from, to)
    fun range_by(from, to, by)

If functions with variadic arity are wanted one can use variadic arguments

::

    fun range(...args) =
        match args
        | (to) = // code here
        | (from, to) = // code here
        | (from, to, by) = // code here


Function in Arza can be viewed as :code:`match` operator applied to tuple of arguments

The same as with :code:`match` for :code:`fun` expression in clauses, arguments are sequentially matched
against patterns. If a match succeeds and the optional guard is true, the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

There are three different types of :code:`fun` expression

Simple function
***************

This is function with only one clause and optional guard

::

    fun any(p, l) = disjunction(map(p, l))

    fun all(p, l) =
         conjunction(map(p, l))

    fun print_2_if_greater(val1, val2) when val1 > val2 =
        io:print("first", val1)
        io:print("second", val2)

Case function
*************

This is function with multiple clauses

::

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

Two level function
******************

This is function that combines syntax of previous two.
It is a syntactic sugar for common problem of saving first state in deeply recursive processes
and also for performing some checks only once

Consider, for example this problem

::

    // this function creates inner function and applies it to all it's arguments
    // because it does not want to check all types every iteration and also
    // it saves coll from first call
    fun scanl(func of Function, accumulator of Seq, coll of Seq) =
        fun _scanl
            | (f, acc, []) = acc :: empty(coll) // coll contains initial value from first call
            | (f, acc, hd::tl) = acc :: scanl(f, f(hd, acc), tl)
        in _scanl(func, accumulator, coll)

    //In Arza there is special syntax for such operation

    fun scanl(func, accumulator, coll)
        | (f, acc, []) = acc :: empty(coll)
        | (f, acc, hd::tl) = acc :: scanl(f, f(hd, acc), tl)

    // it is compiled to
    fun scanl(func, accumulator, coll) =
        let
            fun scanl
                | (f, acc, []) = acc :: empty(coll) // coll contains initial value from first call
                | (f, acc, hd::tl) = acc :: scanl(f, f(hd, acc), tl)
        in scanl(func, accumulator, coll)
    // so when recursion calls scanl it will calls inner function not outer

Some function examples

::

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


Partial application
-------------------


Arza has special syntax for partial application 

::

    // underscores here called holes
    let add_2 = add(_, 2)
    5 = add_2(3)
    let sub_from_10 = sub(10, _)
    5 = sub_from_10(5)
    
    // you can use more than one hole 
    let foldempty = foldl(_, [], _)


Also there is builtin function curry which receives normal function and returns carried version

::

    carried_add = curry(add)
    3 = carried_add(1)(2)
    
    // in prelude there are two operators
    //prefix
    fun ~ (func) = curry(func)
    3 = ~add(1)(2)
    //infix
    fun .. (f, g) = curry(f)(g)
    3 = add .. 1 .. 2

Because all data immutable in Arza, partial application and currying
combined with pipe and composition operators is often the best
way to initialize complex data structures or perform chain of operations.

::

    //from prelude
    infixl (<|, <|, 15)
    infixl (|>, |>, 20)
    infixl (<<, <<, 25)
    infixl (>>, >>, 25)

    fun |>(x, f) = f(x)
    fun <|(f, x) = f(x)
    fun >>(f, g) = x -> g(f(x))
    fun <<(f, g) = x -> f(g(x))

    
    fun twice(f) = f >> f
    fun flip(f) = (x, y) -> f(y, x)


    //now we can do
    let
        l = list:range(0, 10)
    in
        affirm:is_equal (
            l |> seq:filter(_, even),
            [0, 2, 4, 6, 8]
        )

        affirm:is_equal(
            l |> flip(seq:filter) .. even
              |> flip(seq:map) .. (`+` .. 1),
             [1, 3, 5, 7, 9]
        )

        affirm:is_equal (
            l |> seq:filter(_, even)
              |> seq:map(_, `+` .. 1)
              |> seq:map(_, flip(`-`) .. 2),
            [-1, 1, 3, 5, 7]
        )

        affirm:is_equal(
            l |> flip(seq:filter) .. (even)
              |> flip(seq:map) .. (`+` .. 1)
              |> flip(seq:map) .. (flip(`-`) .. 2),
            [-1, 1, 3, 5, 7]
        )

        affirm:is_equal(
            l |> seq:filter(_, even)
              |> seq:map(_, `+`(1, _))
              |> seq:map(_, ~(flip(`-`))(2)(_)),
            [-1, 1, 3, 5, 7]
        )

        let
            square = (x -> x * x)
            triple = `*` .. 3
        in
            affirm:is_equal (
                l |> seq:filter(_, even)
                  |> seq:map(_, `+` .. 1)
                  |> seq:map(_, flip .. `-` .. 2)
                  |> seq:map(_, triple >> square),
                [9, 9, 81, 225, 441]
            )

            affirm:is_equal (
                 (seq:filter(_, even)
                     >> seq:map(_, `+`(1, _))
                     >> seq:map(_, flip(`-`)(2, _))
                     >> seq:map(_, triple >> square))(l),
                 [9, 9, 81, 225, 441]
            )

            affirm:is_equal (
                l |> seq:filter(_, even)
                  >> ~(flip(seq:map))(`+` .. 1)
                  >> seq:map(_, flip(`-`)(2, _))
                  >> ~(flip(seq:map))(triple >> square),
                [9, 9, 81, 225, 441]
            )




