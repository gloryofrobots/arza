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

    var itself = function () {
        return this;
    };
    
    var define = function (n) {
        symbol_table[n.value] = n;
        n.nud      = itself;
        n.led      = null;
        n.std      = null;
        n.lbp      = 0;
        return n;
    }
    
    var checkId = function(ids) {
        if(!ids) {
            return
        }

        if(!Array.isArray(ids)) {
            if (token.id !== ids) {
                console.error("Expected", ids, token);
                token.error("Expected '" + ids + "'.");
            }
            return;
        }

        for (key in ids) {
            if (token.id === ids[key]) {
                return;
            }
        }
        console.error("Expected", ids, token);
        token.error("Expected '" + ids + "'.");
    }

    var advance = function (ids) {
        var a, o, t, v;
        
        checkId(ids);
       
        if (token_nr >= tokens.length) {
            token = symbol_table["(end)"];
            return;
        }
        t = tokens[token_nr];
        token_nr += 1;
        v = t.value;
        a = t.type;
        if (a === "operator" || a === "name" || a === "(endline)") {
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
        token.id = v;
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
        return advance([";","(endline)"]);
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

    var statements = function (endlist) {
        var a = [], s;
        if(!endlist) endlist = ["}", "(end)", "end", "(newline)"]
        var check = false;
        while (true) {
            for(key in endlist) {
                if(endlist[key] === token.id) {
                    check = true;
                }
            }

            if (check) {
                break;
            }

            s = statement();
            if (s) {
                //console.log("s", s);
                if(s) {
                    a.push(s);
                }
                // if(s.id != "(newline)"){
                //     a.push(s);
                // }
            }
        }
        var result =  a.length === 0 ? null : a.length === 1 ? a[0] : a;
        return result;

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
            var exp = undefined;
            while(!exp) {
                 exp = expression(bp);
                //console.log("infix: ", id, exp)
            }
            this.second = exp; 
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

    var stmt = function (s, f) {
        var x = symbol(s);
        x.std = f;
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
    symbol("end");
    symbol(",");
    symbol("else");

    constant("true", true);
    constant("false", false);
    constant("null", null);
    constant("pi", 3.141592653589793);
    constant("Object", {});
    constant("Array", []);

    var empty = function() {
        return undefined;
    }

    symbol("(endline)").nud = empty;
    symbol(";").nud = empty;
    symbol("(literal)").nud = itself;

    symbol("this").nud = function () {
        this.arity = "this";
        return this;
    };

    assignment("=");
    assignment("+=");
    assignment("-=");

    infix("if", 20, function (left) {
        this.first = expression(0);
        this.second = left
        advance("else");
        this.third = expression(0);
        this.arity = "ternary";
        return this;
    });

    infixr("&&", 30);
    infixr("||", 30);

    infixr("==", 40);
    infixr("is", 40);
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

    infix("(", 90, function (left) {
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
    });

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


   prefix("cell", function () {
        var a = [],t;
        if (token.arity === "name") {
            define(token);
            this.name = token.value;
            advance();
        }
        this.first = statements(["end"]);
        advance("end");
        this.arity = "cell";
        return this;
    });

   prefix("fun", function () {
        var a = [],t;
        if (token.arity === "name") {
            define(token);
            this.name = token.value;
            advance();
        }
        advance("(");
        if (token.id !== ")") {
            while (true) {
                var arg = {};
                /*if (token.arity == "operator") {
                    token.error("Wrong function parameter");
                    token.error("Expected a parameter name.");
                }*/
                if(token.id == "::") {
                   
                    if(a.length == 0) {
                        token.error("Wrong list matching");
                    }
                    var listitems = [a.pop()];
                    arg.id = "::"
                    console.log("enter ::", token, a, listitems);
                    while(true) {
                        advance();
                        console.log("::", token);
                        if(token.arity!="name") {
                            token.error("Wrong list item in matching");
                        }
                        listitems.push(token)
                        advance();
                        if (token.id !== "::") {
                            arg.value = listitems;
                            break;
                        }
                    } 
                    a.push(arg);
                } else if(token.arity == "name" || token.arity == "literal") {
                    arg.arity = token.arity;
                    arg.value = token.value;
                    arg.id = token.id;

                    define(token);
                    a.push(arg);
                    advance();    
                }
                if (token.id == "::") {
                    continue;
                }

                if (token.id !== ",") {
                    break;
                }

                advance(",");
            }
        }
        this.first = a;
        advance(")");
       
        var ending_token = null;
        if (token.id == "(endline)") {
            ending_token = "end";
        } else if(token.id == "{") {
            ending_token = "}";
        } else {
            token.error("Wrong function statement expected either (endline) or { in the same line as fun expression")
        }
        
        advance();
        this.second = statements();
        advance(ending_token);
        this.arity = "function";
        return this;
    });


    prefix("do", function () {
        this.first = statements();
        advance("end");
        this.arity = "block";
        return this;
    });

    prefix("if", function () {
        this.branches = []
        var branch = {};
        branch.first = expression(0);
        
        if (token.id === "(endline)" || token.id === "then") {
            advance(["then", "(endline)"]);
            branch.second = statements(["else","elif", "end"]);
            this.branches.push(branch);
        } else {
            token.error("wrong if statement");
        } 
        
        while(token.id == "elif") {
            branch = {};
            advance("elif");
            branch.first = expression(0);
            if (token.id === "(endline)" || token.id === "then") {
                advance(["then", "(endline)"]);
                branch.second = statements(["else","elif", "end"]);
                this.branches.push(branch);
            } 
            else {
                token.error("wrong elif ending");
            } 
        }

        branch = {};
        if (token.id === "else") {
            advance("else");
            branch.first = null;
            branch.second = statements(["end"]);
            this.branches.push(branch);
        } 

        advance("end");
        this.arity = "if";
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

    stmt("(endline)", function () {
        return undefined;
    });
    
    stmt(";", function () {
        return undefined;
    
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
        tokens = source.tokens(':=<>!+-*&|/%^', ':=<>&|');
        var memo = _.reduce(tokens, function(memo, token){ return memo + "<" + token.value + ">,"; }, "");
        //console.log("tokens:", memo);
        //console.log(tokens);
        token_nr = 0;
        advance();
        var s = statements();
        advance("(end)");
        return s;
    };
};