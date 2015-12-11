hello = generic("hello")
print(hello)
Dog = {
    name: "dog",
    teeth: 32,
    sound: "Bark"
}

fn create(origin, data) {
    copy = clone(origin)
    for k in data {
        v = data[k]
        copy[k] = v
    }
    return copy
}

Cat = create(Dog, {
    name: 'Cat',
    sound: "Miau"
})

print(Dog)

specify(hello, [Dog], fn(self){
    print("Dog barks", self)
})
hello(Dog)
hello(Cat)
specify(hello, [Cat], fn(self){
    print("Cat miuaus", self)
})
hello(Cat)


//A = [1,2,3]
//B = [4,5,6]
//
//print(1000,1000,1000,...A, 10,11,12, ...B, 20,20,30, ...[2,2,2,2,2], ...[4,5,6,7,8])
//
//fn fv(x, y, z, ...r) {
//    A = [10,11,12,14]
//    fn _f(w,t) {
//        print(w, t, ...r, x, y, z, ...A)
//
//        print(w, t, x, y, z, r)
//    }
//    _f(x+y, y+z)
//    r
//}
//
//a = fv(1,2,3,4,5,6,7,8)
//
//b = [11,12,13]
//
//print(1,2,3,...a, 9, 10, ...b)
//a = fv(1,2,3,...a, 9, 10, ...b)
//print(a.length())
//print(a)
//
//fn fo() {
//    x = 3
//    y = 4
//    fn _f() {
//        outer x,y
//        x = 1
//        y = 2
//        [x, y]
//    }
//
//   print(_f())
//   print(x, y)
//}
//
//fo()
//
//fn fib(n) {
//  fn _process(n,a,b) {
//    _process(n-1,b,a+b) if n>0 else a;
//  }
//  _process(n,0,1);
//}
//
//print(fib(25))
//
//print("*******")
//fn yfib(x) {
//    coroutine(fn(yield) {
//      for i in range(0, x) {
//        yield(fib(i))
//      }
//      fib(x)
//    })
//}
//
//f = yfib(9)
//
//for i in f {
//  print(i)
//}
//print("*******")
//x = eval("42")
//print(x)
//print("EVAL", eval("return 13 + 24"))
//
//
//fn f(x, y) {
//    fn f2(z) {
//        fn f3(w) {
//            b = 1
//            a = b
//            x + y + z + a + w
//        }
//        f3(10000)
//    }
//    f2(1000)
//}
//
//print(f(10, 100))
//
//
//fn f() {
//    x = 1
//    y = 2
//    z = 3
//    fn f2() {
//        outer x, y
//
//        fn f3() {
//            outer x, z
//            x = 4
//            z = 6
//        }
//        y = 5
//        x = 6
//        f3()
//
//    }
//    f2()
//    [x, y, z]
//}
//f()
//
//fn inner_loop() {
//    x = 0
//    fn f() {
//        outer x
//        while x < 100 {
//            x += 1
//            if x == 8 {
//                continue
//            }
//            elif x == 11 {
//                break
//            }
//            print(x)
//        }
//    }
//    f()
//}
//
//inner_loop()
//x = 1 + 2 * 3
//

