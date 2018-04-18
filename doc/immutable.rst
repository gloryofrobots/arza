
Working with immutable state
============================

.. highlight:: arza

Modifications
-------------

Because all data in Arza immutable there is special need for support of deeply nested modifications
of data structures

Consider Map

::

   let person = {
      name = "Bob",
      addresses = {
        work="Vatutina st. 24/15",
        homes=["Gagarina st. 78", "Gorodotskogo st. 15"]
      }
   }

If we need to create new copy of this map with  new home address
and if we have only standart function :code:`put` to work with, code might be very verbose

::

   let new_adress = "Zelena st. 20"
   let new_person = put(person,
                        #adresses,
                        put(person.adresses,
                            #homes,
                             cons(new_adress, person.adresses.homes)))

This is hard to read and very error prone. Instead in Arza you can just write

::

   
   let new_adress = "Zelena st. 20"
   let new_person = person.{adresses.homes = cons(new_adress, @)}
   // Here @ placeholder means current path inside data structure
   // in case of this example it will be person.addresses.homes


Syntax like :code:`object.property = value` impossible in Arza.

Instead you can use more powerfull modification syntax where you can add more than one change at once.
With this syntax you can also emulate :code:`+=` operator from imperative languages

More complex examples

::

    fun test_map() =
        let
            d = {
                y = 2,
                s1 = {
                    (True) = False,
                    s2 = {
                        x = 1,
                        s3 = {
                            a = 10
                        }
                    }
                }
            }
            d1 = d.{
                s1.True = not @,
                s1.s2.x = @ + 1,
                s1.s2 = @.{
                    x=42,
                    z=24
                },
                s1.s2 = @.{
                    s3 = @.{
                        a = @ - 30,
                        b = 20
                    }
                },
                s1.s2.x = @ - 66,
                y = (@ +
                    @/2.0*@ *
                    seq:reduce([@, @, @], `+`)
                    ) + `*`(@, @)
            }
        in
            affirm:is_equal(d1, {y=18.0, s1={s2={z=24, x=-24, s3={b=20, a=-20}}, (True)=True}})

    fun test_list() =
        let
            d =[
                [0,1,2],
                3,
                4,
                [5,6,7, [8, 9, [10]]]]
            d1 = d.{
                0 = seq:map(@, (x) -> x * x),
                1 = @ * @,
                2 = @,
                (3).(3) = @.{
                    0 = @ * 8,
                    1 = @ * 9
                },
                (3).(3).((fun () = 2)()).0 = ((x) -> @ * x)(4.2)
            }
        in
            affirm:is_equal(d1, [[0, 1, 4], 9, 4, [5, 6, 7, [64, 81, [42.0]]]])

Default values
--------------


Arza does not support keyword arguments in functions, if you want to receive some kind of arbitrary options
you can use maps. However often in such option maps some keys must be set to default values.

Arza support special syntax for updating data structure value if it is absent


::

    let
        v = {x=1, y=2}
        // right side of or operator will be assigned to x
        // only if there are no previous value
        v1 = v.{x or 42, z or 42, y = 42}
        // the same works with lists, tuples and other data structs
        l = [0, 1, 2, 3]
        l1 = l.{0 or 5}
    in
        affirm:is_equal(v1, {y = 42, x = 1, z = 42})
        affirm:is_equal(l1, l)