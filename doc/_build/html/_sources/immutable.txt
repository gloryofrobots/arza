
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
and if we have only standart function :code:`put` to work with our code would be very verbose

::

   let new_adress = "Zelena st. 20"
   let new_person = put(person,
                        #adresses,
                        put(person.adresses,
                            #homes,
                             cons(new_adress, person.adresses.homes)))

This code is hard to read and very error prone. Instead in Arza you can just write

::

   
   let new_adress = "Zelena st. 20"
   let new_person = person.{adresses.homes = cons(new_adress, @)}
   // Here @ placeholder means current path
   // in case of this example it will be person.addresses.homes

Syntax like :code:`object.property = value` impossible in Arza.

Instead you can use more powerfull modification syntax where you can add more than one change at once.
With this syntax you can also emulate :code:`+=` operator from imperative languages

Lets consider more complex examples

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
