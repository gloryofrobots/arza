object Alice(Human, Insect, Fucking, Shit) {
    id = 42
    name = "Alice"
    object Bob(Human) {
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
for i in Alice {
    print(i)
}
print(Alice)
print(Alice.Bob)
print(Alice.greetings)

fn wrap(cb, ...args) {
    cb(1,2, ...args)
}

wrap(fn(...args) {
    print(...args)
},3)


//Alice = {
//    id = 42
//    name = "Alice"
//    Bob = {
//        fn hello(self) {
//            print("I am Bob")
//        }
//    }
//
//    fn greetings(self) {
//        print("Hello from", self.name)
//    }
//
//    goNorth = fn(self) {
//        print("I ", self.name, " go North")
//    }
//}
//
//Alice.Bob.hello()
//Bob.hello()
//greetings(Alice)
////
////AliceTraits = {
////    id:42,
////    name: "Alice",
////    greetings: fn(self) {
////        return 2 if 4 > 5 else 6
////    },
////    goNorth: fn(self) {
////    }
////}
//////AliceTraits.addTraits(Human, Insect, Fucking, Shit)
////
////
////print(AliceTraits)
////
////
////fn p(x, y, ...rest) {
////    print(x, y, ...rest)
////}
////
////
////O = {
////    id: 42,
////    name: "Alice",
////    ammo: 34.34565656565,
////    children: [{}, {}, {}]
////}
////print(O)
////print(p.arity())
////print(p.isVariadic())
////
////eval("return 42")
////print("EVAL", eval("return 13 + 24"))
////
////fn fib(n) {
////  fn _process(n,a,b) {
////    return _process(n-1,b,a+b) if n>0 else a;
////  }
////  return _process(n,0,1);
////}
////
////print(fib(10))
////
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