__author__ = 'gloryofrobots'
import lexer
import tokens as T
from weakref import ref


def testprogram():
    data = ""
    with open("program.obn") as f:
        data = f.read()

    return data


def is_many(node):
    return isinstance(node, list)


def empty_node():
    return []


def is_empty_node(n):
    return isinstance(n, list) and len(n) == 0


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
        d = {"_type": T.token_type_to_str(self.type), "_value": self.value, "_line": self.line
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
        parse_error(parser, "Unknown token", args=(node, str(parser.token)))
    return handler.nud(parser, node)


def std(parser, node):
    handler = node_handler(parser, node)
    if not handler.std:
        parse_error(parser, "Unknown token", args=node)

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
        parse_error(parser, "Unknown token", args=node)

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


class TokenStream(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.node = None
        self.token = None
        self.is_newline_occurred = False

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

        # print token
        self.token = token
        self.node = Node(self.token.type, self.token.val, self.token.pos, self.token.line)
        return self.node


class BaseParser(object):
    def __init__(self, ts):
        self.handlers = {}
        self.ts = ts

    @property
    def token_type(self):
        return self.ts.token.type

    @property
    def is_newline_occurred(self):
        return self.ts.is_newline_occurred

    @property
    def node(self):
        return self.ts.node

    @property
    def token(self):
        return self.ts.token

    def next(self):
        return self.ts.next()

    def isend(self):
        return self.token_type == T.TT_ENDSTREAM


class Parser(BaseParser):
    def __init__(self, ts):
        super(Parser, self).__init__(ts)
        self.args_parser = args_parser_init(BaseParser(ts))
        self.module_name_parser = module_name_parser_init(BaseParser(ts))
        self.module_name_alias_parser = module_name_alias_parser_init(BaseParser(ts))
        self.import_alias_parser = import_alias_parser_init(BaseParser(ts))
        self.generic_signature_parser = generic_signature_parser_init(BaseParser(ts))
        code_parser_init(self)


def parse_error(parser, message, args=None, node=None):
    if not node:
        error_message = "Parse Error %d:%d %s" % (parser.token.line, parser.token.pos, message)
    else:
        error_message = "Parse Error %d:%d %s" % (node.line, node.position, message)

    raise RuntimeError(error_message, args)


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser, "Expected token type %s got token %s" % ((T.token_type_to_str(type)), parser.token))


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, "Expected token type one of %s got token %s" %
                    ([T.token_type_to_str(type) for type in types], parser.token))


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

    parse_error(parser, "Expressions must end with new line or ;")


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
        parse_error(parser, "Bad lvalue in assignment", left)
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
    check_token_type(parser, T.TT_ENDSTREAM)
    return stmts


def args_parser_init(parser):
    prefix(parser, T.TT_ELLIPSIS)
    literal(parser, T.TT_NAME)
    return parser


def infix_simple_pair(parser, node, left):
    node.init(2)
    node.setfirst(left)
    check_token_type(parser, T.TT_NAME)
    node.setsecond(parser.node)
    advance(parser)
    return node


def import_alias_parser_init(parser):
    infix(parser, T.TT_AS, 20, infix_simple_pair)
    literal(parser, T.TT_NAME)
    return parser


def module_name_parser_init(parser):
    infix(parser, T.TT_DOT, 10, infix_simple_pair)
    literal(parser, T.TT_NAME)
    return parser


def module_name_alias_parser_init(parser):
    infix(parser, T.TT_DOT, 10, infix_simple_pair)
    infix(parser, T.TT_AS, 20, infix_simple_pair)
    literal(parser, T.TT_NAME)
    return parser


def generic_signature_parser_init(parser):
    infix(parser, T.TT_OF, 10, infix_simple_pair)
    literal(parser, T.TT_NAME)
    return parser


