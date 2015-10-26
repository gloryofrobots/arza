//function _f1(x, y) {
//    return x + y;
//}
//function _f2(x, y, z) {
//    return (x + y + z)
//}
//print(_f2(2, 3, 4));
//['LOAD_VARIABLE "x" (1)', 'LOAD_INTCONSTANT 1', 'SUB', 'STORE "x" (1)', 'POP', 'LOAD_VARIABLE "x" (1)', 'LOAD_LIST 1', 'LOAD_VARIABLE "print" (2)', 'CALL', 'POP', 'LOAD_VARIABLE "x" (1)', 'RETURN', 'LOAD_UNDEFINED', 'LOAD_UNDEFINED']
//['LOAD_VARIABLE "x" (0)', 'LOAD_INTCONSTANT 1', 'SUB', 'STORE "x" (0)', 'LOAD_VARIABLE "x" (0)', 'LOAD_LIST 1', 'LOAD_VARIABLE "print" (1)', 'CALL', 'LOAD_VARIABLE "x" (0)', 'RETURN', 'LOAD_UNDEFINED', 'LOAD_UNDEFINED']_
//function _f2(x) {
//    x -= 1;
//    print(x);
//    return x;
//}
//print(_f2(23));


fn _f2(x) {
    y = x - 1;
    print(y);
    return x;
}
print(_f2(23));

//fn fib(n) {
//  fn _process(n,a,b) {
//    return _process(n-1,b,a+b)  if n>0 else a;
//  }
//  return _process(n,0,1);
//}

//fn fib2(n) {
//  a = 0
//  b = 1
//  t = nil
//  while n > 0 {
//    n -= 1
//    t = a;
//    a = b;
//    b += t;
//  }
//  return a;
//}
//print(fib2(10))

//function fib(n) {
//  function _process(n,a,b) {
//    return n>0 ? _process(n-1,b,a+b) : a;
//  }
//  return _process(n,0,1);
//}
//
//function fib2(n) {
//  var a = 0, b = 1, t;
//  while (n-- > 0) {
//    t = a;
//    a = b;
//    b += t;
//  }
//  return a;
//}
//
//fib2(10);
