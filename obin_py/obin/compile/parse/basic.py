from obin.compile.parse.token_type import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes
from obin.compile.parse import tokens
from obin.types import space, api, root, plist, environment
from obin.runtime import error
from obin.misc.strutil import get_line, get_line_for_position

TERM_BLOCK = [TT_END]

TERM_IF_BODY = [TT_ELSE, TT_ELIF]
TERM_IF_CONDITION = [TT_ARROW]

TERM_FILE = [TT_ENDSTREAM]
TERM_CASE = [TT_CASE] + TERM_BLOCK
# TERM_CATCH = [TT_CATCH, TT_FINALLY] + TERM_BLOCK
TERM_TRY = [TT_CATCH, TT_FINALLY]
TERM_CATCH_CASE = [TT_CASE, TT_FINALLY] + TERM_BLOCK
TERM_SINGLE_CATCH = [TT_FINALLY] + TERM_BLOCK

TERM_PATTERN = [TT_WHEN]
TERM_FUN_GUARD = [TT_ARROW]
TERM_FUN_PATTERN = [TT_WHEN, TT_ARROW]

TERM_CONDITION_BODY = [TT_CASE] + TERM_BLOCK
TERM_BEFORE_FOR = [TT_FOR]

TERM_TYPE_ARGS = TERM_BLOCK
TERM_UNION_TYPE_ARGS = [TT_CASE] + TERM_BLOCK

TERM_METHOD_SIG = [TT_DEF, TT_ARROW] + TERM_BLOCK
TERM_METHOD_DEFAULT_BODY = [TT_DEF] + TERM_BLOCK
TERM_METHOD_CONSTRAINTS = [TT_DEF] + TERM_BLOCK
TERM_IMPL_BODY = [TT_CASE, TT_DEF] + TERM_BLOCK

TERM_IMPL_HEADER = [TT_DEF] + TERM_BLOCK

TERM_CONDITION_CONDITION = [TT_ARROW]

NODE_FOR_NAME = [NT_NAME]
NODE_FUNC_NAME = [NT_NAME]
NODE_DOT = [NT_NAME, NT_INT]
NODE_IMPLEMENT_NAME = [NT_NAME, NT_IMPORTED_NAME]

LOOP_CONTROL_TOKENS = [TT_END, TT_ELSE, TT_CASE]

SKIP_JUXTAPOSITION = [TT_JUXTAPOSITION]

def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newint(position),
                           space.newstring(u"Unknown Token"),
                           space.newstring(line)
                       ]))


def parse_error(parser, message, node):
    if nodes.node_token_type(node) == TT_ENDSTREAM:
        line = u"Unclosed top level statement"
    else:
        line = get_line(parser.ts.src, api.to_i(nodes.node_line(node)))

    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newtuple([nodes.node_position(node),
                                           nodes.node_line(node),
                                           nodes.node_column(node)]),
                           nodes.node_to_string(node),
                           space.newstring(message),
                           space.newstring(line)
                       ]))


class ParserScope(root.W_Root):
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
    op = api.lookup(cur_scope.operators, op_name, space.newvoid())
    if space.isvoid(op):
        return newoperator()
    return op


def parser_find_operator(parser, op_name):
    undef = space.newvoid()
    cur_scope = parser_current_scope(parser)
    scopes = parser.state.scopes
    for scope in scopes:
        op = api.lookup(scope.operators, op_name, undef)
        if not space.isvoid(op):
            return op

    op = environment.get_operator(parser.state.env, op_name)
    if not space.isvoid(op):
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
        # self.is_breaker = False

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
        return parse_error(parser, u"Invalid token %s" % tokens.token_type_to_str(ttype), parser.node)


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
    if op is None or space.isvoid(op):
        return parse_error(parser, u"Invalid operator", node)
    return op


# def is_breaker(parser, node):
#     handler = node_operator(parser, node)
#     return handler.is_breaker

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
    # if lbp < 0:
    #   parse_error(parser, u"Left binding power error", node)

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


def token_is_one_of(parser, types):
    return parser.token_type in types


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser, u"Wrong token type, expected %s, got %s" % (tokens.token_type_to_str(type),
                                                                        tokens.token_type_to_str(parser.token_type)),
                    parser.node)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, u"Wrong token type, expected one of %s, got %s" %
                    (unicode([tokens.token_type_to_str(type) for type in types]),
                     tokens.token_type_to_str(parser.token_type)), parser.node)


def check_list_node_types(parser, node, expected_types):
    for child in node:
        check_node_types(parser, child, expected_types)


def check_node_type(parser, node, expected_type):
    ntype = nodes.node_type(node)
    if ntype != expected_type:
        parse_error(parser, u"Wrong node type, expected  %s, got %s" %
                    (node_type_to_str(expected_type),
                     node_type_to_str(ntype)), node)