def code_parser_init(parser):
    # *********************************************
    literal(parser, T.TT_INT)
    literal(parser, T.TT_FLOAT)
    literal(parser, T.TT_CHAR)
    literal(parser, T.TT_STR)
    literal(parser, T.TT_NAME)
    literal(parser, T.TT_TRUE)
    literal(parser, T.TT_FALSE)
    literal(parser, T.TT_NIL)
    literal(parser, T.TT_UNDEFINED)

    symbol(parser, T.TT_ENDSTREAM)
    symbol(parser, T.TT_COLON)
    symbol(parser, T.TT_RPAREN)
    symbol(parser, T.TT_RCURLY)
    symbol(parser, T.TT_COMMA)
    symbol(parser, T.TT_ELSE)
    symbol(parser, T.TT_SEMI, nud=empty)

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
    assignment(parser, T.TT_BITOR_ASSIGN)
    assignment(parser, T.TT_BITAND_ASSIGN)
    assignment(parser, T.TT_BITXOR_ASSIGN)

    """
    precedence 20
    infix if
    """

    def _infix_when(parser, node, left):
        node.init(3)
        node.setfirst(expression(parser, 0))
        node.setsecond(left)
        advance_expected(parser, T.TT_ELSE)
        node.setthird(expression(parser, 0))
        return node

    infix(parser, T.TT_WHEN, 20, _infix_when)

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
    # TODO is not and not is

    infix(parser, T.TT_IN, 50)
    infix(parser, T.TT_ISNOT, 50)
    infix(parser, T.TT_IS, 50)
    infix(parser, T.TT_LT, 50)
    infix(parser, T.TT_LE, 50)
    infix(parser, T.TT_GT, 50)
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
    infix(parser, T.TT_DIV, 65)
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

    def _infix_lsquare(parser, node, left):
        node.init(2)
        node.setfirst(left)
        node.setsecond(expression(parser, 0))
        advance_expected(parser, T.TT_RSQUARE)
        return node

    infix(parser, T.TT_LSQUARE, 80, _infix_lsquare)

    """
    precedence 90
    (
    """

    def _infix_lparen(parser, node, left):
        items = []
        if left.type == T.TT_DOT:
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
        if parser.token_type != T.TT_RPAREN:
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

    prefix(parser, T.TT_ELLIPSIS)

    prefix(parser, T.TT_BITNOT)
    prefix(parser, T.TT_NOT)
    prefix(parser, T.TT_SUB)
    prefix(parser, T.TT_ADD)

    def _prefix_lparen(parser, node):
        e = expression(parser, 0)
        if parser.node.type != T.TT_COMMA:
            advance_expected(parser, T.TT_RPAREN)
            return e

        node.init(1)
        items = [e]
        advance_expected(parser, T.TT_COMMA)

        if parser.token_type != T.TT_RPAREN:
            while True:
                items.append(expression(parser, 0))
                if parser.node.type != T.TT_COMMA:
                    break

                advance_expected(parser, T.TT_COMMA)

        advance_expected(parser, T.TT_RPAREN)
        node.setfirst(items)
        return node

    prefix(parser, T.TT_LPAREN, _prefix_lparen)

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

    def _parse_fn(parser):
        args = []
        body = []
        outers = []
        if parser.token_type == T.TT_NAME:
            name = parser.node
            advance(parser)
        else:
            name = empty_node()

        if parser.token_type == T.TT_LPAREN:
            advance_expected(parser, T.TT_LPAREN)
            if parser.token_type != T.TT_RPAREN:
                while True:
                    if parser.token_type == T.TT_NAME:
                        args.append(parser.node)
                        advance(parser)

                    if parser.token_type != T.TT_COMMA:
                        break

                    advance_expected(parser, T.TT_COMMA)

            if parser.token_type == T.TT_ELLIPSIS:
                rest = expression(parser.args_parser, 0)
                # advance(parser)
                args.append(rest)
                # advance_expected(parser, T.TT_NAME)

            advance_expected(parser, T.TT_RPAREN)

        advance_expected(parser, T.TT_LCURLY)
        if parser.token_type == T.TT_OUTER:
            advance_expected(parser, T.TT_OUTER)
            while True:
                if parser.token_type == T.TT_NAME:
                    outers.append(parser.node)
                    advance(parser)

                if parser.token_type != T.TT_COMMA:
                    break

                advance_expected(parser, T.TT_COMMA)

            if len(outers) == 0:
                parse_error(parser, "Outer variables not declared")

        body = statements(parser)
        if not body:
            body = empty_node()
        advance_expected(parser, T.TT_RCURLY)
        return name, args, outers, body

    def _prefix_fn(parser, node):
        node.init(3)
        name, args, outers, body = _parse_fn(parser)
        if not is_empty_node(name):
            parse_error(parser, "In expressions functions could not have names", node=node)
        node.setfirst(args)
        node.setsecond(outers)
        node.setthird(body)
        return node

    prefix(parser, T.TT_FN, _prefix_fn)
    """
    STATEMENTS
    """

    def _stmt_fn(parser, node):
        node.init(4)
        name, args, outers, body = _parse_fn(parser)
        if is_empty_node(name):
            parse_error(parser, "Function statement must be declared with name", node=node)
        node.setfirst(name)
        node.setsecond(args)
        node.setthird(outers)
        node.setfourth(body)
        return node

    stmt(parser, T.TT_FN, _stmt_fn)

    def _parse_object(parser):
        def _object_statement_to_expr(stmt):
            expr = Node(stmt.type, stmt.value, stmt.position, stmt.line)
            expr.init(2)
            expr.setfirst(stmt.second())
            expr.setsecond(stmt.third())
            return expr

        def _fn_statement_to_expr(stmt):
            expr = Node(stmt.type, stmt.value, stmt.position, stmt.line)
            expr.init(3)
            expr.setfirst(stmt.second())
            expr.setsecond(stmt.third())
            expr.setthird(stmt.fourth())
            return expr

        name = empty_node()
        traits = []
        items = []

        if parser.token_type == T.TT_NAME:
            name = parser.node
            advance(parser)

        if parser.token_type == T.TT_LPAREN:
            advance_expected(parser, T.TT_LPAREN)
            if parser.token_type != T.TT_RPAREN:
                while True:
                    if parser.token_type == T.TT_NAME:
                        traits.append(parser.node)
                        advance(parser)

                    if parser.token_type != T.TT_COMMA:
                        break

                    advance_expected(parser, T.TT_COMMA)

            advance_expected(parser, T.TT_RPAREN)

        advance_expected(parser, T.TT_LCURLY)
        if parser.token_type != T.TT_RCURLY:
            while True:
                if parser.token_type == T.TT_FN:
                    fn = statement(parser)
                    key = fn.first()
                    # dirty hack to convert statements to expression for compiler
                    value = _fn_statement_to_expr(fn)
                elif parser.token_type == T.TT_OBJECT:
                    obj = statement(parser)
                    key = obj.first()
                    # dirty hack to convert statements to expression for compiler
                    value = _object_statement_to_expr(obj)
                else:
                    # TODO check it
                    check_token_types(parser, [T.TT_NAME, T.TT_INT, T.TT_STR, T.TT_CHAR, T.TT_FLOAT])
                    key = parser.node
                    advance(parser)
                    advance_expected(parser, T.TT_ASSIGN)
                    value = expression(parser, 0)

                items.append([key, value])
                if parser.token_type == T.TT_RCURLY:
                    break

        advance_expected(parser, T.TT_RCURLY)
        return name, traits, items

    """
    object AliceTraits(Human, Insect, Fucking, Shit) {
        id = 42
        name = "Alice"
        object Bob(Human) {
            fn hello(self) {
                return "I am Bob"
            }
        }
        fn greetings(self) {
            return "Hello from" + self.name
        }
        goNorth = fn(self) {
            "I " + self.name + " go North"
        }
    }

    """

    def _prefix_object(parser, node):
        node.init(2)
        name, traits, body = _parse_object(parser)
        if not is_empty_node(name):
            parse_error(parser, "In expressions objects could not have names", node=node)
        node.setfirst(traits)
        node.setsecond(body)
        return node

    prefix(parser, T.TT_OBJECT, _prefix_object)

    def _stmt_object(parser, node):
        node.init(3)
        name, traits, items = _parse_object(parser)
        # TODO move this check to parse object or add support for error token in error func
        if is_empty_node(name):
            parse_error(parser, "Object statement must have name", node=node)
        node.setfirst(name)
        node.setsecond(traits)
        node.setthird(items)
        return node

    stmt(parser, T.TT_OBJECT, _stmt_object)

    def _stmt_single(parser, node):
        node.init(1)
        if token_is_one_of(parser, [T.TT_SEMI, T.TT_RCURLY]) or parser.is_newline_occurred:
            node.setfirst([])
        else:
            node.setfirst(expression(parser, 0))
        endofexpression(parser)
        return node

    stmt(parser, T.TT_RETURN, _stmt_single)
    stmt(parser, T.TT_THROW, _stmt_single)

    def _stmt_outer(parser, node):
        parse_error(parser, "Outer variables can be declared only in first function statement")

    stmt(parser, T.TT_OUTER, _stmt_outer)

    # stmt(parser, T.TT_SEMI, empty)

    def _stmt_loop_flow(parser, node):
        endofexpression(parser)
        if parser.token_type != T.TT_RCURLY:
            parse_error(parser, "Unreachable statement")
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
        # set big bp to overrinding IN binding power
        vars.append(expression(parser, 70))
        while parser.token_type == T.TT_COMMA:
            advance(parser)
            if parser.token_type != T.TT_NAME:
                parse_error(parser, "Wrong variable name in for loop")

            vars.append(expression(parser, 0))

        node.setfirst(vars)
        advance_expected(parser, T.TT_IN)
        node.setsecond(expression(parser, 0))

        advance_expected(parser, T.TT_LCURLY)
        node.setthird(statements(parser, [T.TT_RCURLY]))
        advance_expected(parser, T.TT_RCURLY)
        return node

    stmt(parser, T.TT_FOR, _stmt_for)

    def _stmt_generic(parser, node):
        if parser.token_type != T.TT_NAME:
            parse_error(parser, "Wrong generic name")
        name = parser.node
        advance(parser)

        if parser.token_type == T.TT_LCURLY or parser.token_type == T.TT_LPAREN:
            node.init(2)
            funcs = _parse_reify_funcs(parser)
            node.setfirst(name)
            node.setsecond(funcs)
        else:
            node.init(1)
            node.setfirst(name)

        return node

    stmt(parser, T.TT_GENERIC, _stmt_generic)

    def _stmt_trait(parser, node):
        node.init(1)
        name = expression(parser, 0)
        if name.type != T.TT_NAME:
            parse_error(parser, "Wrong trait name")
        node.setfirst(name)
        return node

    stmt(parser, T.TT_TRAIT, _stmt_trait)

    def _parse_reify_fn(_parser, _signature_parser):
        signature = []

        advance_expected(parser, T.TT_LPAREN)
        while _parser.token_type != T.TT_RPAREN:
            sig = expression(_signature_parser, 0)
            signature.append(sig)

            if _parser.token_type != T.TT_COMMA:
                break

            advance_expected(_signature_parser, T.TT_COMMA)

        advance_expected(_parser, T.TT_RPAREN)
        advance_expected(parser, T.TT_LCURLY)

        body = statements(parser)
        # TODO FIX IT
        if not body:
            body = empty_node()

        advance_expected(parser, T.TT_RCURLY)
        return [signature, body]

    def _parse_reify_funcs(parser):
        generic_signature_parser = parser.generic_signature_parser
        funcs = []
        if parser.token_type == T.TT_LPAREN:
            func = _parse_reify_fn(parser, generic_signature_parser)
            funcs.append(func)
        else:
            advance_expected(parser, T.TT_LCURLY)
            while parser.token_type == T.TT_LPAREN:
                func = _parse_reify_fn(parser, generic_signature_parser)
                funcs.append(func)

            advance_expected(parser, T.TT_RCURLY)

        if len(funcs) == 0:
            parse_error(parser, "Empty reify statement")

        return funcs

    def _stmt_reify(parser, node):
        node.init(2)

        if parser.token_type != T.TT_NAME:
            parse_error(parser, "Wrong generic name in reify statement")

        name = parser.node
        advance(parser)

        funcs = _parse_reify_funcs(parser)

        node.setfirst(name)
        node.setsecond(funcs)
        return node

    stmt(parser, T.TT_REIFY, _stmt_reify)

    def _stmt_import(parser, node):
        # import statement needs three different parsers :(

        # all parsers share same token stream and token_type checks can be made for any of them
        module_name_parser = parser.module_name_parser
        module_name_alias_parser = parser.module_name_alias_parser
        import_alias_parser = parser.import_alias_parser

        # first statement can be import x.y.z as c
        imported = expression(module_name_alias_parser, 0)
        # destructuring import x as y from a.b.c
        if parser.token_type == T.TT_COMMA or parser.token_type == T.TT_FROM:
            items = [imported]

            # aliases like x as y
            while parser.token_type == T.TT_COMMA:
                advance(parser)
                items.append(expression(import_alias_parser, 0))

            advance_expected(module_name_parser, T.TT_FROM)
            # module name x.y.z
            module = expression(module_name_parser, 0)
            node.init(2)
            node.setfirst(items)
            node.setsecond(module)
        # simple import x.y.z as c
        else:
            node.init(1)
            node.setfirst(imported)

        return node

    stmt(parser, T.TT_IMPORT, _stmt_import)


"""
import fire as army_fire, Weapon as weapon, private as army_private from state.military

import military.army.behavior as bh
print(bh)
import military.army.behavior
print(behavior)
print(fire, army_unit_destroy, army_unit_attack)


"""


def parser_from_str(txt):
    lx = lexer.lexer(txt)
    tokens = lx.tokens()
    ts = TokenStream(tokens)
    parser = Parser(ts)
    return parser


def parse_string(txt):
    parser = parser_from_str(txt)
    stmts = parse(parser)
    # print stmts
    return stmts


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

# ast = parse_string(
#     """
#     reify fire {
#         (self of Soldier, other of Civilian) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#         (self of Soldier, other1, other2) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#         (self, other1, other2, other3 of Enemy) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#     }
#     """
# )
# print ast
# write_ast(ast)
