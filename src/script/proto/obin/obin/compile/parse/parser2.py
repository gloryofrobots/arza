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

    def to_dict(self):
        d = {"type": T.TT_TO_STR(self.type), "value": self.value,
             "arity": self.arity, "pos": self.position}

        if self.children:
            d['children'] = [child.to_dict() for child in self.children if child is not None]

        return d

    def __repr__(self):
        import json

        d = self.to_dict()
        return json.dumps(d, sort_keys=True,
                  indent=4, separators=(',', ': '))


def set_handler(parser, ttype, h):
    parser.handlers[ttype] = h
    return handler(parser, ttype)

def node_handler(parser, node):
    return handler(parser, node.type)

def handler(parser, ttype):
    assert ttype < T.TT_UNKNOWN
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
        error(parser, "Expected token type %s got token %s" % ((T.TT_TO_STR(type)), parser.token))

def check_token_types(parser, types):
    for t in types:
        check_token_type(parser, t)

def advance(parser):
    if parser.isend():
        return None

    return parser.next()

def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

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
    # print "******"
    # print "rbp ", _rbp
    # print "previous", previous.value

    advance(parser)
    # print "current", parser.token

    left = nud(parser, previous)
    # print "left", left.value
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

def set_lbp(parser, ttype, _lbp):
    h = handler(parser, ttype)
    h.lbp = _lbp

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

def stmt(parser, ttype, std):
    set_std(parser, ttype, std)

def literal(parser, ttype):
    set_nud(parser, ttype, itself)

def symbol(parser, ttype, bp=0, nud=None):
    h = handler(parser, ttype)
    h.lbp = bp
    if not nud:
        return
    set_nud(parser, ttype, nud)

def skip(parser, ttype):
    while True:
        if parser.token_type == ttype:
            advance(parser)
            continue
        break


def empty(parser, node):
    return None





def parse(parser):
    parser.next()
    stmts = statements(parser)
    print stmts
    check_token_type(parser, T.TT_ENDSTREAM)
    return stmts


def parser_init(parser):
    literal(parser, T.TT_INT)
    literal(parser, T.TT_FLOAT)
    literal(parser, T.TT_CHAR)
    literal(parser, T.TT_STR)

    symbol(parser, T.TT_ENDSTREAM)
    symbol(parser, T.TT_NAME)
    symbol(parser, T.TT_COLON)
    symbol(parser, T.TT_RPAREN)
    symbol(parser, T.TT_RCURLY)
    symbol(parser, T.TT_COMMA)
    symbol(parser, T.TT_ELSE)
    symbol(parser, T.TT_NEWLINE, nud=empty)
    symbol(parser, T.TT_SEMI, nud=empty)

    constant(parser, T.TT_TRUE, True)
    constant(parser, T.TT_FALSE, False)
    constant(parser, T.TT_NIL, None)

    assignment(parser, T.TT_ASSIGN)
    assignment(parser, T.TT_ADD_ASSIGN)
    assignment(parser, T.TT_SUB_ASSIGN)

    infixr(parser, T.TT_AND, 30)
    infixr(parser, T.TT_OR, 30)
    infixr(parser, T.TT_EQ, 40)
    infixr(parser, T.TT_IS, 40)
    infixr(parser, T.TT_NE, 40)
    infixr(parser, T.TT_GREATER, 40)
    infixr(parser, T.TT_GE, 40)
    infixr(parser, T.TT_LESS, 40)
    infixr(parser, T.TT_LE, 40)

    infix(parser, T.TT_ADD, 50)
    infix(parser, T.TT_SUB, 50)
    infix(parser, T.TT_MUL, 60)
    infix(parser, T.TT_DIVIDE, 60)

    prefix(parser, T.TT_NOT)
    prefix(parser, T.TT_SUB)

    def _infix_if(parser, node, left):
        node.init(3)
        node.setfirst(expression(parser, 0))
        node.setsecond(left)
        advance_expected(parser, T.TT_ELSE)
        node.setthird(expression(parser, 0))
        return node

    infix(parser, T.TT_IF, 20, _infix_if)

    def _infix_dot():
        pass
    
"""
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
                if(token.arity == "name" || token.arity == "literal") {
                    arg.arity = token.arity;
                    arg.value = token.value;
                    arg.id = token.id;

                    define(token);
                    a.push(arg);
                    advance();
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


};


"""
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
    if not isinstance(ast, list):
        ast = [ast.to_dict()]
    else:
        ast = [node.to_dict() for node in ast]
    with open("output.json", "w") as f:
        repr = json.dumps(ast, sort_keys=True,
                              indent=4, separators=(',', ': '))
        f.write(repr)

ast = parse_string("2+3*5")
write_ast(ast)

