from obin.compile.parse.token_type import *
from obin.compile.parse import node_type
from obin.compile.parse import nodes
from obin.compile.parse.tokens import token_type_to_str
from obin.types import space, api, root, plist, environment
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


class ParserScope(root.W_Any):
    def __init__(self):
        self.operators = space.newmap()
        self.macro = space.newmap()


class ParseState:
    def __init__(self, process, env, ts):
        self.ts = ts
        self.process = process
        self.env = env
        self.scopes = plist.empty()


def parser_enter_scope(parser):
    parser.state.scopes = plist.cons(ParserScope(), parser.state.scopes)


def parser_exit_scope(parser):
    head = plist.head(parser.state.scopes)
    parser.state.scopes = plist.tail(parser.state.scopes)
    return head


def parser_current_scope(parser):
    return plist.head(parser.state.scopes)


def parser_current_scope_add_operator(parser, op_name, op):
    cur_scope = parser_current_scope(parser)
    api.put(cur_scope.operators, op_name, op)


def parser_current_scope_find_operator_or_create_new(parser, op_name):
    cur_scope = parser_current_scope(parser)
    op = api.lookup(cur_scope.operators, op_name, space.newnil())
    if space.isnil(op):
        return newoperator()
    return op


def parser_find_operator(parser, op_name):
    undef = space.newnil()
    cur_scope = parser_current_scope(parser)
    scopes = parser.state.scopes
    for scope in scopes:
        op = api.lookup(scope.operators, op_name, undef)
        if not space.isnil(op):
            return op

    op = environment.get_operator(parser.state.env, op_name)
    if not space.isnil(op):
        api.put(cur_scope.operators, op_name, op)

    return op


def parse_env_statements(parser, termination_tokens):
    parser_enter_scope(parser)
    stmts = statements(parser, termination_tokens)
    scope = parser_exit_scope(parser)
    return stmts, scope


class W_Operator(root.W_Hashable):
    def __init__(self):
        root.W_Hashable.__init__(self)
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1

        self.prefix_function = None
        self.infix_function = None

    def _compute_hash_(self):
        hash = 0
        if self.prefix_function:
            hash += api.hash_i(self.prefix_function)
        if self.infix_function:
            hash += api.hash_i(self.infix_function)
        return hash

    def prefix_s(self):
        return "'%s'" % api.to_s(self.prefix_function) if self.prefix_function else ""

    def infix_s(self):
        return "'%s'" % api.to_s(self.infix_function) if self.infix_function else ""

    def _equal_(self, other):
        if not isinstance(other, W_Operator):
            return False
        if self.nud != other.nud or self.led != other.led \
                or self.std != other.std and self.lbp != other.lbp:
            return False

        if self.prefix_function and other.prefix_function:
            if not api.equal_b(self.prefix_function, other.prefix_function):
                return False
        elif self.prefix_function or other.prefix_function:
            return False

        if self.infix_function and other.infix_function:
            if not api.equal_b(self.infix_function, other.infix_function):
                return False
        elif self.infix_function or other.infix_function:
            return False

        return True

    def _to_string_(self):
        return '<operator %s %s>' % (self.prefix_s(), self.infix_s())


def newoperator():
    return W_Operator()


def parser_has_operator(parser, ttype):
    return ttype in parser.handlers


def parser_operator(parser, ttype):
    assert ttype < TT_UNKNOWN
    try:
        return parser.handlers[ttype]
    except:
        return parse_error(parser, u"Invalid token", parser.node)


def get_or_create_operator(parser, ttype):
    if not parser_has_operator(parser, ttype):
        return parser_set_operator(parser, ttype, newoperator())
    return parser_operator(parser, ttype)


def parser_set_operator(parser, ttype, h):
    parser.handlers[ttype] = h
    return parser_operator(parser, ttype)


