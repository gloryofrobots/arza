User types and subtyping
========================

.. highlight:: arza

In Arza programmer can define abstract and concrete types

Abstract types
--------------

::

   type None
   type Bool
   type One
   type LessThan
   type GreaterThan
   

Such types has an instances of themselves and can be used as singleton values
For example in ML family languages one could write

::

   data Maybe a = Just a | Nothing

in Arza it would be just

::

   type Maybe
   // this is subtyping
   type Nothing is Maybe
   type Just(val)  is Maybe

   // now use this type as pattern
   // all clauses will be successful here
   match Just(1)
   | maybe of Maybe
   | maybe of Just
   | {val} of Just
   | {val=1 as value} of Just
   // treating types as Tuples
   | Just(val)
   | Just(1)
   // Treating types as maps
   | Just{val=1 as value}

   match Nothing
   | maybe of Maybe
   | maybe of Nothing
   | type Nothing //need to distinguish between name and empy typeS
   // TODO make simpler type literal
   | x when x == Nothing

   // now  lets write some function
   fun operation(data) =
       if can_do_something(data) then
           let val = do_something(data)
           Just(val)
       else
           Nothing

Concrete types
--------------

Type :code:`Just` from example above is a concrete type. Such types when called like functions create records.
Records in Arza are something like structs in C or named tuples. Internally they differ from tuples because they
provide more efficient data sharing between mutated copies.

Records support both access by name and by field index.

It is forbidden to add new fields to records. You only create copy of existing ones with different values

::

    let t = (1, 2, 3)
    //this is highly undesirable
    let t1 = put(t, 0, 42)
    // instead
    type Three(x, y, z)
    let t2 = Three(1, 2, 3)
    // much more efficient
    let t3 = put(t2, 0, 42)

By default concrete types initalize fields in order of declaration in constructor, but programmer
can create custom initalizer. Such initializer is function defined with :code:`init` keyword.

Initializer receives uninitialized record as first argument and must set all of it's declared fields.
If any of the fields will not be set then exception will be thrown

::

   type Library(available_books, loaned_books)
        //initializer
        init(lib, books of List) =
             // here lib variable is an empty record with uninitialized fields
             // returning modified copy of lib
             lib.{available_books = books, loaned_books}

    // lets write function for borrowing book from library
    fun loan_book(library, book_index) =
        let book = library.available_books.[book_index]
        new_lib = library.{available_books = seq:delete(@, book), loaned_books = book::@}
        //return tuple with book and modified library
        (new_lib, book)

    // reverse process
    fun return_book(library, book) =
        library.{
              available_books = book::@,
              loaned_books = seq:selete(@, book)
        }

Subtyping
---------

Arza supports nominal subtyping for abstract and concrete types. Type can have only one supertype and
supertype can have multiple subtypes.

Concrete types can not be used as supetypes for abstract types.

Subtypes inherit behavior from supertypes and can be used in multiple dispatch in same roles.

When defining subtype from concrete supertype fields of supertype
will be added to fields of would be subtype

::

   type Vec2(x, y)
   type Vec3 is Vec2 (z)
   // Vec3 will have fields(x, y, z)
   // defining generic method
   def sum(v of Vec2) = v.x + v.y
   let v2 = Vec2(1, 2)
   let v3 = Vec2(1, 2, 3)
   // because sum not defined for Vec3
   sum(v2) == sum(v3)
   //but after
   def sum(v of Vec3) = v.x + v.y + v.z
   sum(v3) == 6 != sum(v2)

If you don't need behavioral subtyping but want to reuse fields from other types you can paste type in 
field declaration

::

   type Vec2 (x, y)
   // paste fields from Vec2
   type Vec3 (...Vec2, z)
   // Vec2 and Vec3 are unrelated 

   // More complex example
    type AB(a, b)
    type C(c)
    type DE(d, e)
    type FGH(f, g, h)

    // paste multiple types in multiple position
    type Alphabet (...AB, ...C, ...DE, ...FGH, i, j, k)