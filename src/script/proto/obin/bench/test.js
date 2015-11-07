
A = {
    action: fn (self, a1, a2){
        return a1 + a2
    }
}

B = A.clone()
B.action = fn(self, a1, a2) {
    fn _d() {
        return a1 - a2 * 100
    }
    return _d()
}

a = A.action(2,3.14)
print(a)
b = B.action(2,3.14)
print(b)

print("EVAL", eval("return 42 + 24"))
x = 42
s = "Hello"
f = 3.1214114141414141414
v = [x, s,  11, 3.14]
print(v)

p = x + f
print(p)

//fn F(x,y, ...rest) {
//    print(x,y)
//    print(rest)
//}
//
//F(1,2, "Hello World", {name:"Bob"},[4.34, 42, "Check"])
//




//x = ...A