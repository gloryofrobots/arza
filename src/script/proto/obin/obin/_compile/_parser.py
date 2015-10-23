__author__ = 'gloryofrobots'
import lexer
import tokens as T


def testprogram():
    data = ""
    with open("program.obn") as f:
        data = f.read()

    return data


class Node:
    def __init__(self, _type, value, position, line):
        self.type = _type
        self.value = value
        self.position = position
        self.line = line
        self.children = None
        self.arity = 0

    def init(self, arity):
        if not arity:
            return

        self.children = [None] * arity
        self.arity = arity

    def setchild(self, index, value):
        assert value is not None
        if isinstance(value, list):
            assert None not in value

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

    def __children_repr(self, nodes):
        children = []
        for child in nodes:
            if isinstance(child, list):
                children.append(self.__children_repr(child))
            elif isinstance(child, Node):
                children.append(child.to_dict())
            else:
                # children.append(child)
                raise ValueError("Node child wrong type", child)

        return children

    def to_dict(self):
        d = {"_type": T.TT_TO_STR(self.type), "_value": self.value, "_line": self.line
             # "arity": self.arity, "pos": self.position
             }

        if self.children:
            d['children'] = self.__children_repr(self.children)
            # d['children'] = [child.to_dict() if isinstance(child, Node) else child
            #                         for child in self.children if child is not None]

        return d

    def __repr__(self):
        import json

        d = self.to_dict()
        return json.dumps(d, sort_keys=True,
                          indent=2, separators=(',', ': '))


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
        # error(parser, "Handler not exists %s" % T.TT_TO_STR(ttype))


def nud(parser, node):
    handler = node_handler(parser, node)
    if not handler.nud:
        error(parser, "Unknown token", args=(node, str(parser.token)))
    return handler.nud(parser, node)


def std(parser, node):
    handler = node_handler(parser, node)
    if not handler.std:
        error(parser, "Unknown token", args=node)

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
    if not handler.led:
        error(parser, "Unknown token", args=node)

    return handler.led(parser, node, left)


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
        self.is_newline_occurred = False

    @property
    def token_type(self):
        return self.token.type

    def next(self):
        token = self.tokens.next()
        if token.type == T.TT_NEWLINE:
            # print "NEW LINE"
            self.is_newline_occurred = True
            while token.type == T.TT_NEWLINE:
                token = self.tokens.next()
        else:
            # print "TOKEN"
            self.is_newline_occurred = False

        #print token
        self.token = token
        self.node = Node(self.token.type, self.token.val, self.token.pos, self.token.line)
        return self.node

    def isend(self):
        return self.token.type == T.TT_ENDSTREAM


def error(parser, message, args=None):
    error_message = "Parse Error %d:%d %s" % (parser.token.line, parser.token.pos, message)
    raise RuntimeError(error_message, args)


def check_token_type(parser, type):
    if parser.token_type != type:
        error(parser, "Expected token type %s got token %s" % ((T.TT_TO_STR(type)), parser.token))


def check_token_types(parser, types):
    if parser.token_type not in types:
        error(parser, "Expected token type one of %s got token %s" %
              ([T.TT_TO_STR(type) for type in types], parser.token))


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
    if parser.is_newline_occurred:
        # print "NL"
        return parser.node
    if parser.token_type == T.TT_SEMI:
        # print "SEMI"
        return advance(parser)

    error(parser, "Expressions must end with new line or ;")


def expression(parser, _rbp):
    previous = parser.node
    # print "******"
    # print "rbp ", _rbp
    # print "previous", previous

    advance(parser)
    # print "current", parser.token

    left = nud(parser, previous)
    # print "left", left.value
    while True:
        if parser.is_newline_occurred:
            break
        _lbp = lbp(parser, parser.node)
        if _rbp >= _lbp:
            break
        previous = parser.node
        advance(parser)
        left = led(parser, previous, left)

    return left


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
        endlist = [T.TT_RCURLY, T.TT_ENDSTREAM]

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
        return None
    elif length == 1:
        return stmts[0]

    return stmts


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
    exp = expression(parser, 9)
    node.setsecond(exp)

    return node


