__author__ = 'gloryofrobots'
import lexer
import tokens as T

def testprogram():
    data = ""
    with open("program.obn") as f:
        data = f.read()

    return data


class Node:
    def __init__(self, _type, value, position):
        self.type = _type
        self.value = value
        self.position = position
        self.children = None
        self.arity = 0

    def init(self, arity):
        if not arity:
            return

        self.children = [None] * arity
        self.arity = arity

    def setchild(self, index, value):
        self.children[index] = value

    def getchild(self, index):
        return self.children[index]

    def setfirst(self, value):
        self.setchild(0, value)

    def setsecond(self, value):
        self.setchild(1, value)

    def setthird(self, value):
        self.setchild(2, value)

    def setfourth(self, value):
        self.setchild(3, value)

    def first(self):
        return self.getchild(0)

    def second(self):
        return self.getchild(1)

    def third(self):
        return self.getchild(2)

    def fourth(self):
        return self.getchild(3)

    def __repr__(self):
        d = {"type": self.type, "value": self.value,
             "arity": self.arity, "pos": self.position,
             "items": [str(item) for item in self.items if item is not None]}
        import json
        return json.dumps(d, sort_keys=True,
                  indent=4, separators=(',', ': '))


def set_handler(parser, ttype, h):
    parser.handlers[ttype] = h
    return handler(parser, ttype)

def node_handler(parser, node):
    return handler(parser, node.type)

def handler(parser, ttype):
    assert ttype != T.TT_ENDSTREAM
    try:
        return parser.handlers[ttype]
    except:
        return set_handler(parser, ttype, Handler())
        # parser.handlers[ttype] = Handler()
        # return handler(parser, ttype)
        #error(parser, "Handler not exists %s" % T.TT_TO_STR(ttype))

def nud(parser, node):
    handler = node_handler(parser, node)
    return handler.nud(parser, node)

def std(parser, node):
    handler = node_handler(parser, node)

    return handler.std(parser, node)

def has_nud(parser, node):
    handler = node_handler(parser, node)
    return handler.nud is not None

def has_led(parser, node):
    handler = node_handler(parser, node)
    return handler.led is not None

def has_std(parser, node):
    handler = node_handler(parser, node)
    return handler.std is not None

def rbp(parser, node):
    handler = node_handler(parser, node)
    return handler.rbp

def lbp(parser, node):
    handler = node_handler(parser, node)
    return handler.lbp

def led(parser, node, left):
    handler = node_handler(parser, node)

    return handler.led(parser, node, left)


class Handler(object):
    def __init__(self):
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = None
        self.rbp = None
        self.value = None

class Parser(object):
    def __init__(self, tokens):
        self.handlers = {}
        self.node = None
        self.token = None
        self.tokens = tokens

    @property
    def token_type(self):
        return self.token.type

    def next(self):
        self.token = self.tokens.next()
        self.node = Node(self.token.type, self.token.val, self.token.pos)
        return self.node

    def isend(self):
        return self.token.type == T.TT_ENDSTREAM

def error(parser, message, args=None):
    raise RuntimeError(message, args)

def check_token_type(parser, type):
    if parser.token.type != type:
        error(parser, "Expected token type %s got token %s" % ((str(type)), parser.token))

def check_token_types(parser, types):
    for t in types:
        check_token_type(parser, t)

def advance(parser):
    if parser.isend():
        return None

    return parser.next()

def endofexpression(parser):
    if parser.isend():
        return None

    check_token_types(parser, [T.TT_SEMI, T.TT_NEWLINE])
    return advance(parser)

def expression(parser, _rbp):
    previous = parser.node
    print "******"
    print "rbp ", _rbp
    print "previous", previous.value

    advance(parser)
    print "current", parser.token

    left = nud(parser, previous)
    print "left", left.value
    while True:
        _lbp = lbp(parser, parser.node)
        if _rbp >= _lbp:
            break
        previous = parser.node
        advance(parser)
        left = led(parser, previous, left)

    return left
"""
var expression = function (rbp) {
        var left;
        var t = token;
        // console.log("****************")
         console.log("rbp: ", rbp)
         console.log("previous", t.value);
        advance();
         console.log("current", token.value, token.lbp);
        left = t.nud();
         console.log("left", left.value);
        console.log("expression:", rbp, t.rbp, t.value, token.value, token.rbp, token.lbp);
        while (rbp < token.lbp) {
             console.log(token.lbp);
            t = token;
            advance();
           //console.log("expression2:",   token.value, token.rbp, token.lbp);

            left = t.led(left);
        }
        return left;
    };
"""
def statement(parser):
    node = parser.node

    if has_std(parser, node):
        advance(parser)
        return std(parser, node)

    value = expression(parser, 0)
    endofexpression(parser)
    return value

