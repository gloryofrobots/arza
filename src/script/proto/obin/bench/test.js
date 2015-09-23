// The Great Computer Language Shootout
// http://shootout.alioth.debian.org/
//
// contributed by David Hedbor
// modified by Isaac Gouy
var x = 1;

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

    function A() {
        this.eatPower = function() {
            return eatPower;
        };
        this.name = function(){
            return name;
        };
        this.fuck = function(other) {
           var c = [];
           c.push(this);
           c.push(other);
           return c;
        };
        this.id = function(){
            return aid;
        };
        this.eat = function(other) {
            return eat(this, other);
        };
        this.toString = function() {
            return this.id;
        };
    }
    return new A();
}

var cow = Animal("Zorka", 2);
var bug = Animal("Boris", 4);
var survivor = cow.eat(bug);
print(survivor.name());
var cowbag = cow.fuck(bug);
print("COWBUG");
print(cowbag[0].name());
print(cowbag[1].name());
var i = 3;
while(i-- > 0) {
    for(var j = 0; j < 10; j++) {
        var A = new Array();
        A.push(i);
        A.push(j);
        print("" + i + "," + j + " = " + A);
    }
}

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

