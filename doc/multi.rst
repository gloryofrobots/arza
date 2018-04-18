Interfaces and multimethods
===========================

.. highlight:: arza


Arza's approach to polymorphism is probably the most original part of the language

If you want to learn in details about multiple dispatch you can read excelent Eli Bendersky's articles
https://eli.thegreenplace.net/2016/a-polyglots-guide-to-multiple-dispatch/


Arza uses generic functions with multiple dispatch and intefaces that restricts and formalises relations
between types and generics.

Interfaces
----------

Interface is a term that most often is an attribute of object oriented system. It describes set of operations
that specific class can do.

But how can concept of interfaces can be applied to multimethods?
In Arza interface can be described as a set of generic functions and specific argument positions in this functions.

For example

::

   interface Storage =
      get(storage of Storage, key)

   interface Key =
      use get(storage, key of Key)

In example above we declare two interfaces that share the same generic function :code:`get`.

Expression :code:`storage of Storage` bind first argument of function :code:`get` to interface :code:`Storage`.

Interface :code:`Storage` will be implemented by all types that act like first arguments in :code:`get`.
Interface :code:`Key` will be implemented by all types that act like second arguments in :code:`get`.

The same code can be written in shorter way

::

   // all declarations are equivalent

   interface Storage =
      get(Storage, key)

   //here I is interface alias
   interface Storage(I) =
      get(storage of I, key)

   // or even shorter
   interface Storage(I) =
      get(I, key)


**Generic function can be declared only inside interface. They can not be declared twice**

::

   interface Storage =
      get(storage of Storage, key)

   interface Key =
      // this is error, function get already declared above
      get(storage, key of Key)
      // instead define reference with `use` expression
      use get(storage, key of Key)

Interfaces do not create namespaces, our function :code:`get`
will be available as :code:`get`, not as :code:`Storage:get`

**Generic function will dispatch only on arguments for whom interfaces are declared.**


Interfaces in Arza perform two important functions

* Formalisation of type behavior. Consider Arza's pattern matching.
  If custom type used as first argument in :code:`first` and :code:`rest` generics,
  it can be destructured by :code:`x::xs and [x, x1, ...xs]` patterns.

  Because in prelude  there is interface

  ::

    interface Seq =
        first(Seq)
        rest(Seq)

  Compiler just perform this check :code:`arza:is_implemented(customtype, Seq) == True`

  Also consider complex program with a lot of multimethods. In some point you may want to ensure that specific
  generics implemented for specifice types

* Limit number of arguments to perform multiple dispatch.
  Multiple dispatch is a costly procedure, especially for dynamic languages.
  Even with cache strategies substantial amount of methods can degrade performance.
  By limiting number of dispatch arguments compiler can more easily fall back to single dispatch.

  function :code:`put` has one of the biggest call rate in Arza
  and because this function defined only with one interface it's call time is more optimised

  ::

    interface Put(I) =
        put(I, key, value)

**One interface can have multiple roles in one generic function**

::

   interface Eq(I) =
      ==(I, I)
      !=(I, I)

Only types that have both first and second roles in **==** and **!=** generics will implement **Eq** interface

Interfaces can be concatenated

::

    interface Put(I) =
        put(I, key, value)

    interface At(I) =
        at(I, key)
        has(I, key)

    // you can combine interfaces
    interface Coll is (Put, At)


In some specific case there is a need to dispatch not on type of the argument but on argument value.
Example is the :code:`cast` function. 

::
   
    interface Cast(I) =
        cast(I, valueof to_what)

    interface Castable(I) =
        use cast(what, I)

To specify that we need to dispatch on value keyword :code:`valueof` is used.

Afterwards we can use it like

::

    import affirm

    type Robot(battery_power)

    def cast(r of Robot, type Int) = r.battery_power

    def cast(r of Robot, interface Seq) = [r as Int]

    def cast(r of Robot, interface Str) = "Robot"

    def at(s of Robot, el) when el == #battery_power  =
        // casting back to Record type to avoid infinite loop
        (s as Record).battery_power + 1


    fun test() =
        let
            r = Robot(42)
        in
            affirm:is_equal(r.battery_power, 43)
            affirm:is_equal(r as Int, 43)
            affirm:is_equal(r as Seq, [43])
            affirm:is_equal(r as Str, "Robot")

           
If concrete type defines custom method for :code:`at` generic
then to access it's internal structure you must cast it to parent Record type.
Like in example above

::

    def at(s of Robot, el) when el == #battery_power  =
        // casting back to Record type to avoid infinite loop
        (s as Record).battery_power + 1


Most of the times our programs can be easily implemented with single dispatch.
In some cases especially for mathematical operations  double dispatch is very usefull.
But sometimes there is a need for even bigger arity of dispatch function.

I never actually encounter them in my own work,
but here I found this example of :ref:`triple-dispatch-label` on the internet


Defining methods
----------------

To define new method for generic function use :code:`def` expression

