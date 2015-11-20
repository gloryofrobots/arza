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
    fn f2() {
        x = 1
        outer x
        x = 2
    }
    f2()
    x
}
f()