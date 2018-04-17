Indentantions and layouts
=========================

.. highlight:: arza


Arza is indentation "aware" language

If you are familiar with a language like Python that also is whitespace sensitive,
be aware that that the rules for indentation in Arza are subtly different.

Arza syntax very similar to F# light syntax where indentation
used as statement and expression delimiter but instead of using simple
dedents and indents like in Python, Arza uses code layouts to determine block borders

::

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

    if x == 1 then
         2
    else 3
    
    fun add 
    | (1, 2) = 3
    | (x, y) = x + y

    match x
    | True = False
    | False =
         True

There are special rules for operators to continue expressions from line above,
which differs from F# syntax and more similar to Ruby syntax

::

    fun f() =
        1 +
        2 +
        3
        // returns 6

However this technique creates problem with ambidextra operators
(operators having have both prefix and infix binding powers)
Examples of such operators are - and (

To resolve parse conflicts Arza uses new lines as terminators

::

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


If you do not like to use indentation aware syntax at all, you can
enclose any block in ( and )

You can enclose in ( and ) almost any syntax construct and use  free code layout
without worrying about whitespaces.

::

    (fun f() =
            1
    +
    2 + 3)

    (interface Map
        put
            (key, value, Map)
    at
        (key,
        Map)
    )

If you need to use nested statements inside such free layout you must enclose each of them in ()

::

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

However because it is common pattern to use if or match expression inside function call
there are special support for such syntax

::

   add(match x
        | #one = 1
        | #two = 2
      //here comma terminates free layout and there are no need to enclose match in ()
      , 2)
      
   add(match x
        | #one = 1
        | val of Float =
           // but nested expressions must be enclosed
           (if val < 0.0 then abs(val)
           else val)
      //here comma terminates free layout and there are no need to enclose match in ()
      , 2)