def check_node_types(parser, node, types):
    ntype = nodes.node_type(node)
    if ntype not in types:
        parse_error(parser, u"Wrong node type, expected one of %s, got %s" %
                    (unicode([node_type_to_str(type) for type in types]),
                     node_type_to_str(ntype)), node)


def advance(parser):
    if parser.isend():
        return None

    return parser.next()


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    return advance(parser)


def advance_expected_one_of(parser, ttypes):
    check_token_types(parser, ttypes)

    if parser.isend():
        return None

    return parser.next()


def advance_end(parser):
    advance_expected_one_of(parser, TERM_BLOCK)


def isendofexpressiontoken(parser):
    return parser.token_type == TT_SEMI


def endofexpression(parser):
    if parser.isend():
        return None
    if parser.is_newline_occurred:
        return parser.node
    if parser.token_type in TERM_BLOCK:
        return parser.node
    if parser.token_type == TT_SEMI:
        return advance(parser)

    parse_error(parser, u"Expected end of expression mark", parser.node)


def base_expression(parser, _rbp, terminators=None):
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

        if terminators is not None:
            if parser.token_type in terminators:
                return left, 0

        _lbp = node_lbp(parser, parser.node)

        # juxtaposition support
        if _lbp < 0:
            if parser.break_on_juxtaposition is True:
                return left, _lbp

            op = parser_operator(parser, TT_JUXTAPOSITION)
            _lbp = op.lbp
            # return left, _lbp

            if _rbp >= _lbp:
                break
            previous = parser.node
            # advance(parser)
            if not op.led:
                parse_error(parser, u"Unknown token led", previous)

            left = op.led(parser, op, previous, left)
        else:
            if _rbp >= _lbp:
                break
            previous = parser.node
            advance(parser)

            left = node_led(parser, previous, left)

    assert left is not None
    return left, 0


def expect_expression_of(parser, _rbp, expected_type, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_type(parser, exp, expected_type)
    return exp


def expect_expression_of_types(parser, _rbp, expected_types, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_types(parser, exp, expected_types)
    return exp


def expression(parser, _rbp, terminators=None):
    expr, _lbp = base_expression(parser, _rbp, terminators)
    expr = postprocess(parser, expr)
    return expr


def juxtaposition_list(parser, terminators, skip=None):
    args = []
    if parser.token_type in terminators:
        return None, args
    while True:
        if skip is not None:
            while parser.token_type in skip:
                advance(parser)

        node, _lbp = base_expression(parser, 0, terminators)
        args.append(node)

        if parser.token_type in terminators:
            return node, args


def flatten_juxtaposition(parser, node):
    ntype = nodes.node_type(node)
    if ntype == NT_JUXTAPOSITION:
        first = nodes.node_first(node)
        second = nodes.node_second(node)
        head = flatten_juxtaposition(parser, first)
        tail = flatten_juxtaposition(parser, second)
        return plist.concat(head, tail)
    else:
        return nodes.list_node([node])


def postprocess(parser, node):
    if nodes.is_empty_node(node):
        return node
    elif nodes.is_list_node(node):
        children = []
        for c in node:
            children.append(postprocess(parser, c))
        return nodes.list_node(children)

    ntype = nodes.node_type(node)
    if ntype == NT_JUXTAPOSITION:
        flatten = flatten_juxtaposition(parser, node)
        # probably overkill
        if len(flatten) < 2:
            parse_error(parser, u"Invalid use of juxtaposition operator", node)

        if parser.juxtaposition_as_list:
            return postprocess(parser, nodes.create_list_node_from_list(node, flatten))
        else:
            caller = plist.head(flatten)
            args = plist.tail(flatten)
            return postprocess(parser, nodes.node_2(NT_CALL, nodes.node_token(caller), caller, args))
    else:
        children = []
        node_children = nodes.node_children(node)
        if node_children is None:
            return node

        for c in node_children:
            new_child = postprocess(parser, c)
            children.append(new_child)
        return nodes.newnode(nodes.node_type(node), nodes.node_token(node), children)


def literal_expression(parser):
    # Override most operators in literals
    # because of prefix operators
    return expression(parser, 70)


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


def symbol(parser, ttype, nud=None):
    h = get_or_create_operator(parser, ttype)
    h.lbp = 0
    parser_set_nud(parser, ttype, nud)
    return h


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


def condition_expression(parser):
    node = expression(parser, 0)
    if is_assignment_node(node):
        parse_error(parser, u"Assignment operators not allowed in conditions", node)
    # call endofexpression to allow one line prefixes like if x == 1, x end
    endofexpression(parser)
    return node


def condition_terminated_expression(parser, terminators):
    node = expression(parser, 0, terminators)

    if is_assignment_node(node):
        parse_error(parser, u"Assignment operators not allowed in conditions", node)

    check_token_types(parser, terminators)
    advance(parser)
    return node
