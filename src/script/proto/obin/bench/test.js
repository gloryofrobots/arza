fn assertEqual(value1, value2, msg) {
    if value1 != value2 {
        print(msg);
        raise msg;
    }
}

fn Human(_name, _id) {
    fn secret(val) {
        return val + 21
    }
    return {
        name: fn{
            return _name;
        },
        id: fn{
            return _id;
        },
        greetings: fn {
            return this.name() + " - " + _id;
        },
        memory : {
            secret: fn {
                return secret(21);
            }
        }
    }
}

h = Human("Bob", 42)
assertEqual(h.name(), "Bob", 'h.name(), "Bob",')
assertEqual(h.id(), 42, 'h.id(), 42')
assertEqual(h.greetings(), "Bob - 42", 'h.greetings(), "Bob - 42"')
assertEqual(h.memory.secret(), 42,'h.memory.secret(), 42')


fn fib(n) {
  fn _process(n,a,b) {
    return _process(n-1,b,a+b)  if n>0 else a;
  }
  return _process(n,0,1);
}

fn fib2(n) {
  a = 0
  b = 1
  t = nil
  while n > 0 {
    n -= 1
    t = a;
    a = b;
    b += t;
  }
  return a;
}

assertEqual(fib(10), fib2(11), 'fib(10) fib2(10)')

F = fn(msg) {
    f = fn {
        f2 = fn {
            return msg + " second"
        }
        return f2(msg) + " first"
    }
    return f(msg) + " zeros"
}

m = F("Hello world")
F.action = fn {
    print("OLOLO")
}

F.action()
return m

//

