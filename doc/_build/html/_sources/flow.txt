
Conditions and pattern matching
===============================

.. highlight:: arza

If-elif-else condition
----------------------

If condition must have else branch and might have zero or many elif branches
if one of the branches succeeds result of it's last expression will be result of entire if expression

::

    //if as expression inside function call
    affirm:is_true(if 5 > 4 then True else False)
    fun f() =
        if something() then
            anything()
        elif something_else() == True then
            // series of expressions inside ()
            // equivalent to {} in C or Java
            io:print("I am here")
            nothing()
        else
            42

    // if-elif-else always evaluates to value
    let I1 = if 2 == 2 then 2 else 4
    let I2 =
        if 2 == 1 then 2
        elif 3 == 4 then 3
        elif {x=1, y=2} == (1,2,3) then 4
        else 5


Pattern matching
----------------

Pattern matching is key concept of Arza. It allows to write short and expressive programs.

Also using pattern matching  is the only way to bind value to a name.

There are no assignment in Arza.

Pattern matching  used in function clauses, generic function specializations,
let bindings before :code:`=` token, lambda functions before :code:`->` token,
:code:`catch`  and :code:`match` expressions.

Arza doesn't have loops so pattern matching and recursion are used to create iterative and recursive processes.

PM expressions can have one or more clauses delimited by | token 

::

    match [1,2,3,4]
        | 1::2::3::4::[] = #ok
        | x::xs = (x, xs)  

The expression after  :code:`match`  is evaluated and the patterns  are sequentially matched against the result
If a match succeeds and the optional guard is true, the corresponding body is evaluated.
If there is no matching pattern with a true guard sequence, runtime error occurs.

Example with guard

::

    match (1,2,3)
        | (x, y, z) when z == 2 = #first
        | (x, y, z) when z == 3 and y == 3 = #second
        | (x, y, z) when z == 3 and y == 2 and x == 3 = #third
        | (x, y, z) when z == 3 and y == 2 and x == 1 and A == 2 = #fourth
        | (x, y, z) when z == 3 and y == 2 and x == 1 and not (A `is` True) and greater_then_ten(9) = #fifth
        | (x, y, z) when z == 3 and y == 2 and x == 1 and A `is` True or greater_then_ten(11) = #sixth
        | _ = 12


Lets describe all possible patterns for pattern matching in arza
(Right sides ommited below, for clarity)

::

    match some_expression
        // underscore binds to anything
        | _ 

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

        // name binds value to variable and succeeds matching of this subbranch
        | x
        | SomeLONG_NAME


        // Tuples 
        | ()
        | (1)
        | (1,2,3)
        | (a, b, 42, ...rest)
        // ...rest will take rest of the tuple and put it into new tuple

        // [] destructs all types implementing Seq interface including List
        // ... destructs rest of the data structure
        // :: is cons operator
        | []
        | [1, 2, 3]
        | [1,2,3, x, (a,b,...rest_in_tuple), ...rest_in_list]
        | x::[]
        | 1::2::3::x::rest

        // {} destructs all types implementing Dict interface including Maps and Records
        | {}
        | {x}
        | {x="some value", y, z=42}


        // operator `of` restricts value to type or interface
        | x of Int
        | _ of List
        | {field1, field2=value2} of MyType

        // operator as binds value or expression to variable

        // expression will succeeds if map has key a=True and then it will bind it not to a name but to b
        | {a=True as b}

        | {genre, "actress"="Lily" as LilyName, age=13} as Result
        | 42 as i

        // when guard can be used to specify conditions for identical patterns
        | (a, (x, y, z)) when z == 3 and y == 2 and x == 1 and not (a == True)
        | (a, (x, y, z) when z == 4
        | (a, (x, y, z))

        // match types
        | type None 
        // if type here is omitted like
        | None it will bind everything to name None
        // interface
        | interface Seq
        // in case of concrete types
        //treating custom types as tuples
        | Vector3(x, y, z)
        //treating custom types as maps
        | Vector3{x, y, z}

All data structure pattern except tuples :code:`(n1, n2, ...n)` are accepting user defined data types that
implement specific protocols.

* To support patterns :code:`x::x1::xs` and :code:`[x, x1, ...xs]` type must implement :code:`Seq` interface

* To support :code:`{key1=value, key2=value}` type must implement :code:`Dict` interface

Some examples

::

    match {name="Bob", surname=("Alice", "Dou"), age=42}
        | {age=41, names} =  (name, age, 0)
        | {name, age=42} =  (name, age, 1)
        | {age=42} =  (age, 2)
        | _ =  42

    match (1, 2, 1)
        | (A, x, A)  = (#first, A)
        | (A, x, B)  = (#second, A, B)
        | (3, A) = #third

    match {x=1, y="YYYY"}
        | {x of String, y of Int} = #first
        | {x of Int, y="YY" of String} = #second
        | {x of Int, y="YYYY" of String} = #third

    match [1,2,3]
        | [a, b, c as B2] as B1 = (B1, B2, a, b, c)
        | _ = 42
    // result will be ([1, 2, 3], 3, 1, 2, 3)

let, let-in
-----------

Let, Fun, Let-in and match expressions are only ways to bind value to name.

Let expression binds names to values.
All patterns, but without  guards can be placed by the left hand side of = operator.

::

    let a = 1
    // checks if true
    let 1 = a

    // let creates layout and we can write multiple bindings at once
    let
        x::xs = [1,2,3]
        1 = x
        [2, 3] = xs

    // this expression will fail with MatchError
    let {x, y=2} = {x=1, y=3}

To avoid conflicts between names one can use let-in expression

Let-in creates nested, lexically-scoped, list of declarations
The scope of the declarations is the expressions after *let* and before *in*
and the result is the expression after *in*, evaluated in this scope

::
   
    let
        x = 1
    in
       let
           x = 2
       in
           x + 2
       x - 2
    

Also let in can be used as expression

::

    sum = 
        let
            x = 1
            y = 2
        in
            x + y


try-catch-finally
-----------------

Overall exception handling is very similar to imperative languages with difference that exceptions
are matched to catch clauses and if there are no successful branch ExceptionMatchError will be thrown

Any value can be used as exception in throw expression


::

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