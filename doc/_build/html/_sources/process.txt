
Processes
=========

.. highlight:: arza

Arza is heavily inspired by Erlang and uses its idea of processes as a concurrency tool.

Processes or actors or symmetric coroutines are independent  universal primitives of concurrent computation.

They can exchange messages but can not share any data.

Arza syntax for process creation and message handling very similar to Erlang

::

    //to spawn process
    let pid = spawn(somefunc, args)

    // get pid of current process
    let this_pid = self()

    // to receive messages from other processes
    receive
        | clause1 = branch1
        | clause2 = branch2

    // to kill process
    close(pid)

Ping-Pong example

::
    
    // usefull functions
    import process

    type PingPongFinished(store)

    fun ping(n, pong_pid, store) =
        if n == 0 then
            // This is message sending
            pong_pid ! #finished
            store
        else
            // self() returns current pid
            pong_pid ! (#ping, self())
            receive #pong =
                    ping(n-1, pong_pid, #pong :: store)

    fun pong(store) =
        receive
            | #finished =
                // if excepion occures it became process result
                throw PingPongFinished(store)

            | (#ping, ping_pid) =
                ping_pid!#pong
                pong(#ping :: store)

        // this disables printing exceptions in processes to stderr
        process:set_error_print_enabled(pong_pid, False)
        let pong_pid = spawn(pong, ([],))
        // using currying just for clarity
        ping_pid = spawn .. ping .. (3, pong_pid, [])
        // waiting for all processes to end
        result = process:wait_for([pong_pid, ping_pid])
    in
        affirm:is_equal(result.[ping_pid], [#pong, #pong, #pong])
        affirm:is_equal(result.[pong_pid], ValueError([#ping, #ping, #ping]))
        // closing 
        close(pong_pid)
        close(ping_pid)

With symmetric coroutines  it's easy to implement asymmetric coroutines

::

    // function from std lib
    fun coro(fn) =
        let
            proc1 = self()
            proc2 = process:create()

            fun make_chan(pid) =
                fun (...args) =
                    if is_finished(pid) then
                        throw CoroutineEmpty(result(pid))
                    else
                        match args
                            | () = pid ! ()
                            | (m) = pid ! m
                        // receiving
                        receive msg = msg
            chan1 = make_chan(proc2)
            chan2 = make_chan(proc1)

            fun wrapper(...args) =
                let
                    (res =
                        (try
                            fn(...args)
                        catch e = e
                        )
                    )
                in
                    proc1 ! res
                    res

            fun _coro(...args) =
                if is_idle(proc2) then
                    start(proc2, wrapper, (chan2,) ++ args)
                    receive msg = msg
                else
                    chan1(...args)
        in
            _coro

    fun test_coro() =
        let
            fun test1() =
                let
                    c = process:coro(fun(yield, start) =
                        (let
                            x = yield(start)
                        in
                            yield(x)
                        )
                    )
                    c1 = process:coro((yield) -> #zero)
                in
                    affirm:is_equal .. c1() .. #zero
                    affirm:is_throw(c1, ())

                    affirm:is_equal .. c(#first) .. #first
                    affirm:is_equal .. c(#second) .. #second
                    affirm:is_equal .. c(#last) .. #last
                    affirm:is_throw(c, ())
                    affirm:is_throw(c, ())

            fun test2() =
                let
                    c = process:coro(fun(yield) = throw 1)
                in
                    affirm:is_equal .. c() .. 1
                    affirm:is_throw(c, ())
        in
            test1()
            test2()

With processes you can create emmulation of mutable state

Example: :ref:`mutable-state-label`