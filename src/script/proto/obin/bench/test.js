// The Great Computer Language Shootout
// http://shootout.alioth.debian.org/
//
// contributed by David Hedbor
// modified by Isaac Gouy
var x = 1;
//
//Object.create = function(o, properties) {
//    if (typeof o !== 'object' && typeof o !== 'function') throw new TypeError('Object prototype may only be an Object: ' + o);
//    else if (o === null) throw new Error("This browser's implementation of Object.create is a shim and doesn't support 'null' as the first argument.");
//
//    if (typeof properties != 'undefined') throw new Error("This browser's implementation of Object.create is a shim and doesn't support a second argument.");
//
//    var O = {};
//    O.prototype = o;
//
//    return O;
//};

function extend(object) {
     var hasOwnProperty = Object.hasOwnProperty;
     var clone = object.clone();
     var length = arguments.length;
     for (var i = 1; i < length; i++) {
        var extension = arguments[i];
         for (var property in extension) {
             if (hasOwnProperty.call(extension, property)){
                 object[property] = extension[property];
             }
        }
     }

     return clone;
};

function Robot(id) {
    this.id = id;
    this.launchRockets = function() {
        this.destroyWhosLeft = function() {
            print("You all gonna die");
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

print(r);
print(rc);
print(bc);

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

var cow = Animal("Zorka", 2);
var bug = Animal("Boris", 4);
var survivor = cow.eat(bug);
print(survivor.name());
var cowbag = cow.fuck(bug);
print("COWBUG");
print(cowbag[0].name());
print(cowbag[0]);
print(cowbag[1].name());
//var i = 3;
//while(i-- > 0) {
//    for(var j = 0; j < 10; j++) {
//        var A = [];
//        A.push(i);
//        A.push(j);
//        print("" + i + "," + j + " = " + A);
//    }
//}
//
//var a, x, y;
//var r = 10;
//with (Math) {
//  a = PI * r * r;
//  x = r * cos(PI);
//  y = r * sin(PI / 2);
//}
//print("a= " + a + " x= " + x + " y= " + y);
//
//try {
//   throw "Shit!"
//} catch(e) {
//    print("Error occurred:" + e);
//}
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

