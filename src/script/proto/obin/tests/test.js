fn test_eq(str, val, expected) {
    print("test:","'" + str + "'", val, val == expected)
    if val != expected {
        throw "Test error"
    }
}

x = 1
test_eq("x = 1", x, 1)

x = "Hello"
test_eq("x = 'Hello'", x, "Hello")

x = 42.234433444
test_eq("x = 42.234433444", x, 42.234433444)

x = [1, "Hello", 35.44555]
print(x)
print(x[1])

x = (42,)
print(x)

x = (1,2, ["Alice", "Bob", (45,), 54.000000001])
print(x)

x = {name: "XXX"}
print(x.name)

print((1,2, ["Alice", "Bob", (45,), 54.000000001]), {name:"Alice", surname: "Bob"})

x = true
print(x)

x = false
print(x)
x = nil
print(x)

x = { name:"X", age:42.24 }
print(x)

x = 1
y = 0
print("x = ", x, "y = ", y)

print("x or y", x or y)

print("x and y", x and y)
print("not y", not y)
print("~ y", ~ y)
print("~ y", ~ y)


print("x | y", x | y)
print("x & y", x & y)
print("x ^ y", x ^ y)

//print("x += 0.5", x += 0.5)
//print("x -= 1", x -= 1)
//print("x *= 2", x *= 2)
//print("x /= 3", x /= 3)
//print("x %= 4", x %= 4)
//print("x &= 5", x &= 5)
//print("x ^=6", x ^=6)
//print("x |= 7", x |= 7)

print("true when 5 > 4 else false", true when 5 > 4 else false)
print("x is y", x is y)
print("x isnot y", x isnot y)
print("5 > 5", 5 > 5)
print("5 >= 3", 5 >= 3)
print("5 < 4", 5 < 4)
print("5 <= 3", 5 <= 3)
print("x != 6", x != 6)
print("x == y", x == y)
//print("x >> 43", x >> 43)
//print("x << 10001", x << 10001)
//print("x >>> 1001001001", x >>> 1001001001)
print("x + 34", x + 34)
print("x - 34", x - 34)
print("x * 34", x * 34)
print("x / 45", x / 45)
print("x % 32", x % 32)


A = [0, 1, 2, x]
print(x,"in",A, x in A)

x = 2

y = if x == 3 {
    5
} elif x == 20 {
    6
} else {
    7
}
print(y)

while x == 2 {
    print("LOOP")
    x = 1
}

x = fn(x,y) {
    z = x + y
} (1, 2)

print("x", x)

trait Private
trait Patriot
trait Man
trait Weapon
trait Rifle
trait Equipment

object Joe(Private, Patriot, Man) {
    health = 100

    object rifle(Rifle, Weapon, Equipment) {
        ammo = 100
    }

    fn fire (self){
        print("Joe firing with", self.rifle)
    }
}

print(Joe)

generic fire {
    (self of Patriot, rifle of Rifle) {
        print("Patriot", self, "fire rifle", rifle)
    }
    (self of Man) {
        print("Man firing")
        fire(self, self.rifle)
    }
}

fire(Joe)

reify fire {
    (self of Private, w of Weapon) {
        print("Private", self, "fire weapon", w)
    }
}
detach(Joe.rifle, Rifle)

fire(Joe)

import military.equipment as eq
import military.troops
import attack, hide, runaway as run_away_from_danger, three from military.ta.behavior


print(attack)
print(hide)
print(run_away_from_danger)
print(troops.Squad)
print(troops.Civilian)
print(troops.Soldier)

print(eq.Weapon)
print(eq.fire)

S = "ABCDEFGH"
for s in S {
    print(s)
}

L = [23, 42.344, "Hello", (1,2,3,55555,[2,3]), {name:"Bob", surname:"Alice"}]
for el in L {
    print(el)
}

for el in L[3] {
    print(el)
}

A = [1, 2, 3, 4, 5, 6, 35, 110, 122]
for a in A {
    if(a == 35) {
       continue
    }

    if(a > 115) {
        if(1 < 2) {
            break;
        }
    }
    print(a)
}

x = 20
while x > 0 {
    x -= 5
    if x == 10 {
        print("SKIP", x)
        continue
    }
    print("X", x)

}

fn inner_loop_outer() {
    x = 0
    fn f() {
        outer x
        while x < 100 {
            x += 1
            if x == 8 {
                continue
            }
            elif x == 11 {
                break
            }
            print(x)
        }
    }
    f()
}
inner_loop_outer()

fn fib(n) {
  fn _process(n,a,b) {
    return _process(n-1,b,a+b) when n>0 else a;
  }
  return _process(n,0,1);
}

print(fib(10))



fn p(...rest) {
    print(rest)
}

v1 = [1,2,3]
v2 = [7,8]
v3 = [11,12,13,14,15,16,17,18,19,20]

p(...v1, 4,5,6, ...v2, 9, 10, ...v3, ...[21, 22], 23)

fn add2(...rest) {
    return add(1, ...rest)
}

fn add(x,y,z) {
    print(x,y,z)
    return x + y + z
}

A = [3]
add2(2,...A)
// Here args must be empty list
fn wrap(cb, ...args) {
    cb(...args)
}

wrap(fn(x, ...args) {
    print(x, args)
}, 1)


fn fv(x, y, z, ...r) {
    A = [10,11,12,14]
    fn _f(w,t) {
        print(w, t, ...r, x, y, z, ...A)

        print(w, t, x, y, z, r)
    }
    _f(x+y, y+z)
    r
}

a = fv(1,2,3,4,5,6,7,8)

b = [11,12,13]

print(1,2,3,...a, 9, 10, ...b)
a = fv(1,2,3,...a, 9, 10, ...b)
print(a)

