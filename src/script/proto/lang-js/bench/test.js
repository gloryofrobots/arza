// The Great Computer Language Shootout
// http://shootout.alioth.debian.org/
//
// contributed by David Hedbor
// modified by Isaac Gouy
//"use strict";
function A() {
    return 1;
}

function B() {
    return A() + 1;
}

print (B());
//function Obj(id) {
//    this.id = id;
//}
//
//var obj = new Obj(1);
//print(obj.id);
//function main() {
//    var x = 1, i = 0;
//    while(true) {
//        break
//    }
//    return i;
//}
//print(main())
//
//function F() {
//    this.uid = 1233.232;
//    this.data = {};
//    this.data.id = 1;
//    var self = this;
//    /*this.data.getId = function() {
//        return self.data.id;
//    };*/
//}


/*
var f = new F();
print(f.data.getId());

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