::

   interface Num =
       //interface must be in both roles
       add(Num, Num)
       // only first argument
       sub(Num, other)


   type Vec2(x, y)

   def add(v1 of Vec2, v2 of Vec2) = Vec2(v1.x + v2.x, v1.y + v2.y)

   //However this would be an error
   // because we define second argument to have specific type
   def sub(v1 of Vec2, v2 of Vec2) = Vec2(v1.x - v2.x, v1.y - v2.y)

   // This is correct
   def sub(v1 of Vec2, v2) =
       match v2
       | Vec2(x, y) = Vec2(v1.x - x, v1.y - y)

Method definition can be simple function and two level functions but not case function.

Also method definition can have guards

::

    interface Racer(R) =
        race_winner(v1 of R, v2 of R)

    type Car (speed)
    type Plane (speed)

    fun faster(v1, v2) = v1.speed > v2.speed

    def race_winner(c1 of Car, c2 of Car)
        | (c1, c2) when faster(c1, c2)  = c1
        | (c1, c2) when arza:at(c1, #speed) < c2.speed = c2
        | (c1, c2) when c1.speed == c2.speed = c1

    // plane always wins
    // Double dispatch
    def race_winner(c of Car, p of Plane) = p

    def race_winner(p of Plane, c of Car) = p

There is a possibility to declare method not as function but as expression

::

   def somegeneric(t of Sometype) as someexpression()

   // often it's used with functions defined in native modules

   // native module
   import arza:_string

   // assign native functions as methods
   def slice(s of String, _from, _to) as _string:slice
   def drop(s of String, x) as _string:drop
   def take(s of String, x) as _string:take


Sometimes there is a need to override existing method

To do so use :code:`override` expression


::

    interface F =
        f1(F)

    def f1(i of Int)
        | 1 = #one
        | i = i

    // overriding
    // expression (_) after override means that we do not need previous method
    override(_) f1(i of Int) = 21

    // here we bind previous method to name super and call it in our new method
    override(super) f1(i of Int) = super(i) + 21

    // this can be done indefinitely
    override(super) f1(i of Int) = super(i) + 42


    type Val(val)

    // specifying builtin operator +
    def + (v1 of Val, v2 of Val) = v1.val + v2.val

    //overriding 
    override (super) + (v1 of Val, v2 of Val) = super(v1, v2) * 2

    fun test() =
        affirm:is_equal(signatures(f1), [[Int]])
        affirm:is_equal_all(f1(1), f1(0), f1(10000), f1(-1223), 84)

        let
            v1 = Val(1)
            v2 = Val(2)
        in
            affirm:is_equal((v1 + v2), 6)

Ensuring interface implementation
---------------------------------

After implementing all interface roles
type will put reference to interface in it's list of implemented interfaces.

But if there is a need to ensuring that this type(types) implements one or more interfaces you
can assert this with :code:`describe` expression.

::

   describe Symbol as  Concat

   describe String as (Eq, Repr,
        Len, Coll,
        Prepend, Append, Concat, Cons,
        ToSeq, Slice, Empty)

   describe (Triple, Pair) as Serializable

   describe (Dictionary, Array, Pair, Triple, Single, SecondAndThird) as (Storage, GetSet)

If some of the types does not implement even one of the interfaces then exception will be thrown.

Traits
------

Trait in Arza is a function that can work on types. This function consist of one or more
:code:`def instance override` expressions. :code:`instance` expression is a trait application to specific
number of types.

Traits are tools for code reuse and expressiveness.
If subtype-supertype relationship between types is unwanted traits can help to share behavior between them.

::

    // creating trait 
    // trait excepts two types and defines for them two methods
    trait TEq(T1, T2) =
        def equal (first of T1, second of T2) = first == second
        def notequal (first of T1, second of T2) = first != second


    // applying previously defined trait to couple of types
    instance TEq(Int, Int)
    instance TEq(Float, Float)
    instance TEq(Int, Float)
    instance TEq(Float, Int)


Arza has special syntax for applying trait immidiatelly after it's declaration

::
   
   
   trait TValue(T) for MyType =
       def val(v of T) = v.value

   // to apply this to trait to more than one type 

   trait TValue(T) for [MyType1, MyType1, MyType3] =
       def val(v of T) = v.value

   // in case of more arguments
   trait TEq(T1, T2) for (Int, Float) =
       def equal (first of T1, second of T2) = first == second
       def notequal (first of T1, second of T2) = first != second

    // or to cover all relations
   trait TEq(T1, T2)
           for [(Int, Float), (Int, Int), (Float, Float), (Float, Int)] =
       def equal (first of T1, second of T2) = first == second
       def notequal (first of T1, second of T2) = first != second

Anonymous traits
****************

If we do not care about reusing trait after declaration we can ommit trait name

::

   trait (T1, T2)
           for [(Int, Float), (Int, Int), (Float, Float), (Float, Int)] =
       def equal (first of T1, second of T2) = first == second
       def notequal (first of T1, second of T2) = first != second

   // applying anonymous trait to multiple types in serial order
   trait (T) for [Float, Int] =
       // applying trait inside trait
       instance TEq(T, T)
       def - (x of T, y) as _number:sub
       def + (x of T, y) as _number:add
