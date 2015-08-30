// parse.js
// Parser for Simplified JavaScript written in Simplified JavaScript
// From Top Down Operator Precedence
// http://javascript.crockford.com/tdop/index.html
// Douglas Crockford
// 2010-06-26

var make_parse = function () {
    var symbol_table = {};
    var token;
    var tokens;
    var token_nr;
    var reserved = ["if", "else", "case", "of", "class", "def",
     "func","fn", "or", "and"]

    var itself = function () {
        return this;
    };
    
    var define = function (n) {
        symbol_table[n.value] = n;
        n.reserved = false;
        n.nud      = itself;
        n.led      = null;
        n.std      = null;
        n.lbp      = 0;
        return n;
    }
    


    var advance = function (id) {
        var a, o, t, v;
        if (id && token.id !== id) {
            console.error("Expected", id, token);

            token.error("Expected '" + id + "'.");
        }
        if (token_nr >= tokens.length) {
            token = symbol_table["(end)"];
            return;
        }
        t = tokens[token_nr];
        token_nr += 1;
        v = t.value;
        a = t.type;
        if (a === "operator" || a === "name") {
            o = symbol_table[v];
            if (!o) {
                define(t);
                o = t;
                //t.error("Unknown operator. " + v);
            }

        } else if (a === "string" || a ===  "number") {
            o = symbol_table["(literal)"];
            a = "literal";
        } else {
            t.error("Unexpected token.");
        }
        token = Object.create(o);
        token.from  = t.from;
        token.to    = t.to;
        token.value = v;
        token.arity = a;
        token.error = function(){
            console.error(arguments);
            throw new Error(arguments);
        }
        
        return token;
    };

    var endofexpression = function() {
        if (token_nr >= tokens.length) {
            return advance();
        }
        return advance(";");
    }

    var expression = function (rbp) {
        var left;
        var t = token;
        advance();
        left = t.nud();
        //console.log("expression:", rbp, t.rbp, t.value, token.value, token.rbp, token.lbp);
        while (rbp < token.lbp) {
            t = token;
            advance();
            //console.log("expression2:",   token.value, token.rbp, token.lbp);

            left = t.led(left);
        }
        return left;
    };

    var statement = function () {
        var n = token, v;

        if (n.std) {
            advance();
            return n.std();
        }
        v = expression(0);
        
        //if(v.id === "(") {
        //    advance(")");
        //}

        //if (!v.assignment && v.id !== "(") {
        //    v.error("Bad expression statement.");
        //}
        endofexpression();
        return v;
    };

    var statements = function () {
        var a = [], s;
        while (true) {
            if (token.id === "}" || token.id === "(end)") {
                break;
            }
            s = statement();
            if (s) {
                a.push(s);
            }
        }
        return a.length === 0 ? null : a.length === 1 ? a[0] : a;
    };

    var block = function () {
        var t = token;
        advance("{");
        return t.std();
    };

    var original_symbol = {
        nud: function () {
            this.error("Undefined.");
        },
        led: function (left) {
            this.error("Missing operator.");
        }
    };

    var symbol = function (id, bp) {
        var s = symbol_table[id];
        bp = bp || 0;
        if (s) {
            if (bp >= s.lbp) {
                s.lbp = bp;
            }
        } else {
            s = Object.create(original_symbol);
            s.id = s.value = id;
            s.lbp = bp;
            symbol_table[id] = s;
        }
        return s;
    };

    var constant = function (s, v) {
        var x = symbol(s);
        x.nud = function () {
            this.value = symbol_table[this.id].value;
            this.arity = "literal";
            return this;
        };
        x.value = v;
        return x;
    };

    var infix = function (id, bp, led) {
        var s = symbol(id, bp);
        s.led = led || function (left) {
            this.first = left;
            this.second = expression(bp);
            this.arity = "binary";
            return this;
        };
        return s;
    };

    var infixr = function (id, bp, led) {
        var s = symbol(id, bp);
        s.led = led || function (left) {
            this.first = left;
            this.second = expression(bp - 1);
            this.arity = "binary";
            return this;
        };
        return s;
    };

    var assignment = function (id) {
        return infixr(id, 10, function (left) {
            if (left.id !== "." && left.id !== "[" && left.arity !== "name" 
                && left.id != ",") {
                console.log("Bad Lv ", left); 
                left.error("Bad lvalue.");
            }
            this.first = left;
            this.second = expression(9);
            this.assignment = true;
            this.arity = "binary";
            return this;
        });
    };

    var prefix = function (id, nud) {
        var s = symbol(id);
        s.nud = nud || function () {
            this.first = expression(70);
            this.arity = "unary";
            return this;
        };
        return s;
    };

    var stmt = function (s, f, reserved) {
        var x = symbol(s);
        x.std = f;
        if (reserved) {
            x.reserved = reserved;
        }
        return x;
    };

    symbol("(end)");
    symbol("end");
    symbol("(name)");
    symbol(":");
    symbol(";");
    symbol(")");
    symbol("]");
    symbol("}");
    symbol(",");
    symbol("else");

    constant("true", true);
    constant("false", false);
    constant("null", null);
    constant("pi", 3.141592653589793);
    constant("Object", {});
    constant("Array", []);

    symbol("(literal)").nud = itself;

    symbol("this").nud = function () {
        this.arity = "this";
        return this;
    };

    assignment("=");
    assignment("+=");
    assignment("-=");

    infix("?", 20, function (left) {
        this.first = left;
        this.second = expression(0);
        advance(":");
        this.third = expression(0);
        this.arity = "ternary";
        return this;
    });

    infixr("&&", 30);
    infixr("||", 30);

    infixr("===", 40);
    infixr("!==", 40);
    infixr("<", 40);
    infixr("<=", 40);
    infixr(">", 40);
    infixr(">=", 40);

    infix("+", 50);
    infix("-", 50);

    infix("*", 60);
    infix("/", 60);
    
    infix("->", 80);
    
    infix(".", 80, function (left) {
        this.first = left;
        if (token.arity !== "name") {
            token.error("Expected a property name.");
        }
        token.arity = "literal";
        this.second = token;
        this.arity = "binary";
        advance();
        return this;
    });

    var tuplemode = false;

    // infix(",", 5, function (left) {
    //     if(tuplemode) {
    //         this.arity = "unary";
    //         this.first = left;
    //         console.log("token tuplemode:", token);
    //         return this;
    //     }
    //     var a = [left];
    //     this.first = a;
    //     this.arity = "unary";
    //     console.log("token:", token)
    //     tuplemode = true;
    //     while(true) {
    //         var e = expression(0);
            
    //         var t = tokens[token_nr];
            
    //         if(e.id == ',') {
    //             a.push(e.first);
    //             console.log("e:", a, e, t, token);
    //         } else {
    //             console.log("breaking!");
    //             a.push(e);
    //             tuplemode = false;
    //             console.log("e:", a, e, t, token);
    //             break;
    //         }
    //     }
    //     return this;
    // });
    infix(",", 20);
    infix("[", 80, function (left) {
        this.first = left;
        this.second = expression(0);
        this.arity = "binary";
        advance("]");
        return this;
    });

    /*infix("(", 90, function (left) {
        var a = [];
        if (left.id === "." || left.id === "[") {
            this.arity = "ternary";
            this.first = left.first;
            this.second = left.second;
            this.third = a;
        } else {
            this.arity = "binary";
            this.first = left;
            this.second = a;
            if ((left.arity !== "unary" || left.id !== "function") &&
                    left.arity !== "name" && left.id !== "(" &&
                    left.id !== "&&" && left.id !== "||" && left.id !== "?") {
                left.error("Expected a variable name.");
            }
        }
        if (token.id !== ")") {
            while (true) {
                a.push(expression(0));
                if (token.id !== ",") {
                    break;
                }
                advance(",");
            }
        }
        advance(")");
        return this;
    });*/

    var __call__ = function(id) {
        var s = symbol(id, 80);
        s.led = function (left) {
            var a = [];
            if (left.id === "." || left.id === "[") {
                this.arity = "ternary";
                this.first = left.first;
                this.second = left.second;
                this.third = a;
            } else {
                this.arity = "binary";
                this.first = left;
                this.second = a;
            }

            if (token.id == "(" || token.id == "=" 
                || token.arity == "operator" 
                || token.id == ".") {
                return this;
            }
            
            while (true) {
                a.push(expression(0));
                if (token.id !== ",") {
                    break;
                }
                advance(",");
            }

            return this;
       }
       return s;
    };

    prefix("!");
    prefix("-");
    prefix("typeof");

    // prefix("(", function () {
    //     var a = [];
    //     while (true) {
    //         a.push(expression(0));
    //         if (token.id !== ",") {
    //             break;
    //         }
    //         advance(",");
    //     }
        
    //     advance(")");

    //     if(a.length == 1) {
    //         return a[0];
    //     }

    //     this.first = a;
    //     this.arity = "unary";
    //     return this;
    // });

   prefix("(", function () {
        var e = expression(0);
        advance(")");
        return e;
    });


    prefix("function", function () {
        var a = [];
        if (token.arity === "name") {
            define(token);
            this.name = token.value;
            advance();
        }
        advance("(");
        if (token.id !== ")") {
            while (true) {
                if (token.arity !== "name") {
                    token.error("Expected a parameter name.");
                }
                define(token);
                a.push(token);
                advance();
                if (token.id !== ",") {
                    break;
                }
                advance(",");
            }
        }
        this.first = a;
        advance(")");
        advance("{");
        this.second = statements();
        advance("}");
        this.arity = "function";
        return this;
    });

    prefix("do", function () {
        this.first = [];
        this.second = statements();
        advance("end");
        this.arity = "block";
        return this;
    });


    prefix("[", function () {
        var a = [];
        if (token.id !== "]") {
            while (true) {
                a.push(expression(0));
                if (token.id !== ",") {
                    break;
                }
                advance(",");
            }
        }
        advance("]");
        this.first = a;
        this.arity = "unary";
        return this;
    });

    prefix("{", function () {
        var a = [], n, v;
        if (token.id !== "}") {
            while (true) {
                n = token;
                if (n.arity !== "name" && n.arity !== "literal") {
                    token.error("Bad property name.");
                }
                advance();
                advance(":");
                v = expression(0);
                v.key = n.value;
                a.push(v);
                if (token.id !== ",") {
                    break;
                }
                advance(",");
            }
        }
        advance("}");
        this.first = a;
        this.arity = "unary";
        return this;
    });


    stmt("{", function () {
        var a = statements();
        advance("}");
        return a;
    });


    var reserve = function(n) {
        n.reserved = true;
    };

    stmt("if", function () {
        advance("(");
        this.first = expression(0);
        advance(")");
        this.second = block();
        if (token.id === "else") {
            reserve(token);
            advance("else");
            this.third = token.id === "if" ? statement() : block();
        } else {
            this.third = null;
        }
        this.arity = "statement";
        return this;
    }, true);

    stmt("return", function () {
        if (token.id !== ";") {
            this.first = expression(0);
        }
        endofexpression();
        if (token.id !== "}") {
            token.error("Unreachable statement.");
        }
        this.arity = "statement";
        return this;
    });

    stmt("break", function () {
        endofexpression();
        if (token.id !== "}") {
            token.error("Unreachable statement.");
        }
        this.arity = "statement";
        return this;
    });

    stmt("while", function () {
        advance("(");
        this.first = expression(0);
        advance(")");
        this.second = block();
        this.arity = "statement";
        return this;
    });

    return function (source) {
        tokens = source.tokens('=<>!+-*&|/%^', '=<>&|');
        var memo = _.reduce(tokens, function(memo, token){ return memo + "<" + token.value + ">,"; }, "");
        console.log("tokens:", memo);
        //console.log(tokens);
        token_nr = 0;
        advance();
        var s = statements();
        advance("(end)");
        return s;
    };
};