def assignment(parser, ttype):
    infixr(parser, ttype, 10, led_infixr_assign)


def prefix_nud(parser, node):
    node.init(1)
    exp = expression(parser, 70)
    node.setfirst(exp)
    return node


def prefix(parser, ttype, nud=prefix_nud):
    set_nud(parser, ttype, nud)


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
    while parser.token_type == ttype:
        advance(parser)


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
    literal(parser, T.TT_NAME)

    symbol(parser, T.TT_ENDSTREAM)
    symbol(parser, T.TT_COLON)
    symbol(parser, T.TT_RPAREN)
    symbol(parser, T.TT_RCURLY)
    symbol(parser, T.TT_COMMA)
    symbol(parser, T.TT_ELSE)
    symbol(parser, T.TT_SEMI, nud=empty)

    constant(parser, T.TT_TRUE, True)
    constant(parser, T.TT_FALSE, False)
    constant(parser, T.TT_NIL, None)

    # precedence 5
    # infix(parser, T.TT_COMMA, 5)
    # infix(parser, T.TT_COLON, 5)

    """
    precedence 10
    = += -= *= /= %= &= ^= |=
    """
    assignment(parser, T.TT_ASSIGN)
    assignment(parser, T.TT_ADD_ASSIGN)
    assignment(parser, T.TT_SUB_ASSIGN)
    assignment(parser, T.TT_MUL_ASSIGN)
    assignment(parser, T.TT_DIV_ASSIGN)
    assignment(parser, T.TT_MOD_ASSIGN)
    assignment(parser, T.TT_OR_ASSIGN)
    assignment(parser, T.TT_AND_ASSIGN)
    assignment(parser, T.TT_XOR_ASSIGN)



    """
    precedence 20
    infix if
    """

    def _infix_if(parser, node, left):
        node.init(3)
        node.setfirst(expression(parser, 0))
        node.setsecond(left)
        advance_expected(parser, T.TT_ELSE)
        node.setthird(expression(parser, 0))
        return node

    infix(parser, T.TT_IF, 20, _infix_if)


    """
    precedence 25
    or
    """
    infix(parser, T.TT_OR, 25)

    """
    precedence 30
    AND
    """
    infix(parser, T.TT_AND, 30)


    """
    precedence 35
    |
    """
    infixr(parser, T.TT_BITOR, 35)

    """
    precedence 40
    ^
    """
    infixr(parser, T.TT_BITXOR, 40)


    """
    precedence 45
    &
    """
    infixr(parser, T.TT_BITAND, 45)

    """
    precedence 50
    in, is, <, <=, >, >=, !=, ==
    """
    #TODO is not and not is

    infix(parser, T.TT_IN, 50)
    infix(parser, T.TT_IS, 50)
    infix(parser, T.TT_LESS, 50)
    infix(parser, T.TT_LE, 50)
    infix(parser, T.TT_GREATER, 50)
    infix(parser, T.TT_GE, 50)
    infix(parser, T.TT_NE, 50)
    infix(parser, T.TT_EQ, 50)

    """
    precedence 55
    >> << >>>
    """
    infix(parser, T.TT_LSHIFT, 55)
    infix(parser, T.TT_RSHIFT, 55)
    infix(parser, T.TT_URSHIFT, 55)

    """
    precedence 60
    + -
    """
    infix(parser, T.TT_ADD, 60)
    infix(parser, T.TT_SUB, 60)

    """
    precedence 65
    * / %
    """
    infix(parser, T.TT_MUL, 65)
    infix(parser, T.TT_DIVIDE, 65)
    infix(parser, T.TT_MOD, 65)

    """
    precedence 70
    .
    """
    def _infix_dot(parser, node, left):
        node.init(2)
        node.setfirst(left)
        check_token_type(parser, T.TT_NAME)
        node.setsecond(parser.node)
        advance(parser)
        return node

    infix(parser, T.TT_DOT, 70, _infix_dot)

    """
    precedence 80
    [
    """
    def _infix_rsquare(parser, node, left):
        node.init(2)
        node.setfirst(left)
        node.setsecond(expression(parser, 0))
        advance_expected(parser, T.TT_RSQUARE)
        return node

    infix(parser, T.TT_LSQUARE, 80, _infix_rsquare)

    """
    precedence 90
    (
    """
    def _infix_lparen(parser, node, left):
        items = []
        if left.type == T.TT_DOT or left.type == T.TT_LSQUARE:
            node.init(3)
            node.setfirst(left.first())
            node.setsecond(left.second())
            node.setthird(items)
        else:
            node.init(2)
            node.setfirst(left)
            node.setsecond(items)
            """
            if ((left.arity !== "unary" || left.id !== "function") &&
                left.arity !== "name" && left.id !== "(" &&
                left.id !== "&&" && left.id !== "||" && left.id !== "?") {
                left.error("Expected a variable name.");
            }
            """
        if parser.node.type != T.TT_RPAREN:
            while True:
                items.append(expression(parser, 0))
                if parser.node.type != T.TT_COMMA:
                    break

                advance_expected(parser, T.TT_COMMA)

        advance_expected(parser, T.TT_RPAREN)
        return node

    infix(parser, T.TT_LPAREN, 90, _infix_lparen)


    """
    PREFIXES
    """

    prefix(parser, T.TT_NOT)
    prefix(parser, T.TT_SUB)
    prefix(parser, T.TT_ADD)

    def _prefix_backslash(parser, node):
        items = []
        node.init(2)
        # function name
        node.setfirst(expression(parser, 0))
        node.setsecond(items)
        if parser.token_type == T.TT_RPAREN:
            return node

        while True:
            items.append(expression(parser, 0))
            if parser.node.type != T.TT_COMMA or parser.is_newline_occurred:
                break

            advance_expected(parser, T.TT_COMMA)

        return node

    prefix(parser, T.TT_BACKSLASH, _prefix_backslash)

    def _prefix_lparen(parser, node):
        e = expression(parser, 0)
        advance_expected(parser, T.TT_RPAREN)
        return e

    prefix(parser, T.TT_LPAREN, _prefix_lparen)

    def _prefix_fn(parser, node):
        items = []
        node.init(3)
        if parser.token_type == T.TT_NAME:
            node.setfirst(parser.node)
            advance(parser)
        else:
            node.setfirst(Node(T.TT_NAME, "anonymous", parser.node.position))

        if parser.token_type == T.TT_LPAREN:
            advance_expected(parser, T.TT_LPAREN)
            if parser.token_type != T.TT_RPAREN:
                while True:
                    if parser.token_type == T.TT_NAME:
                        items.append(parser.node)
                        advance(parser)

                    if parser.token_type != T.TT_COMMA:
                        break

                    advance_expected(parser, T.TT_COMMA)

                advance_expected(parser, T.TT_RPAREN)

        node.setsecond(items)
        advance_expected(parser, T.TT_LCURLY)
        node.setthird(statements(parser))
        advance_expected(parser, T.TT_RCURLY)
        return node

    prefix(parser, T.TT_FN, _prefix_fn)

    def _prefix_do(parser, node):
        node.init(1)
        advance_expected(parser, T.TT_LCURLY)
        node.setfirst(statements(parser))
        advance_expected(parser, T.TT_RCURLY)
        return node

    prefix(parser, T.TT_DO, _prefix_do)

    def _prefix_if(parser, node):
        node.init(1)
        branches = []
        branch = [None] * 2
        branch[0] = expression(parser, 0)
        advance_expected(parser, T.TT_LCURLY)
        branch[1] = (statements(parser, [T.TT_RCURLY]))
        branches.append(branch)
        advance_expected(parser, T.TT_RCURLY)

        while parser.token_type == T.TT_ELIF:
            advance_expected(parser, T.TT_ELIF)

            branch = [None] * 2
            branch[0] = expression(parser, 0)
            advance_expected(parser, T.TT_LCURLY)
            branch[1] = (statements(parser, [T.TT_RCURLY]))
            branches.append(branch)
            advance_expected(parser, T.TT_RCURLY)

        if parser.token_type == T.TT_ELSE:
            branch = [None] * 2
            advance_expected(parser, T.TT_ELSE)
            advance_expected(parser, T.TT_LCURLY)
            branch[0] = []
            branch[1] = statements(parser, [T.TT_RCURLY])
            advance_expected(parser, T.TT_RCURLY)
            branches.append(branch)
        else:
            branches.append([])

        # append else branch anyway
        node.setfirst(branches)
        return node

    prefix(parser, T.TT_IF, _prefix_if)

    def _prefix_lsquare(parser, node):
        items = []
        node.init(1)
        if parser.token_type != T.TT_RSQUARE:
            while True:
                items.append(expression(parser, 0))
                if parser.token_type != T.TT_COMMA:
                    break

                advance_expected(parser, T.TT_COMMA)

        node.setfirst(items)
        advance_expected(parser, T.TT_RSQUARE)
        return node

    prefix(parser, T.TT_LSQUARE, _prefix_lsquare)

    def _prefix_lcurly(parser, node):
        items = []
        key = None
        value = None
        node.init(1)
        if parser.token_type != T.TT_RCURLY:
            while True:
                # TODO check it
                check_token_types(parser, [T.TT_NAME, T.TT_INT, T.TT_STR, T.TT_CHAR, T.TT_FLOAT])
                key = parser.node
                advance(parser)
                advance_expected(parser, T.TT_COLON)
                value = expression(parser, 0)
                items.append([key, value])
                if parser.token_type != T.TT_COMMA:
                    break

                advance_expected(parser, T.TT_COMMA)

        advance_expected(parser, T.TT_RCURLY)
        node.setfirst(items)
        return node

    prefix(parser, T.TT_LCURLY, _prefix_lcurly)

    def _stmt_return(parser, node):
        node.init(1)
        if token_is_one_of(parser, [T.TT_SEMI, T.TT_RCURLY]) or parser.is_newline_occurred:
            node.setfirst([])
        else:
            node.setfirst(expression(parser, 0))
        endofexpression(parser)
        return node

    stmt(parser, T.TT_RETURN, _stmt_return)
    # TODO CHECK
    # stmt(parser, T.TT_SEMI, empty)

    def _stmt_loop_flow(parser, node):
        endofexpression(parser)
        if parser.token_type != T.TT_RCURLY:
            error(parser, "Unreachable statement")
        return node

    stmt(parser, T.TT_BREAK, _stmt_loop_flow)
    stmt(parser, T.TT_CONTINUE, _stmt_loop_flow)

    def _stmt_while(parser, node):
        node.init(2)
        node.setfirst(expression(parser, 0))
        advance_expected(parser, T.TT_LCURLY)
        node.setsecond(statements(parser, [T.TT_RCURLY]))
        advance_expected(parser, T.TT_RCURLY)
        return node

    stmt(parser, T.TT_WHILE, _stmt_while)

    def _stmt_for(parser, node):
        node.init(3)
        vars = []
        vars.append(expression(parser, 0))
        while parser.token_type == T.TT_COMMA:
            advance(parser)
            if parser.token_type != T.TT_NAME:
                error(parser, "Wrong variable name in for loop")

            vars.append(expression(parser, 0))

        node.setfirst(vars)
        advance_expected(parser, T.TT_IN)
        node.setsecond(expression(parser, 0))

        advance_expected(parser, T.TT_LCURLY)
        node.setthird(statements(parser, [T.TT_RCURLY]))
        advance_expected(parser, T.TT_RCURLY)
        return node

    stmt(parser, T.TT_FOR, _stmt_for)


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
                          indent=2, separators=(',', ': '))
        f.write(repr)


ast = parse_string(testprogram())
write_ast(ast)
