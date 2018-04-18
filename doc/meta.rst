
Metaprogramming
===============

.. highlight:: arza

Arza metaprogramming facilities are limited.

I have not decided yet if I want macroses in language or not.

Instead I borrowed concept of decorators from Python to generate functions and types at compile time.


Decorators
----------

Decorators are syntactic sugar borrowed from Python for function composition.

Decorators can be applied to functions, types, and methods

In case of decorating functions decorator is a function which recieves other function and optional list of arguments
and must return different function.

Example

::

    fun add1(fn, v) =
        fun (x, ...args) =
            // ...args will flush contents of a sequence into arguments
            fn(x+v, ...args)

    fun add2(fn, v1, v2) =
        fun (x, y) =
            fn(x+v1, y+v2)

    // applying decorators
    @add1(10)
    @add2(0.1, 0.2)
    fun f(x, y) = x + y

    // now f is functions decorated by to functions add1 and add2

    // decorators can be applied to specific methods
    interface I =
        add(I, I)

    @add1(10)
    @add2(0.1, 0.2)
    def add(x of Int, y of Int) = x + y

    @add1(10)
    def+(super) sub(x of Int, y of Int) =  super(x, y) + super(x, y)

    // decorators can be used in traits also
    trait Add(T) for Float =
        @add1(0.1)
        @add1(0.01)
        def add(x of T, y of T) = x + y

        @add2(0.001, 0.0001)
        def+ (super) add(x of T, y of T) = super(x, y) * -1

    // lets test our new functions
    affirm:is_equal_all(f(1,2), add(1,2), 13.3)
    affirm:is_equal(add(1.0, 2.0), -3.1111)


When decorating types decorator will receive tuple of three elements as first argument.

This tuple will consist of supertype, fields as list of symbols and initialisation function.

::

    // this decorator will add specific field to type fields if this field is not already there
    fun add_field ((supertype, fields, _init) as typedata, field) =
        if not has(fields, field) then
            (supertype, append(fields, field), _init)
        else
            typedata

    // this decorator will add field #y
    let add_y = add_field(_, #y)

    // this decorator will init specific field with value after initialisation 
    fun init_field((supertype, fields, _init), field, value) =
        let
            fun _wrap(...args) =
                let
                    data = _init(...args)
                in
                    data.{(field) = value}
        in
            (supertype, fields, _wrap)

    // this is almost the same like above but initialize field with special function
    fun init_field_with((supertype, fields, _init), field, value, fn) =
        let
            fun _wrap(...args) =
                let
                    data = _init(...args)
                in
                    data.{(field) = fn(@, value)}
        in
            (supertype, fields, _wrap)

    // Lets apply them to some types
    @add_field(#z)
    @add_y
    type XYZ(x)

    @add_field(#c)
    @add_field(#b)
    @add_field(#a)
    type ABC()


    @init_field(#b, #b)
    @init_field_with(0, #c, (x, y) -> x ++ y)
    @add_field(#b)
    type AB(a)
        init (ab, a) = ab.{a=a}

    type Sum(v)
        init (sum, x, y) =
            sum.{v = x + y}

    @extends(Sum)
    type Sum2

    // now we can test with

    let
        xyz = XYZ(1, 2, 3)
        abc = ABC(1, 2, 3)
        ab = AB(#a)
        sum1 = Sum(1,2)
        sum2 = Sum(1, 2)
    in
        affirm:is_equal_to_map(xyz, {x=1, y=2, z=3})
        affirm:is_equal_to_map(abc, {a=1, b=2, c=3})
        affirm:is_equal_to_map(ab, {a=#ac, b=#b})
        affirm:is_equal_all(sum1.v, sum2.v, 3)

