fn fib(n) {
  fn _process(n,a,b) {
    _process(n-1,b,a+b) if n>0 else a;
  }
  _process(n,0,1);
}

print(fib(25))

fn yfib(x) {
    coroutine(fn(yield) {
      for i in range(0, x - 1) {
        yield(fib(i))
      }
      fib(x)
    })
}

f = yfib(5)

for i in f {
  print(i)
}

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

