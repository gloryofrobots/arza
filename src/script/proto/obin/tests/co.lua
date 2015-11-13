 co = coroutine.create(function ()
           function send(i)
               return coroutine.yield(i)
            end

           for i=1,3 do
               v = send(i)
               print(i + v)

           end
     end)


v1, v2 = coroutine.resume(co, 10)
print(v1, v2)
v1, v2 = coroutine.resume(co, 10)
print(v1, v2)
v1, v2 = coroutine.resume(co, 10)
print(v1, v2)
v1, v2 = coroutine.resume(co, 10)
print(v1, v2)
v1, v2 = coroutine.resume(co, 10)
print(v1, v2)