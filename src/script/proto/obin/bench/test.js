 co = coroutine(fn(yield, x) {
           Z = "1111"

           _co1 = coroutine(fn(yield2, y) {
               Y = "2222"
               fn send() {
                    X = "3333"
                    return yield2(42 + y)
               }
               send()
           })

        print("x", x)
        v = _co1(x)
        t = yield(v)
        print("t", t)
        x = yield(t)
        print("x", x)
        return x
      })

v = co(23)
print(v)
v = co(34)
print(v)
v = co(44)
print(v)

iter = coroutine(fn(yield) {
           _iter = coroutine(fn(yield2) {
               fn send(i) {
                    return yield2(i)
               }
               i = 0
               while i < 9 {
                   send(i)
                   i += 1
               }
               return i
           })
        for v in _iter {
            yield(v)
        }
        return nil
      })

for v in iter {
    print(v)
}
//
//fn fib(n) {
//  fn _process(n,a,b) {
//    return _process(n-1,b,a+b) if n>0 else a;
//  }
//  return _process(n,0,1);
//}
//
//print(fib(10))
//
//
//
//object Human {
//    __name__ = "Human"
//    name = nil
//    fn make_shit(self) {
//        print("SHIT from ", self.name)
//    }
//}
//
//object Insect {
//    fn eat_human(self, h) {
//        print("Eating ", h.name)
//    }
//}
//
//object Alice(Human, Insect) {
//    id = 42
//    name = "Alice"
//    object Bob(Human) {
//        name = "Bob"
//        fn hello(self) {
//            print("I am Bob")
//        }
//    }
//    fn greetings(self) {
//        print("Hello from", self.name)
//    }
//    goNorth = fn (self) {
//        print("I ", self.name, " go North")
//    }
//}
//
//N = object {
//    __name__ = "N"
//}
//
//print(N.traits())
//
//N = {
//    __name__ : "N1"
//}
//
//print(N.traits())
//
//N = object(Human) {
//    __name__ = "N2"
//}
//
//print(N.traits())
//
//x  = [1,2,3,4]
//
//for i in Alice {
//    print(i)
//}
//
//Alice.make_shit()
////Alice.nota(Insect)
//Alice.eat_human(Alice.Bob)
//
//print(Alice)
//print(Alice.Bob)
//print(Alice.greetings)
////A = {
////    action: fn (self, a1, a2){
////        return a1 + a2
////    }
////}
////
////B = A.clone()
////B.action = fn(self, a1, a2) {
////    fn _d() {
////        return a1 - a2 * 100
////    }
////    return _d()
////}
////
////a = A.action(2,3.14)
////print(a)
////b = B.action(2,3.14)
////print(b)
////
////x = 42
////s = "Hello"
////f = 3.1214114141414141414
////v = [x, s,  11, 3.14]
////print(v)
////
////p = x + f
////print(p)
////
//////fn F(x,y, ...rest) {
//////    print(x,y)
//////    print(rest)
//////}
//////
//////F(1,2, "Hello World", {name:"Bob"},[4.34, 42, "Check"])
//////
////
////
////
////
//////x = ...A