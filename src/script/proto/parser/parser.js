var _ = require('underscore-node');
var fs = require('fs');
var http = require('http') // http module
    , qs = require('qs'); // querystring parser

// tokens.js
// 2010-02-23

// (c) 2006 Douglas Crockford

// Produce an array of simple token objects from a string.
// A simple token object contains these members:
//      type: 'name', 'string', 'number', 'operator'
//      value: string or number value of the token
//      from: index of first character of the token
//      to: index of the last character + 1

// Comments of the // type are ignored.

// Operators are by default single characters. Multicharacter
// operators can be made by supplying a string of prefix and
// suffix characters.
// characters. For example,
//      '<>+-&', '=>&:'
// will match any of these:
//      <=  >>  >>>  <>  >=  +: -: &: &&: &&



String.prototype.tokens = function (prefix, suffix) {
    var c;                      // The current character.
    var from;                   // The index of the start of the token.
    var i = 0;                  // The index of the current character.
    var length = this.length;
    var n;                      // The number value.
    var q;                      // The quote character.
    var str;                    // The string value.
    var linecount = 1;
    var result = [];            // An array to hold the results.

    var make = function (type, value) {
// Make a token object.

        return {
            type: type,
            value: value,
            from: from,
            to: i,
            line: linecount,
            error: function(){
                console.error(arguments);
                throw new Error(arguments);
            }
        };
    };

// Begin tokenization. If the source string is empty, return nothing.

    if (!this) {
        return;
    }

// If prefix and suffix strings are not provided, supply defaults.

    if (typeof prefix !== 'string') {
        prefix = '<>+-&';
    }
    if (typeof suffix !== 'string') {
        suffix = '=>&:';
    }


// Loop through this text, one character at a time.

    c = this.charAt(i);
    while (c) {
        from = i;

// Ignore whitespace.

        if( c == "\n") {
            linecount+=1;
            i += 1;
            result.push(make('(endline)', "(endline)"));
            c = this.charAt(i);

        }
        else if (c <= ' ') {
            i += 1;
            c = this.charAt(i);

// name.

        } else if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
            str = c;
            i += 1;
            for (;;) {
                c = this.charAt(i);
                if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                    (c >= '0' && c <= '9') || c === '_') {
                    str += c;
                    i += 1;
                } else {
                    break;
                }
            }
            result.push(make('name', str));

// number.

// A number cannot start with a decimal point. It must start with a digit,
// possibly '0'.

        } else if (c >= '0' && c <= '9') {
            str = c;
            i += 1;

// Look for more digits.

            for (;;) {
                c = this.charAt(i);
                if (c < '0' || c > '9') {
                    break;
                }
                i += 1;
                str += c;
            }

// Look for a decimal fraction part.

            if (c === '.') {
                i += 1;
                str += c;
                for (;;) {
                    c = this.charAt(i);
                    if (c < '0' || c > '9') {
                        break;
                    }
                    i += 1;
                    str += c;
                }
            }

// Look for an exponent part.

            if (c === 'e' || c === 'E') {
                i += 1;
                str += c;
                c = this.charAt(i);
                if (c === '-' || c === '+') {
                    i += 1;
                    str += c;
                    c = this.charAt(i);
                }
                if (c < '0' || c > '9') {
                    make('number', str).error("Bad exponent");
                }
                do {
                    i += 1;
                    str += c;
                    c = this.charAt(i);
                } while (c >= '0' && c <= '9');
            }

// Make sure the next character is not a letter.

            if (c >= 'a' && c <= 'z') {
                str += c;
                i += 1;
                make('number', str).error("Bad number");
            }

// Convert the string value to a number. If it is finite, then it is a good
// token.

            n = +str;
            if (isFinite(n)) {
                result.push(make('number', n));
            } else {
                make('number', str).error("Bad number");
            }

// string

        } else if (c === '\'' || c === '"') {
            str = '';
            q = c;
            i += 1;
            for (;;) {
                c = this.charAt(i);
                if (c < ' ') {
                    make('string', str).error(c === '\n' || c === '\r' || c === '' ?
                        "Unterminated string." :
                        "Control character in string.", make('', str));
                }

// Look for the closing quote.

                if (c === q) {
                    break;
                }

// Look for escapement.

                if (c === '\\') {
                    i += 1;
                    if (i >= length) {
                        make('string', str).error("Unterminated string");
                    }
                    c = this.charAt(i);
                    switch (c) {
                        case 'b':
                            c = '\b';
                            break;
                        case 'f':
                            c = '\f';
                            break;
                        case 'n':
                            c = '\n';
                            break;
                        case 'r':
                            c = '\r';
                            break;
                        case 't':
                            c = '\t';
                            break;
                        case 'u':
                            if (i >= length) {
                                make('string', str).error("Unterminated string");
                            }
                            c = parseInt(this.substr(i + 1, 4), 16);
                            if (!isFinite(c) || c < 0) {
                                make('string', str).error("Unterminated string");
                            }
                            c = String.fromCharCode(c);
                            i += 4;
                            break;
                    }
                }
                str += c;
                i += 1;
            }
            i += 1;
            result.push(make('string', str));
            c = this.charAt(i);

// comment.

        } else if (c === '/' && this.charAt(i + 1) === '/') {
            i += 1;
            for (;;) {
                c = this.charAt(i);
                if (c === '\n' || c === '\r' || c === '') {
                    break;
                }
                i += 1;
            }

// combining

        } else if (prefix.indexOf(c) >= 0) {
            str = c;
            i += 1;
            while (true) {
                c = this.charAt(i);
                if (i >= length || suffix.indexOf(c) < 0) {
                    break;
                }
                str += c;
                i += 1;
            }
            result.push(make('operator', str));

// single-character operator

        } else {
            i += 1;
            result.push(make('operator', c));
            c = this.charAt(i);
        }
    }
    return result;
};

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

    var advance = function (ids, skip) {
        var a, o, t, v;

        if(skip) {
            t = tokens[token_nr];
            console.log("advance", skip, t);
            if (t.value == skip) {
                token_nr += 1;
                token = tokens[token_nr];
                return advance(ids, skip);
            }
        }

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
        token.line = t.line;
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
        // console.log("****************")
        // console.log("rbp: ", rbp)
        // console.log("previous", t.value);
        advance();
        // console.log("current", token.value, token.lbp);
        left = t.nud();
        // console.log("left", left.value);
        //console.log("expression:", rbp, t.rbp, t.value, token.value, token.rbp, token.lbp);
        while (rbp < token.lbp) {
            // console.log(token.lbp);
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
                if(s) {
                    a.push(s);
                }
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

    prefix("(", function () {
        var a = [];
        while (true) {
            a.push(expression(0));
            if (token.id !== ",") {
                break;
            }
            advance(",");
        }

        advance(")");

        if(a.length == 1) {
            return a[0];
        }

        this.first = a;
        this.arity = "unary";
        return this;
    });

    prefix("(", function () {
        var e = expression(0);
        advance(")");
        return e;
    });


    prefix("fn", function () {
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
//                    console.log("enter ::", token, a, listitems);
                    while(true) {
                        advance();
//                        console.log("::", token);
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
        advance("{");
        this.second = statements();
        advance("}");
        this.arity = "function";
        return this;
    });


    prefix("do", function () {
        advance("{");
        this.first = statements();
        advance("}");
        this.arity = "block";
        return this;
    });

    prefix("if", function () {

        this.branches = []
        var branch = {};
        branch.first = expression(0);
        advance("{");
        branch.second = statements(["}"]);
        this.branches.push(branch);
        advance("}");

        while(token.id == "elif") {
            branch = {};
            advance("elif");
            branch.first = expression(0);
            advance("{");
            branch.second = statements(["}"]);
            advance("}");
            this.branches.push(branch);
        }

        branch = {};

        if (token.id === "else") {
            advance("else");
            advance("{");
            branch.first = null;
            branch.second = statements(["}"]);
            advance("}");
            this.branches.push(branch);
        }

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
                if(n.arity == "(endline)") {
                    advance();
                    continue;
                }
                if (n.arity !== "name" && n.arity !== "literal") {
                    console.log(n);
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
        advance("}", "(endline)");
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
        this.first = expression(0);
        advance("{");
        this.second = statements(["}"]);
        advance("}");
        this.arity = "statement";
        return this;
    });

    stmt("for", function () {
        this.first = [expression(0)]
        while (token.id == ",") {
            advance();
            if(token.arity != "name" && token.arity != "literal") {
                token.error("expected name in for loop");
            }

            this.first.push(expression(0));
        }
        advance("in");
        this.second = expression(0);

        advance("{");
        this.third = statements(["}"]);
        advance("}");
        this.arity = "for";
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

function testprogram() {
    return fs.readFileSync("program.obn", "utf8");
}

function testast() {
    var parser = make_parse();
    var ast = parser(testprogram());

    return prettify(ast);
}

function parse(program) {
    var parser = make_parse();
    var ast = parser(program);
    return prettify(ast);
}

function testparse() {
    fs.writeFileSync('output.json', testast());
}

function prettify(ast, silent) {
    if(silent) {
        var cb = function(key, value) {
            if(key  == "scope" || key == "from" || key == "to" || key == "arity") {
                return undefined;
            }
            else {
                return value;
            }
        }
    } else {
        var cb = undefined;
    }

    return JSON.stringify(ast, cb, 2);
}

testparse();

return;
// create the http server
http.createServer(function (req, res) {
    // handle the routes
    if (req.method == 'POST') {
        // pipe the request data to the console
        var body = "";
        req.on('data', function(chunk) {
            console.log("Received body data:");
           body += chunk.toString();
            console.log(body);
        });

        req.on("end", function(){
            var decodedBody = qs.parse(body);
            console.log(decodedBody);
            res.writeHead(200, {'Content-Type': 'text/json'});
            var program = decodedBody['program'];
            console.log("prog", program);
            var ast = parse(program);
            console.log("ast", ast);
            res.write(ast);
            res.end();
        });

    }
}).listen(8084);
