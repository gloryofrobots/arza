from obin.compile.parse.token_type import *
from obin.compile.parse.node import list_node, empty_node
from obin.compile.parse.tokens import token_type_to_str


def parse_error_node(parser, message, node):
    assert isinstance(message, str)
    error_message = "Parse Error %d:%d %s" % (node.line, node.position, message)
    raise RuntimeError(error_message)


def _parse_error(message, args):
    raise RuntimeError(message, args)


def parse_error_simple(parser, message):
    assert isinstance(message, str)
    error_message = "Parse Error %d:%d %s" % (parser.token.line, parser.token.pos, message)
    raise RuntimeError(error_message)


def parse_error(parser, message, node):
    assert isinstance(message, str)
    error_message = "Parse Error %d:%d %s" % (parser.token.line, parser.token.pos, message)
    return _parse_error(error_message, (node,))


class Handler:
    def __init__(self):
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1
        self.rbp = -1
        self.value = None


def set_handler(parser, ttype, h):
    parser.handlers[ttype] = h
    return handler(parser, ttype)


def node_handler(parser, node):
    return handler(parser, node.type)


def handler(parser, ttype):
    assert ttype < TT_UNKNOWN
    try:
        return parser.handlers[ttype]
    except:
        return set_handler(parser, ttype, Handler())
        # parser.handlers[ttype] = Handler()
        # return handler(parser, ttype)
        # error(parser, "Handler not exists %s" % TT_TO_STR(ttype))


def nud(parser, node):
    handler = node_handler(parser, node)
    if not handler.nud:
        parse_error(parser, "Unknown token", node)
    return handler.nud(parser, node)


def std(parser, node):
    handler = node_handler(parser, node)
    if not handler.std:
        parse_error(parser, "Unknown token", node)

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
    rbp = handler.rbp
    if rbp == -1:
        parse_error(parser, "Right binding power can't be evaluated", node)
    return rbp


def lbp(parser, node):
    handler = node_handler(parser, node)
    lbp = handler.lbp
    if lbp == -1:
        parse_error(parser, "Left binding power can't be evaluated", node)
    return lbp


def led(parser, node, left):
    handler = node_handler(parser, node)
    if not handler.led:
        parse_error(parser, "Unknown token", node)

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


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error_simple(parser, "Wrong token type %s %s" % (token_type_to_str(type), parser.token))


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error_simple(parser,
                           "Wrong token type %s %s" % (str([token_type_to_str(type) for type in types]), parser.token))


def advance(parser):
    if parser.isend():
        return None

    return parser.next()


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    if parser.isend():
        return None

    return parser.next()


def advance_expected_one_of(parser, ttypes):
    check_token_types(parser, ttypes)

    if parser.isend():
        return None

    return parser.next()


def endofexpression(parser):
    if parser.isend():
        return None
    if parser.is_newline_occurred:
        # print "NL"
        return parser.node
    if parser.token_type == TT_END:
        return parser.node
    if parser.token_type == TT_SEMI:
        # print "SEMI"
        return advance(parser)

    parse_error_simple(parser, "Expressions must end with new line or ;")


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
        value = std(parser, node)
        endofexpression(parser)
        return value

    value = expression(parser, 0)
    endofexpression(parser)
    return value


def token_is_one_of(parser, types):
    return parser.token_type in types


def statements(parser, endlist=None):
    if not endlist:
        endlist = [TT_END, TT_ENDSTREAM]

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
        return empty_node()
    # TODO REMOVE IT
    elif length == 1:
        return stmts[0]

    return list_node(stmts)


def itself(parser, node):
    return node




def infix(parser, ttype, lbp, led):
    set_led(parser, ttype,  lbp, led)




def infixr(parser, ttype, lbp, led):
    set_led(parser, ttype, lbp, led)




def prefix(parser, ttype, nud):
    set_nud(parser, ttype, nud)


def stmt(parser, ttype,  std):
    set_std(parser, ttype, std)


def literal(parser, ttype):
    set_nud(parser, ttype, itself)


def symbol(parser, ttype, nud):
    h = handler(parser, ttype)
    h.lbp = 0
    set_nud(parser, ttype,  nud)


def skip(parser, ttype):
    while parser.token_type == ttype:
        advance(parser)


def empty(parser, node):
    return None



def is_assignment_node(node):
    token_type = node.type
    assert isinstance(token_type, int)
    if token_type == TT_ASSIGN \
            or token_type == TT_ADD_ASSIGN or token_type == TT_SUB_ASSIGN \
            or token_type == TT_MUL_ASSIGN or token_type == TT_DIV_ASSIGN \
            or token_type == TT_MOD_ASSIGN \
            or token_type == TT_BITAND_ASSIGN or token_type == TT_BITOR_ASSIGN \
            or token_type == TT_BITXOR_ASSIGN:
        return True
    return False


def condition(parser):
    node = expression(parser, 0)
    if is_assignment_node(node):
        parse_error_node(parser, "Assignment operators not allowed in conditions", node=node)
    return node
