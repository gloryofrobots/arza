/*function f(x, y){
    function f1(z) {
        function f3(a,b) {
            return x + y + z + a + b;
        }
        return x + y + z + f3(x, y);

    }
    return x + f1(y);
}

var result = f.call(undefined, 2,3) == f(2,3);
print(result);
var result = f.apply(undefined, [2,3]) == f(2,3);
print(result);
if (f(2,3) == 23) {
    print("GOT IT");
}
else {
    print(f(2,3));
}*/

function range(start, end, step) {
        step = step || 1;
        if (!end) {
            end = start;
            start = 0;
        }
        var arr = [];
        for (var i = start; i < end; i += step) arr.push(i);
        return arr;
}
//
//for (var y in range(10)) {
//    print(y);
//}

function fibonacci(mode, n) {
    function fib(n) {
      function _process(n,a,b) {
        return n>0 ? _process(n-1,b,a+b) : a;
      }
      return _process(n,0,1);
    }

    function fib2(n) {
      var a = 0, b = 1, t;
      while (n-- > 0) {
        t = a;
        a = b;
        b += t;
      }
      return a;
    }

     if (mode == 1) {
        return fib(n);
     } else if(mode == 2) {
        return fib2(n);
     }

}
function fold(array, fn, initial, bind){
		var len = array.length(), i = 0;
		if (len == 0 && arguments.length == 1) return null;
		var result = initial || array[i++];
		for (; i < len; i++) {
		    result = fn.call(bind, result, array[i], i, array);
		}
		return result;
}
function foldr(array, fn, initial, bind){
		var len = array.length(), i = len - 1;
		if (len == 0 && arguments.length == 1) return null;
		var result = initial || array[i--];
		for (; i >= 0; i--) result = fn.call(bind, result, array[i], i, array);
		return result;
}

function root_mean_square(ary) {
    var sum_of_squares = fold(ary, function(s,x) {return (s + x*x)}, 0);
    return Math.sqrt(sum_of_squares / ary.length());
}

function horner(coeffs, x) {
    return foldr(coeffs, function(acc, coeff) { return(acc * x + coeff) }, 0);
}

print(horner([-19,7,-4,6],3));  // ==> 128

print( root_mean_square([1,2,3,4,5,6,7,8,9,10]) ); // ==> 6.2048368229954285
var n = 11;
print ("Fibonacci(" + n + ") = " + fibonacci(1, n) + " check = " + (fibonacci(1, n) == fibonacci(2, n)));

function operators() {
    var z = 1 + 2;
    z = 345.5 * 34;
    z = 42 / 2;
    z = 10 % 2;
    z = 12 ^ 3;
    z = 34 | 3;
    z = 2233 & 123;
    z = 2 && 0;
    z = 2 || 0;
    z = 4 == 5;
    z = 4 != 5;
    z = 45 > 3;
    z = 45 < 4;
    z = 45 >= 4;
    z = 45 <= 4;
    z = 45 >> 4;
    z = 35 >>> 34;
    z = 234 << 4;
}

function main() {
    var s = "abcd";

    print(s.charAt(2));

    var s2 = eval("var g = 42; return g");

    print("EVAL IS " + s2);

    var L = {};

    function extend(object) {
     var hasOwnProperty = Object.hasOwnProperty;
     var clone = object.clone();
     print("clone " + clone);
     var length = arguments.length;
     for (var i = 1; i < length; i++) {
        var extension = arguments[i];
         for (var property in extension) {
             if (hasOwnProperty.call(extension, property)){
                 clone[property] = extension[property];
             }
        }
     }

     print("object " + object);
     print("clone " + clone);
     return clone;
    };

    function Robot(id) {
        this.id = id;
        this.launchRockets = function() {
            this.destroyWhosLeft = function() {
                print("You all gonna die " + this.id);
            };
            print("BDUSCH!!!" + this.id);
        };
    }

    function blueprint(func, object) {
    if(!func) {
        throw "Function required"
    }
    if(!object) {
        object = {};
    }
    var args = [];
    for(var i = 2; i < arguments.length; i++) {
        args.push(arguments[i]);
    }
    func.apply(object, args);
    return object;
    }

    var r = blueprint(Robot, null, "MEGA PIHAR");
    var rc = r.clone();

    rc.launchRockets();
    rc.destroyWhosLeft();
    r.launchRockets();

    var bc = extend(rc, {
    name:"ROBOT-GOBOT"
    });
    var tc = extend(bc, {
        ammo: 1000,
        lazerBeam: function() {
            print("BZZZZZ ", --this.ammo);
        }
    }, {
        photonCannon: function()  {
            print("PTRRRR ", --this.ammo)
        }
    });
    print(r);
    print(rc);
    print(bc);
    print(tc);

    tc.lazerBeam();
    tc.photonCannon();
    //
    //
    //
    function Animal(name, eatPower) {
    function eat(a1, a2) {
        function _eat(){
            function __eat() {
                if(a1.eatPower() > a2.eatPower()) {
                     return a1;
                }
                return a2;
            }
            return __eat();
        }
        return _eat();
    }

    var aid = name + "Animal";

    var A = {
        eatPower : function() {
            return eatPower;
        },
        fuck : function(other) {
           var c = [];
           c.push(this);
           c.push(other);
           return c;
        },
        id : function(){
            return aid;
        },
        eat : function(other) {
            return eat(this, other);
        },
        toString : function() {
            return this.id;
        },
        name : function(){
            return name;
        }
    };
    return A.clone();
    }
    var t = 1 !=0;
    print("t=" + t);
    var cow = Animal("Zorka", 2);
    var bug = Animal("Boris", 4);
    var survivor = cow.eat(bug);
    print(survivor.name());
    var cowbag = cow.fuck(bug);
    print("COWBUG");
    print(cowbag[0].name());
    print(cowbag[0]);
    print(cowbag[1].name());
    var i = 3;
    while(i-- > 0) {
        for(var j = 0; j < 10; j++) {
            var A = [];
            A.push(i);
            A.push(j);
            print("" + i + "," + j + " = " + A);
        }
    }

try {
   throw "Shit!"
} catch(e) {
    var x = 1;
    print("Error occurred:" + e);
} finally {
    var x = "wwww";
    print('Finally after catch');
}

try {
    print ("there are no errors");
} catch(e) {
    print("Error occurred:" + e);
} finally {
    print('Finally after try');
}


}

main();

var P = {
    id:1,
    name:"2"
};

delete P.id;

print(this);

print(this.Object);

return 42;
//var a, x, y;
//var r = 10;
//with (Math) {
//  a = PI * r * r;
//  x = r * cos(PI);
//  y = r * sin(PI / 2);
//}
//print("a= " + a + " x= " + x + " y= " + y);
//

//var n = 34.343434;
//var s = "aaaaa";

/*Object.create = function(o, properties) {
    if (typeof o !== 'object' && typeof o !== 'function') throw new TypeError('Object prototype may only be an Object: ' + o);
    else if (o === null) throw new Error("This browser's implementation of Object.create is a shim and doesn't support 'null' as the first argument.");

    if (typeof properties != 'undefined') throw new Error("This browser's implementation of Object.create is a shim and doesn't support a second argument.");

    function F() {}

    F.prototype = o;

    return new F();
};

 var rectangle = {
      create: function (width, height) {
          var self = Object.create(this);
          self.height = height;
          self.width = width;
          return self;
      },
     area: function () {
          return this.width * this.height;
     }
};

var rect = rectangle.create(5, 10);
print(rect.width)*/