def node_operator(parser, node):
    ttype = nodes.node_token_type(node)
    if not parser.allow_overloading:
        return parser_operator(parser, ttype)

    if ttype != TT_OPERATOR:
        return parser_operator(parser, ttype)

    # in case of operator
    op = parser_find_operator(parser, nodes.node_value(node))
    if op is None or space.isnil(op):
        return parse_error(parser, u"Invalid operator", node)
    return op


def nud(parser, node):
    handler = node_operator(parser, node)
    if not handler.nud:
        parse_error(parser, u"Unknown token nud", node)
    return handler.nud(parser, handler, node)


def std(parser, node):
    handler = node_operator(parser, node)
    if not handler.std:
        parse_error(parser, u"Unknown token std", node)

    return handler.std(parser, handler, node)


def node_has_nud(parser, node):
    handler = node_operator(parser, node)
    return handler.nud is not None


def node_has_led(parser, node):
    handler = node_operator(parser, node)
    return handler.led is not None


def node_has_std(parser, node):
    handler = node_operator(parser, node)
    return handler.std is not None


def node_lbp(parser, node):
    handler = node_operator(parser, node)
    lbp = handler.lbp
    if lbp == -1:
        parse_error(parser, u"Left binding power error", node)
    return lbp


def node_led(parser, node, left):
    handler = node_operator(parser, node)
    if not handler.led:
        parse_error(parser, u"Unknown token led", node)

    return handler.led(parser, handler, node, left)


def parser_set_nud(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.nud = fn
    return h


def parser_set_std(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.std = fn
    return h


def parser_set_led(parser, ttype, lbp, fn):
    h = get_or_create_operator(parser, ttype)
    h.lbp = lbp
    h.led = fn
    return h


def operator_infix(h, lbp, led, infix_fn):
    h.lbp = lbp
    h.led = led
    h.infix_function = infix_fn
    return h


def operator_prefix(h, nud, prefix_fn):
    h.nud = nud
    h.prefix_function = prefix_fn
    return h


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


def check_node_type(parser, node, expected_type):
    ntype = nodes.node_type(node)
    if ntype != expected_type:
        parse_error(parser, u"Wrong node type, expected  %s, got %s" %
                    (node_type.node_type_to_str(expected_type),
                     node_type.node_type_to_str(ntype)), node)


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


def advance_expected_after(parser, ttype):
    node = advance(parser)
    check_token_type(parser, ttype)
    return node


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    return advance(parser)


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


def closed_expression(parser, _rbp):
    res = expression(parser, _rbp)
    endofexpression(parser)
    return res

# SAME AS EXPRESSION BUT WITH TERMINATION CONDITION
# USED in parsing name declarations like specify a.b.c () -> end
# so () can be in same line as a.b.c
def terminated_expression(parser, _rbp, token_types):
    previous = parser.node
    advance(parser)

    left = nud(parser, previous)
    while True:
        if parser.token_type in token_types:
            break
        if parser.is_newline_occurred:
            break
        _lbp = node_lbp(parser, parser.node)
        if _rbp >= _lbp:
            break
        previous = parser.node
        advance(parser)
        left = node_led(parser, previous, left)

    return left


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
        _lbp = node_lbp(parser, parser.node)
        if _rbp >= _lbp:
            break
        previous = parser.node
        advance(parser)
        left = node_led(parser, previous, left)

    return left


def literal_expression(parser):
    # TODO WHY 70 here?!!!!
    return expression(parser, 70)


def literal_terminated_expression(parser):
    exp = literal_expression(parser)
    endofexpression(parser)
    return exp


def statement(parser):
    node = parser.node

    if node_has_std(parser, node):
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
    parser_set_led(parser, ttype, lbp, led)


def prefix(parser, ttype, nud):
    parser_set_nud(parser, ttype, nud)


def stmt(parser, ttype, std):
    parser_set_std(parser, ttype, std)


def literal(parser, ttype):
    from obin.compile.parse.callbacks import itself
    parser_set_nud(parser, ttype, itself)


def symbol(parser, ttype, nud):
    h = get_or_create_operator(parser, ttype)
    h.lbp = 0
    parser_set_nud(parser, ttype, nud)


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
