fn fo() {
    x = 3
    y = 4
    fn _f() {
        outer x,y
        x = 1
        y = 2
        [x, y]
    }

   print(_f())
   print(x, y)
}

fo()

fn fib(n) {
  fn _process(n,a,b) {
    _process(n-1,b,a+b) if n>0 else a;
  }
  _process(n,0,1);
}

print(fib(25))

print("*******")
fn yfib(x) {
    coroutine(fn(yield) {
      for i in range(0, x) {
        yield(fib(i))
      }
      fib(x)
    })
}

f = yfib(9)

for i in f {
  print(i)
}
print("*******")
x = eval("42")
print(x)
print("EVAL", eval("return 13 + 24"))

fn fv(x, y, z, ...r) {
    print(x, y, z, r)
    r
}

a = fv(1,2,3,4,5,6,7,8)

b = [11,12,13]

print(1,2,3,...a, 9, 10, ...b)
a = fv(1,2,3,...a, 9, 10, ...b)
print(a.length())
print(a)

fn f(x, y) {
    fn f2(z) {
        fn f3(w) {
            b = 1
            a = b
            x + y + z + a + w
        }
        f3(10000)
    }
    f2(1000)
}

print(f(10, 100))


fn f() {
    x = 1
    y = 2
    z = 3
    fn f2() {
        outer x, y

        fn f3() {
            outer x, z
            x = 4
            z = 6
        }
        y = 5
        x = 6
        f3()

    }
    f2()
    [x, y, z]
}
f()

object Human {
    __name__ = "Human"
    name = nil
    fn make_shit(self) {
        print("SHIT from ", self.name)
    }
}

object Insect {
    fn eat_human(self, h) {
        print("Eating ", h.name)
    }
}

object Alice(Human, Insect) {
    id = 42
    name = "Alice"
    object Bob(Human) {
        name = "Bob"
        fn hello(self) {
            print("I am Bob")
        }
    }
    fn greetings(self) {
        print("Hello from", self.name)
    }
    goNorth = fn (self) {
        print("I ", self.name, " go North")
    }
}

N = object {
    __name__ = "N"
}

print(N.traits())

N = {
    __name__ : "N1"
}

print(N.traits())

N = object(Human) {
    __name__ = "N2"
}

print(N.traits())

x  = [1,2,3,4]

for i in Alice {
    print(i)
}

Alice.make_shit()
//Alice.nota(Insect)
Alice.eat_human(Alice.Bob)

print(Alice)
print(Alice.Bob)
print(Alice.greetings)

object C {
    fn __call__(self, x, y, z) {
        x + y + z
    }
}

fn inner_loop() {
    x = 0
    fn f() {
        outer x
        while x < 100 {
            x += 1
            if x == 8 {
                continue
            }
            elif x == 11 {
                break
            }
            print(x)
        }
    }
    f()
}

inner_loop()
C(10,100,1000)