def token_is_one_of(parser, types):
    return parser.token_type in types

def statements(parser, endlist=None):
    if not endlist:
        endlist = [T.TT_RCURLY, T.TT_NEWLINE, T.TT_ENDSTREAM]

    s = None
    stmts = []
    while True:
        if token_is_one_of(parser, endlist):
            break
        s = statement(parser)

        if s is None:
            continue
        stmts.append(s)

    length = len(stmts)
    if length == 0:
        return  None
    elif length == 1:
        return stmts[0]

    return stmts

def set_nud(parser, ttype, fn):
    h = handler(parser, ttype)
    h.nud = fn

def set_std(parser, ttype, fn):
    h = handler(parser, ttype)
    h.std = fn

def set_led(parser, ttype, lbp, fn):
    h = handler(parser, ttype)
    h.lbp = lbp
    h.led = fn

def itself(parser, node):
    return node

def nud_constant(parser, node):
    h = node_handler(parser, node)
    node.value = h.value
    node.init(0)
    return node

def constant(parser, ttype, value):
    h = handler(parser, ttype)
    h.value = value
    set_nud(parser, ttype, nud_constant)

def led_infix(parser, node, left):
    h = node_handler(parser, node)
    node.init(2)
    node.setfirst(left)
    exp = None
    while exp is None:
        exp = expression(parser, h.lbp)

    node.setsecond(exp)
    return node

def infix(parser, ttype, lbp, led=led_infix):
    set_led(parser, ttype, lbp, led)


def led_infixr(parser, node, left):
    h = node_handler(parser, node)
    node.init(2)

    node.setfirst(left)
    exp = expression(parser, h.lbp - 1)
    node.setsecond(exp)

    return node

def infixr(parser, ttype, lbp, led=led_infixr):
    set_led(parser, ttype, lbp, led)

def led_infixr_assign(parser, node, left):
    node.init(2)
    if left.type not in [T.TT_DOT, T.TT_LSQUARE, T.TT_NAME, T.TT_COMMA]:
        error(parser, "Bad lvalue in assignment", left)
    node.setfirst(left)
    exp = expression(parser, node, 9)
    node.setsecond(exp)

    return node

def assignment(parser, ttype):
    infixr(parser, ttype, 10, led_infixr_assign)

def prefix_nud(parser, node):
    node.init(1)
    exp = expression(parser, 70)
    node.setfirst(exp)
    return node

def prefix(parser, ttype):
    set_nud(parser, ttype, prefix_nud)

def std_statement(parser, ttype, std):
    set_std(parser, ttype, std)

def literal(parser, ttype):
    set_nud(parser, ttype, itself)

def empty(parser, node):
    return None

def parse(parser):
    parser.next()
    stmts = statements(parser)
    check_token_type(parser, T.TT_ENDSTREAM)
    return stmts


def parser_init(parser):
    infix(parser, T.TT_ADD, 50)
    infix(parser, T.TT_SUB, 50)
    infix(parser, T.TT_MUL, 60)
    infix(parser, T.TT_DIVIDE, 60)
    literal(parser, T.TT_INT)
    literal(parser, T.TT_FLOAT)
    literal(parser, T.TT_CHAR)
    literal(parser, T.TT_STR)

    assignment(parser, T.TT_ASSIGN)


def parser_from_str(txt):
    lx = lexer.lexer(txt)
    tokens = lx.tokens()
    parser = Parser(tokens)
    parser_init(parser)
    return parser

def parse_string(txt):
    parser = parser_from_str(txt)
    return parse(parser)


def test_lexer():
    txt = testprogram()
    lx = lexer.lexer(txt)
    try:
        for tok in lx.tokens():
            print(tok)
    except lexer.LexerError as e:
        print "Lexer Error at ", e.pos
        print txt[e.pos:]


def write_ast(ast):
    import json
    repr = json.dumps(ast, sort_keys=True,
                      indent=4, separators=(',', ': '))
    print repr

ast = parse_string("2+3")
write_ast(ast)

"""


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

    var skipId = function(id){
//        console.log("TOKEN ", token, id);
        while(true) {
            if(token.id == id) {
                advance();
                continue;
            }
            break;
        }
    }

    var advance = function (ids) {
        var a, o, t, v;
        if(arguments.length > 1) {
            throw new Error("Wrog args");
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
        skipId("(endline)");
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
        skipId("(endline)");
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
//        console.log("AFTER SKIP", token);
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


"""