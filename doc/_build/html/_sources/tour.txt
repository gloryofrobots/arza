Quick tour
==========

.. highlight:: arza

This is simple but absolutely useless program that help to illustrate some of the most important
Arza features

::

    import io (print)
    import affirm
    include list (range_to as range)
    import seq

    interface GetSet(I) =
        get(I, key)
        set(I, key, value)

    interface Storage(I) =
        contains(I, key)
        use get(I, key)
        use set(I, key, value)
        size(I)

    interface StorageKey(I) =
        use get(storage, I)
        use set(storage, I, value)

    interface Serializable(I) =
        serialize(storage of I, serializer)

    interface Serializer(I) =
        use serialize(storage, serializer of I)

    //abstract type


    type Nothing
    def str(s of Nothing) = "(novalue)"

    type First
    type Second
    type Third

    // parens here mean that this is record type
    // it will inherit standart behavior like at, put, has, ==, != ...etc
    type Collection()

    type Single is Collection
        (first)
        init(s) = s.{first = Nothing}

    def set(s of Single, k of First, val) =
        s.{first = val}

    def get({first} of Single, k of First) = first

    def size(s of Single) = 1

    //////////////////////////////////////////////////////////////

    type Pair is Single
        (second)
        init(p) =
            super(Single, p).{second = Nothing}

    // define trait and apply it immidiately to Pair
    trait TPair(T) for Pair =
        def set(s of T, k of Second, val) =
            s.{second = val}
        def get(s of T, k of Second) = s.second


    // cast Pair to its supertype Single
    def size(s of Pair) = size(s as Single) + 1

    //////////////////////////////////////////////////////////////

    type Triple is Pair
        (third)
        init(t) =
            super(Pair, t).{third = Nothing}

    trait TTriple(T) for Triple =
        def set(s of T, k of Third, val) =
            s.{third = val}
        def get(s of T, k of Third) = s.third


    def size(s of Triple) = size(s as Pair) + 1

    //////////////////////////////////////////////////////////////

    // lets create completely unrelated type to Single :> Pair :> Triple
    // but use traits for pair and triple to avoid code dublication

    type SecondAndThird is Collection (second, third)

    instance TPair(SecondAndThird)

    instance TTriple(SecondAndThird)

    def size(s of SecondAndThird) = 2

    //////////////////////////////////////////////////////

    type Dictionary is Collection (items)
        init(d) =
            d.{ items = {} }

    // do not subtype from Dictionary but use its structure
    type Array is Collection
        (size, ...Dictionary)
        init(s, size) =
            //silly idea of arrays implemented as lists
            s.{items = seq:consmany([], Nothing, size), size=size}

    // create anonymous trait and apply it serially to list of types
    trait (T) for [Dictionary, Array] =
        def size({items} of T) = len(items)

    trait TStorageWithItems(T, KeyType) =
        def set(s of T, k of KeyType, val) =
            s.{
                items = @.{ (k) = val }
            }

        def get(s of T, k of KeyType) = s.items.[k]

    instance TStorageWithItems(Dictionary, Symbol)
    instance TStorageWithItems(Dictionary, StorageKey)
    instance TStorageWithItems(Array, Int)

    //redefine array size to avoid list
    override (prev) size(a of Array) =
        a.size

    type InvalidKeyError is Error

    // redefine set function for Array
    // to avoid index out of range problems
    // prev is previous method
    // override expression do not adds this method to specific signature set(Array, Int)
    // but replaces it completely
    // so only indexes > 0 and < size will be accepted
    override (prev) set(arr of Array, i of Int, val)
        | ({size}, i, val) when i >= 0 and i < size = prev(arr, i, val)
        | (_, i, _) = throw InvalidKeyError(i)


    def ==(d of Dictionary, m of Map) = d.items == m

    def ==(m of Map, d of Dictionary) = d.items == m

    //////////////////////////////////////////////////////

    // define method for parent subtype
    def contains(s of Collection, k) =
        let val =
            // if method is not implemented for specific key it will throw NotImplementedError exception
            // we catch it and tell user key not exists
            try
                get(s, k)
            catch
                | e of NotImplementedError = Nothing
                | e = throw e

        match val
            | type Nothing = False
            | _ = True

    /// there are other more preferable way to implement such behavior
    //// this method will be called if specific get(Storage, Key) was undefined
    //// for example get(Single, Second) will otherwise crash with not implemented error
    def get(s of Collection, k of Any) = Nothing
    // after this declaration NotImplementedError will never be thrown in get generic



    //////////////////////////////////////////////////////

    //ensure that all types are satisfiing interface
    describe (Dictionary, Array, Pair, Triple, Single, SecondAndThird) as (Storage, GetSet)

    def serialize({first, second} of Pair, serializer of Dictionary) =
        serializer
            |> set(_, First, first)
            |> set(_, Second, second)

    def serialize(s of Triple, serializer of Dictionary) =
        serializer
            |> serialize(s as Pair, _)
            |> set(_, Third, s.third)

    def serialize(s of Array, serializer of List) =
        seq:concat(s.items, serializer)

    describe (Triple, Pair) as Serializable
    describe Dictionary as Serializer
    describe Array  as Serializable

    fun array_map({items} as arr, fn) =
        // lets pretend this Array implementation is not based on lists
        // and write some ridiculously slow map implementation
        // there are zip in seq module
        // but lets define our own here
        fun zip(seq1, seq2)
            | (x::xs, y::ys) = (x, y) :: zip(xs, ys)
            | (_, _) = []

        // same with foldl but here we call set directly
        fun fold
            | ([], acc) = acc
            | (hd::tl, acc) =
                let
                    (index, item) = hd
                    new_acc = set(acc, index, fn(item))
                in
                    fold(tl, new_acc)

        let
            arrsize = size(arr)
            indexes = range(arrsize)
        in
            fold(
                seq:zip(indexes, items),
                Array(arrsize)
            )


    fun test() =
        let
            single = Single()
                |> set(_, First, #one)

            pair = Pair()
                |> set(_, First, #one)
                |> set(_, Second, #two)

            triple = Triple()
                |> set(_, First, #one)
                |> set(_, Second, #nottwo)
                |> set(_, Third, #three)

            arr = Array(10)
                |> set(_, 0, #zero)
                |> set(_, 5, #five)
                |> set(_, 8, #eight)

            dict =
                Dictionary()
                |> set(_, #one, 0)
                // update
                |> set(_, #one, 1)
                |> set(_, #two, 2)
        in
            affirm:is_equal_all(
                get(single, First),
                get(pair, First),
                get(triple, First),
                #one
            )

            affirm:is_not_equal(get(triple,  Second), get(pair, Second))

            let
                dict1 = dict.{ items = @.{three = [1,2,3]} }
                //deeply nested update
                dict = dict1.{items.three = 0::@}
            in
                affirm:is_true(dict == {one=1, two=2, three=[0,1,2,3]})

            // this is old dict value
            affirm:is_true(dict == {one=1, two=2})
            let
                // lets try some function composition
                fn = (`++` .. "Val->") << str
                // this is equivalent to
                fn2 = (x) -> "Val->" ++ str(x)
                //where (args) -> expression is lambda expression
                arr_str = array_map(arr, fn)
                arr_str2 = array_map(arr, fn2)
            in
                affirm:is_equal(arr_str.items, arr_str2.items)

            let
                dict_ser = serialize(triple, dict)
            in
                affirm:is_true(dict_ser == {(First) = #one, (Second) = #nottwo, (Third) = #three,  one=1, two=2})

                // using func like infix operator
                affirm:is_true(dict_ser `contains` First)
                affirm:is_true(dict_ser `contains` #two)

            affirm:is_true(single `contains` First)
            affirm:is_false(single `contains` Second)
            affirm:is_true(pair `contains` Second)
            affirm:is_true(triple `contains` Third)

            let arr2 =
                try
                    set(arr, 10, 10)
                catch e of InvalidKeyError = Nothing
                finally
                    set(arr, 9, 42)

            affirm:is_true(get(arr2, 9) == 42)
