O = {
        id:42,
        action: fn () {},
        name: "Alice"
    }

L = {
    gender: "Male",
    hello: fn(){

        print("Hello i am L")
    }
}

print(O.traits())
print(L.traits())
O.isa(L)
print(O.traits())
O.hello()
O.nota(L)
print(O.traits())
print("Kindof", O.kindof(L))
O.isa(L)
print(O.traits())

O2 = O.clone()


print(O.name)
print(O)
print(O2)

x = 42
s = "Hello"
f = 3.1214114141414141414
v = [x, s, O, 11, 3.14]
p = x + f
print(p)

//fn F(x,y, ...rest) {
//    print(x,y)
//    print(rest)
//}
//
//F(1,2, "Hello World", {name:"Bob"},[4.34, 42, "Check"])
//
//A = {
//    action: fn (a1, a2){
//        return a1 + a2
//    }
//}
//
//a = A.action(2,3.14)
//print(a)




//x = ...A