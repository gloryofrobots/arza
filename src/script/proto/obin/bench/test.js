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
//fn Human(_name, _id) {
//    fn secret(msg) {
//        print("SECRET :" + msg);
//    }
//    return {
//        name: fn{
//            return _name;
//        },
//        greetings: fn {
//            return this.name() + " - " + _id;
//        },
//        memory : {
//            secret: fn {
//                secret("real secret");
//            }
//        }
//    }
//}
//
//h = Human("Bob", 42)
//print(h.name())
//print(h.greetings())
//h.memory.secret()
//
//fn fib(n) {
//  fn _process(n,a,b) {
//    return _process(n-1,b,a+b)  if n>0 else a;
//  }
//  return _process(n,0,1);
//}
//
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

