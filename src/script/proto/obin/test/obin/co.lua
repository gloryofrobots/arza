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


do
  local wrap, yield = coroutine.wrap, coroutine.yield

  local function putrev(w)
    if w then
      putrev(yield())
      io.write(w)
    end
  end

  function prevchar(s)
    local p = wrap(putrev)
    p"\n"
    string.gsub(s, ".", p)
    p()
  end

  -- don't look at this one until you understand the first one
  function prevword(s)
    local p = wrap(putrev)
    local function q(a, b) p(a) p(b) end
    p"\n"
    string.gsub(s, "(%S+)(%s*)", q)
    p()
  end

end