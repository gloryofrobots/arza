Code examples
=============

Simple game
-----------

.. code-block:: arza

               
    // This is simple battleship game
    // All ships have 1x1 size and they don't move throughout course of the game
    // gameplay consists of random shooting by each of the ships

    // module imports
    // print functions
    import io
    // sequence combinators
    import seq
    import string
    // test assertions
    import affirm

    // type declaration
    type Ship(id, hp, pos)

    // defining method for generic function str which will be called by print function

    def str({id, hp, pos} of Ship) =
        // Arza lacks sprintf for now, instead this is simple concatenation
        string:all("<Ship id=", id, " hp=", hp, " pos=", pos, ">")

    // Other type with initializer
    // Product of this type will be value which initializer returns
    type Game(cols, rows, ships, _id)
        init(game, cols, rows) =
            game.{
                // field attrs
                rows = rows,
                cols = cols,
                // list with ships, list is not a best type of data structure here but the simplest one
                ships=[],
                // special id increment for new ships
                _id=0
            }

            
    def str({rows, cols, ships} of Game) =
        string:all(
            "<Game (",
            rows,
            ", ",
            cols,
            ") ",
            // if is an expression like almost everything
            if not is_empty(ships) then "ships: \n...." else "",
            string:join("\n....", ships),
            " >"
        )

    // checking if position is on board
    fun is_valid_pos({rows, cols}, (x, y) as pos) =
        x >= 0 and x < cols and y >= 0 and y < rows

    // add ship and return new game record
    // because values are immutable in arza
    fun add_ship(game, pos) =
        // increment id counter
        let new_id = game._id + 1
        // create new ship with 2 hit points
        let ship = Ship(new_id, 2, pos)
        // .{ operator allows to create modified immutable structure
        // here we creating new instance of Game from old one with changed keys _id and ships
        // @ placeholder means previous value and :: is cons operator
        game.{
            _id = new_id,
            ships = ship::@
            // can be written as
            // ships = cons(ship, @)
        }


    // using seq module for finding ship at pos ship_pos
    fun atpos({ships} of Game, ship_pos) =
        // function arguments are subjects of pattern matching
        // {ships} of Game means argument must be of type Game
        // and must implement Map interface and has attribute ships
        // binding ships will be created
        seq:find_with(
            ships,
            // default value
            None,
            //lambda expression
            ship -> ship_pos == ship.pos
        )


    fun update_ship(game, newship) =
        // modifing game.ships
        game.{
            ships = seq:map(
                // equivalent to game.ships
                @,
                // using parens to delimit multi expression function
                (fun(ship) =
                    (if ship.id == newship.id then
                        newship
                    else
                        ship))
            )
        }


    // fire at random position
    fun fire({rows, cols} as game, ship) =
        let
            x = randi(0, rows)
            y = randi(0, cols)
            fire_pos = (x, y)

        if fire_pos == ship.pos then
            //retry
            fire(game, ship)
        else
            fire_at(game, ship, fire_pos)


    // as operator in pattern matching will bind left value to right name in case of successful branch
    fun fire_at({rows, cols, ships} as game, ship, fire_pos) =
        let enemy = atpos(game, fire_pos)
        // if we found enemy change its hp
        // this all immutable of course, so we return new game state
        match enemy
            | enemy of Ship =
                update_ship(game, enemy.{hp = @ - 1})
            | None =
                game


    fun turn({rows, cols, ships} as game) =
        // this basically foreach through all ships
        // foldl is used because we can put current state as accumulator
        /*
            foldl is basically this function
            fun foldl
                | ([], acc, f) = acc
                | (hd::tl, acc, f) = foldl(tl, f(hd, acc), f)
        */
        seq:foldl(
            ships,
            game,
            fun (ship, new_game) =
                fire(new_game, ship)
        )


    // win conditions
    // all ships are dead then draw
    // if one ship alive she is the winner
    // else continue playing
    fun checkgame(game) =
        let (alive, dead) = seq:partition(game.ships, fun({hp}) = hp > 0 )
        match alive
            | [] = (game, (#DRAW, "All dead"))
            | x::[] = (game, (#WINNER, x))
            | _ = None


    // This game main loop
    // This type of function is called recursive wrappers in arza
    // first branch will be executed only once
    // and subsequent calls will not check when count > 0 guard
    fun run(game, count) when count > 0
        | (game, 0) = (game, (#DRAW, "Time is out"))
        | (game, count_turns) =
            let game1 = turn(game)
            match checkgame(game1)
                | None = run(game1, count_turns - 1)
                | result = result


    // just simple random game 
    fun random_game() =
        let
            size = 4
            pos = () -> randi(0, size)
            (game, result) = Game(size, size)
                    |> add_ship(_, (pos(), pos()))
                    |> add_ship(_, (pos(), pos()))
                    |> run(_, 100)
        io:p(#GAME, game)
        io:p(#RESULT, result)


    // and some testing
    fun test() =
        fun test_game() =
            let game = Game(4, 4)
                    |> add_ship(_, (3,1))
                    |> add_ship(_, (0,0))
            let ship1 = atpos(game, (3, 1))
            let ship2 = atpos(game, (0, 0))
            (game, ship1, ship2)

        let
            (game, ship1, ship2) = test_game()
        in
            let
                (game1, result) = game
                    |> fire_at(_, ship1, ship2.pos)
                    |> fire_at(_, ship2, ship1.pos)
                    |> fire_at(_, ship1, ship2.pos)
                    |> fire_at(_, ship2, ship1.pos)
                    |> checkgame(_)
            in
                affirm:is_equal(result.0, #DRAW)

        let
            (game, ship1, ship2) = test_game()
        in
            let
                (game1, (label, winner)) = game
                    |> fire_at(_, ship1, ship2.pos)
                    |> fire_at(_, ship2, ship1.pos)
                    |> fire_at(_, ship1, ship2.pos)
                    |> checkgame(_)
            in
                affirm:is_equal(label, #WINNER)
                affirm:is_equal(winner.id, ship1.id)

Mutable State
-------------

.. code-block:: arza

    // this program will implement mutable state via processes

    import process
    import decor

    type State(pid)

    // special error
    type StateError is Error

    // because State will implement at generic all calls like state.key or
    // matches {key1, key2} will be infinitely recursive
    // to avoid this we need to cast state to parent Record type
    // asrecord defined in prelude like fun asrecord(r) = r as Record
    fun pid(s) = asrecord(s).pid


    fun is_valid(s) =
        not process:is_finished(pid(s))

    fun __ensure_process(s) =
        if not is_valid(s) then
            throw StateError("Process inactive")
        else
            s

    // creating assertion decorators as partially applied function decor:call_first
    let ensure1 = decor:call_first(_, 1, __ensure_process)
    let ensure2 = decor:call_first(_, 2, __ensure_process)
    let ensure3 = decor:call_first(_, 3, __ensure_process)

    // trait is function which can operate on types
    // traits have global side effects
    // they used to specify behavior for one or more types
    // and can be applied to different set of types with 'instance' expression
    // this is anonymous trait. They are used just for convinience to avoid typing long type names

    // generic functions at, put has specific meaning in arza because expression
    // x.y transforms by compiler into at(x, #y) and x.{y=1} into put(x, #y, 1)
    trait (T) for State =
        // T means State
        def close(s of T) =
            process:kill(pid(s), 0)

        // all ensure decorators assert that state process is not dead
        @ensure3
        def put(s of T, key, value) =
            // sending tuple to process
            // #put is symbol specifiing type of action
            pid(s) ! (#put, key, value)
            // returning itself
            s

        @ensure2
        def at(s of T, key) =
            // sending request
            pid(s) ! (#at, self(), key)
            // and receiving reply
            receive (#at, val) = val

        @ensure1
        def &(s of T) =
            pid(s) ! (#get, self())
            receive (#get, val) = val

        @ensure2
        def := (s of T, val) =
            pid(s) ! (#set, val)
            s

        @ensure2
        def del(s of T, el) =
            pid(s) ! (#del, el)
            s

        @ensure2
        def has(s of T, el) =
            pid(s) ! (#has, self(), el)
            receive (#has, val) = val

        @ensure1
        def arza:len (s of T) =
            pid(s) ! (#len, self())
            receive (#len, val) = val

        @ensure2
        def ==(s of T, data) = &s == data

        @ensure1
        def arza:is_empty(s of T) = len(s) > 0


    // this is actual process
    fun _loop(data) =
        // this block will receive messages from other processes
        receive
            | (#set, new_data) =
                // just replace data
                _loop(new_data)

            | (#get, pid) =
                // receiving action with receiver
                // replying to receiver
                pid ! (#get, data)
                // going to loop again because otherwise process will be finished
                _loop(data)

            | (#at, pid, key) =
                pid ! (#at, data.[key])
                _loop(data)

            | (#has, pid, key) =
                // calling has generic func  as has operator
                pid ! (#has, data `has` key)
                _loop(data)

            | (#len, pid) =
                pid ! (#len, len(data))
                _loop(data)

            | (#put, key, val) = _loop(data.{(key)=val})

            | (#del, key) = _loop(del(data, key))
            | msg = throw (#InvalidMessage, msg)

    //constructor function
    /*
        you can use this module like
        import state
        let s = state:new({x=1, y=2, z=3})
        updates state structure
        s.{x=2}
        replaces state value
        s:=1
    */
    fun new(data) =
        let pid = spawn(_loop, data)
        State(pid)

Triple Dispatch
---------------

.. code-block:: arza

    import seq

    //case for triple dispatch described here https://softwareengineering.stackexchange.com/questions/291525/a-real-world-use-case-for-triple-dispatch
    //
    //This program represents a repository of citation information, containing books, articles and journals
    //with action of formatting those books for consumption on demand.
    //
    //Let's take two approaches to formatting. National Library of Medicine (derived from the Vancouver Project)
    //specifies citations in a particular way, mostly affecting how author names are laid out.
    //NLM differs from American Psychological Association (APA) formatting.
    //
    //Also we have to publish these citations and choice of outputs are: plain text, PDF, HTML.
    //Some of these items require different layout strategies,
    //depending on the type of the format (APA indents following lines, NLM doesn't).

    // Declaring interfaces

    interface Repo(I) =
        add(I, item)

    interface Source(I) =
        format(item of I, format_standart, output_format)

    interface Standart(I) =
        use format(item, format_standart of I, output_format)

    interface Output(I) =
        use format(item, format_standart, output_format of I)

    fun format_books(library) =
        let books = seq:map(library.books, format)

    // Declaring types

    type Item(author, name)
    type Record(id, item)
    type Book is Item
    type Article is Item
    type Journal is Item

    type FormatStandart
    type NLM is FormatStandart
    type APA is FormatStandart

    type OutputFormat
    type PDF is OutputFormat
    type HTML is OutputFormat
    type TXT is OutputFormat

    type Library(_id, items)
        init(l) =
            l.{items = []}

    // Defining generic functions

    def add(l of Library, item) =
        let id = l._id + 1
        l.{
            id = _id,
            items = Record(id, item)::@
        }


    def format(b of Book, c of NLM, f of TXT) = None // do something here
    def format(b of Article, c of NLM, f of TXT) = None // do something here
    def format(b of Journal, c of NLM, f of TXT) = None // do something here

    def format(b of Book, c of APA, f of TXT) = None // do something here
    def format(b of Article, c of APA, f of TXT) = None // do something here
    def format(b of Journal, c of APA, f of TXT) = None // do something here

    // and so on and so on              


Some sequence functions
-----------------------

.. code-block:: arza

    fun foldl
        | ([], acc, f) = acc
        | (hd::tl, acc, f) = foldl(tl, f(hd, acc), f)


    fun foldr
        | ([], acc, f) = acc
        | (hd::tl, acc, f) = f(hd, foldr(tl, acc, f))


    fun reduce(sq, f)
        | (x::xs, f) = foldl(xs, x, f)
        | ([], f) = throw EmptySeqError(sq)


    fun map(sq, f)
        | ([], f) = empty(sq)
        | (hd::tl, f) = f(hd) :: map(tl, f)


    fun filter(sq, predicate)
        | ([], p) = empty(sq)
        | (x::xs, p) =
            if p(x) then
                x :: filter(xs, p)
            else
                filter(xs, p)


    fun sort(s, f) =
        let
            fun _merge
                | ([], ys) = ys
                | (xs, []) = xs
                | (x::xs, y::ys) =
                    if f(x, y) then x :: _merge(xs, y::ys)
                    else y :: _merge(x::xs, ys)

            fun _sort
                | [] = []
                | [x] as s = s
                | xs =
                    let (ys, zs) = split(xs)
                    in _merge(_sort(ys), _sort(zs))

        in _sort(s)


    fun zip(seq1, seq2)
        | (x::xs, y::ys) = (x, y) :: zip(xs, ys)
        | (_, _) = []


    fun unzip(l) =
        let fun _unzip
            | ((x, y) :: ts, xs, ys) = _unzip(ts, x :: xs, y :: ys)
            | ([], xs, ys) = (reverse(xs), reverse(ys))

        in _unzip(l, [], [])


    fun zipwith(seq1, seq2, f)
        | (x::xs, y::ys, f) = f(x, y) :: zipwith(xs, ys, f)
        | (_, _, _) = []


    fun span(sq, predicate)
        | ([], p) =
            let c = empty(sq)
            in (c, c)
        | ([x, ...xs1] as xs, p) =
            if not(p(x)) then
                (empty(sq), xs)
            else
                let (ys, zs) = span(xs1, p)
                in (x::ys, zs)