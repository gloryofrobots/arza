fn f() {
}

x = 1

fn fib(n) {
  fn _process(n,a,b) {
    _process(n-1,b,a+b) if n>0 else a;
  }
  _process(n,0,1);
}

fib(25)
