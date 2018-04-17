Quick tour
==========

As quick tour of language lets define prelude (special namespace which be available for all modules)
and some simple programs
in file __std__/prelude.arza

.. highlight:: arza

              

Importing modules 

::

    // this module is defined internally
    // import statement does not load module as first class object
    // instead it binds all its names with _datatype: prefix
    import arza:_map 
    import seq
    import string
    // here specified names copied from arza:_types internal module
    include arza:_types (Any, Abstract, Record, Bool, Number, Symbol, String, List, Tuple)

Extending parser with custom operators

::

    // first name is operator, second is function which be used by compiler and third is precedence 
    infixl (<|, <|, 15)
    // right binding
    infixr (!, __send__, 15)
    infixl (|>, |>, 20)
    infixl (==, ==, 35)
    infixl (!=, !=, 35)
    infixl (+, +, 40)
    infixl (-, -, 40)
    infixl (.., .., 90)

    // prefix operators
    prefix (~, ~, 96)
    // cannot use - it is set for infix operator
    prefix (-, negate, 55)
    // some operators can not be defined because they have special meaning to parser
    // for example (: , .  ::) 

Lets describe common behavior, by defining interfaces with generics functions

::
    interface Eq(I) =
        ==(I, I)

Name I called interface alias and is significant in defining generics.
It tells that this argument will be polymorphic. Here == function will dispatch on two arguments.
In case it was written as ==(i, I) it will be dispatching only on second argument

Interfaces do not create namespaces so == function will be available as ==
and because we defined == infix operator above, we can write 1 == 2 and it will be
transformed into ==(1,2)

::
   
    interface NotEq(I) =
        // reusing already defined generic 
        use ==(I, I)

    interface Num(I) =
        +(I, I)
        -(I, I)

    interface Concat(I) =
        ++(I, I)

    // if interface does not define alias, interface name must be used instead
    interface Str =
        str(Str)

    interface Put(I) =
        put(I, key, value)

    interface At(I) =
        at(I, key)
        has(I, key)

    // you can combine interfaces
    interface Coll is (Put, At, Del)

Now lets define some of this generics for imported internal types
::
   
    // operator of defines dispatching type
    def at (m of Map, k) = _map:at(m, k)
    // second argument of at  can not be defined
    // because there are no interface for second argument
    // so this would be an error
    //def at (m of Map, k of String) = ...

    def put (m of Map, k, v) = _map:put(m, k, v)

    def str(m of Map) =
        let fun _joiner((fst, snd)) =
                str(fst) ++ "=" ++ str(snd)
        in "{"
                ++ string:join_with(", ", _map:to_list(m), _joiner) ++
            "}"

Using traits for code reuse and less typing.
Traits are functions operating on generics with side effects

::
    
    // creating trait 
    trait TEq(T1, T2) =
        def == (this of T1, other of T2) as _std:equal
        def != (this of T1, other of T2) as  _std:not_equal

    // applying previously defined trait
    instance TEq(Int, Float)
    instance TEq(Float, Int)

    // Anonymous trait if we are going to use it only once
    trait (T) for Record =
        // copying function from _datatype module 
        // this is more efficient then
        //def put (this of T, k, v) = _datatype:put(this, k, v)

        def put (this of T, k, v) as _datatype:put
        def at (this of T, k) as _datatype:at


    // applying anonymous trait to multiple types in serial order
    trait (T) for [Float, Int] =
        // applying trait inside trait
        instance TEq(T, T)
        def - (x of T, y) as _number:sub
        def + (x of T, y) as _number:add
