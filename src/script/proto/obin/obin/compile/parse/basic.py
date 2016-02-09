from obin.compile.parse.token_type import *
from obin.compile.parse import node_type
from obin.compile.parse import nodes
from obin.compile.parse.tokens import token_type_to_str
from obin.types import space, api
from obin.runtime import error
from obin.misc.strutil import get_line, get_line_for_position

TERM_BLOCK = [TT_END, TT_SEMI]
TERM_IF = [TT_ELIF, TT_ELSE]
TERM_FILE = [TT_ENDSTREAM]
TERM_CASE = [TT_CASE] + TERM_BLOCK
TERM_CATCH = [TT_FINALLY] + TERM_BLOCK
TERM_TRY = [TT_CATCH]

LOOP_CONTROL_TOKENS = [TT_END, TT_ELSE, TT_ELIF, TT_CASE]

def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    return error.throw(error.Errors.PARSE,
                       space.newtuple([
                           space.newint(position),
                           space.newstring(u"Unknown Token"),
                           space.newstring(line)
                       ]))


def parse_error(parser, message, node):
    line = get_line(parser.ts.src, api.to_i(nodes.node_line(node)))
    return error.throw(error.Errors.PARSE,
                       space.newtuple([
                           space.newtuple([nodes.node_position(node),
                                           nodes.node_line(node),
                                           nodes.node_column(node)]),
                           nodes.node_to_string(node),
                           space.newstring(message),
                           space.newstring(line)
                       ]))


class Handler:
    def __init__(self):
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1
        self.rbp = -1
        self.value = None


def has_handler(parser, ttype):
    return ttype in parser.handlers


def handler(parser, ttype):
    assert ttype < TT_UNKNOWN
    try:
        return parser.handlers[ttype]
    except:
        parse_error(parser, u"Invalid token", parser.node)

def get_or_create_handler(parser, ttype):
    if not has_handler(parser, ttype):
        return set_handler(parser, ttype, Handler())
    return handler(parser, ttype)


def set_handler(parser, ttype, h):
    parser.handlers[ttype] = h
    return handler(parser, ttype)


def node_handler(parser, node):
    ttype = nodes.node_token_type(node)
    return handler(parser, ttype)


def nud(parser, node):
    handler = node_handler(parser, node)
    if not handler.nud:
        parse_error(parser, u"Unknown token nud", node)
    return handler.nud(parser, node)


def std(parser, node):
    handler = node_handler(parser, node)
    if not handler.std:
        parse_error(parser, u"Unknown token std", node)

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
        parse_error(parser, u"Right binding power can't be evaluated", node)
    return rbp


def lbp(parser, node):
    handler = node_handler(parser, node)
    lbp = handler.lbp
    if lbp == -1:
        parse_error(parser, u"Left binding power error", node)
    return lbp


def led(parser, node, left):
    handler = node_handler(parser, node)
    if not handler.led:
        parse_error(parser, u"Unknown token led", node)

    return handler.led(parser, node, left)


def set_nud(parser, ttype, fn):
    h = get_or_create_handler(parser, ttype)
    h.nud = fn


def set_std(parser, ttype, fn):
    h = get_or_create_handler(parser, ttype)
    h.std = fn


def set_led(parser, ttype, lbp, fn):
    h = get_or_create_handler(parser, ttype)
    h.lbp = lbp
    h.led = fn


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser, u"Wrong token type, expected %s, got %s" % (token_type_to_str(type),
                                                                        token_type_to_str(parser.token_type)),
                    parser.node)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, u"Wrong token type, expected one of %s, got %s" %
                    (unicode([token_type_to_str(type) for type in types]),
                     token_type_to_str(parser.token_type)), parser.node)

def check_node_types(parser, node, types):
    ntype = nodes.node_type(node)
    if ntype not in types:
        parse_error(parser, u"Wrong node type, expected one of %s, got %s" %
                    (unicode([node_type.node_type_to_str(type) for type in types]),
                     node_type.node_type_to_str(ntype)), node)

def advance(parser):
    if parser.isend():
        return None

    return parser.next()


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    if parser.isend():
        return None

    return parser.next()


def advance_end(parser):
    advance_expected_one_of(parser, TERM_BLOCK)


def advance_expected_one_of(parser, ttypes):
    check_token_types(parser, ttypes)

    if parser.isend():
        return None

    return parser.next()


def endofexpression(parser):
    if parser.isend():
        return None
    if parser.is_newline_occurred:
        return parser.node
    if parser.token_type in TERM_BLOCK:
        return parser.node
    if parser.token_type == TT_COMMA:
        return advance(parser)

    parse_error(parser, u"Expected end of expression mark", parser.node)


def expression(parser, _rbp):
    previous = parser.node
    # print "******"
    # print "rbp ", _rbp
    # print "previous", previous

    advance(parser)

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


def statements(parser, endlist):
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
        return parse_error(parser, u"Expected one or more expressions", parser.node)

    return nodes.list_node(stmts)


def infix(parser, ttype, lbp, led):
    set_led(parser, ttype, lbp, led)


def prefix(parser, ttype, nud):
    set_nud(parser, ttype, nud)


def stmt(parser, ttype, std):
    set_std(parser, ttype, std)


def literal(parser, ttype):
    from obin.compile.parse.callbacks import itself
    set_nud(parser, ttype, itself)


def symbol(parser, ttype, nud):
    h = get_or_create_handler(parser, ttype)
    h.lbp = 0
    set_nud(parser, ttype, nud)


def skip(parser, ttype):
    while parser.token_type == ttype:
        advance(parser)


def empty(parser, node):
    return None


def is_assignment_node(node):
    token_type = nodes.node_token_type(node)
    assert isinstance(token_type, int)
    if token_type == TT_ASSIGN:
        return True
    return False


def condition(parser):
    node = expression(parser, 0)
    if is_assignment_node(node):
        parse_error(parser, u"Assignment operators not allowed in conditions", node)
    return node


def prefix_condition(parser):
    node = expression(parser, 0)
    if is_assignment_node(node):
        parse_error(parser, u"Assignment operators not allowed in conditions", node)
    # call endofexpression to allow one line prefixes like if x == 1, x end
    endofexpression(parser)
    return node
