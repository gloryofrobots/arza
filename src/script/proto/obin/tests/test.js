
fn fv(x, y, z, ...r) {
    print(x, y, z, r)
    r
}

print(fv(1,2,3,4,5,6,7,8,9))


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

fn fib(n) {
  fn _process(n,a,b) {
    _process(n-1,b,a+b) if n>0 else a;
  }
  _process(n,0,1);
}

fib(25)

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

