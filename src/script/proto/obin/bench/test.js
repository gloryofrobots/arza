fn F(x,y, ...rest) {
    print(x,y)
    print(rest)
}

F(1,2, "Hello World", {name:"Bob"},[4.34, 42, "Check"])

A = {
    action: fn (a1, a2){
        return a1 + a2
    }
}

a = A.action(2,3.14)
print(a)




//x = ...A