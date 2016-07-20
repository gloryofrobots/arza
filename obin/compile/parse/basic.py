from obin.compile.parse.token_type import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes
from obin.compile.parse import tokens
from obin.types import space, api, root, plist, environment
from obin.runtime import error
from obin.misc.strutil import get_line, get_line_for_position

TERM_BLOCK = [TT_END]
TERM_EXP = [TT_END_EXPR]

TERM_IF_BODY = [TT_ELSE, TT_ELIF]
TERM_IF_CONDITION = [TT_THEN]

TERM_FILE = [TT_ENDSTREAM]

TERM_MATCH_EXPR = [TT_WITH]
TERM_MATCH_PATTERN = [TT_WITH]
TERM_CASE = [TT_CASE] + TERM_BLOCK
# TERM_CATCH = [TT_CATCH, TT_FINALLY] + TERM_BLOCK
TERM_TRY = [TT_CATCH, TT_FINALLY]
TERM_CATCH_CASE = [TT_CASE, TT_FINALLY] + TERM_BLOCK
TERM_SINGLE_CATCH = [TT_FINALLY] + TERM_BLOCK

TERM_LET = [TT_IN]

TERM_PATTERN = [TT_WHEN]
TERM_FUN_GUARD = [TT_ARROW]
TERM_FUN_PATTERN = [TT_WHEN, TT_ARROW]
TERM_FUN_SIGNATURE = [TT_ARROW, TT_CASE]

TERM_CONDITION_BODY = [TT_CASE] + TERM_BLOCK

TERM_BEFORE_WITH = [TT_WITH]

TERM_TYPE_ARGS = TERM_BLOCK
TERM_UNION_TYPE_ARGS = [TT_CASE] + TERM_BLOCK

TERM_METHOD_SIG = [TT_DEF, TT_ARROW] + TERM_BLOCK
TERM_METHOD_DEFAULT_BODY = [TT_DEF] + TERM_BLOCK
TERM_METHOD_CONSTRAINTS = [TT_DEF] + TERM_BLOCK
TERM_IMPL_BODY = [TT_CASE, TT_DEF] + TERM_BLOCK
TERM_IMPL_HEADER = [TT_DEF] + TERM_BLOCK

TERM_TRAIT_DEF = [TT_DEF, TT_CASE] + TERM_BLOCK

TERM_EXTEND_DEF = [TT_CASE, TT_DEF, TT_USE] + TERM_BLOCK
TERM_EXTEND = [TT_DEF, TT_USE] + TERM_BLOCK

TERM_FROM_IMPORTED = [TT_IMPORT, TT_HIDE]

TERM_CONDITION_CONDITION = [TT_ARROW]

NODE_FOR_NAME = [NT_NAME]
NODE_FUNC_NAME = [NT_NAME]
NODE_DOT = [NT_NAME, NT_INT]
NODE_IMPLEMENT_NAME = [NT_NAME, NT_IMPORTED_NAME]

LOOP_CONTROL_TOKENS = [TT_END, TT_ELSE, TT_CASE]

LEVELS_MATCH = TERM_MATCH_EXPR
LEVELS_IF = [TT_ELSE, TT_ELIF]
LEVELS_TRY = [TT_CATCH, TT_FINALLY]
LEVELS_LET = [TT_IN]

SKIP_JUXTAPOSITION = [TT_JUXTAPOSITION]


def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newint(position),
                           space.newstring(u"Unknown Token"),
                           space.newstring(line)
                       ]))


def parser_error_indentation(parser, msg, position, lineno, column):
    print parser.ts.advanced_values()
    print parser.ts.layouts
    line = get_line_for_position(parser.ts.src, position)
    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newint(position),
                           space.newint(lineno),
                           space.newint(column),
                           space.newstring(msg),
                           space.newstring(line)
                       ]))


def parse_error(parser, message, node):
    print parser.ts.advanced_values()
    print parser.ts.layouts
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


def init_code_layout(parser, node, terminators=None):
    skip_indent(parser)
    parser.ts.add_code_layout(node, terminators)


def init_offside_layout(parser, node):
    parser.ts.add_offside_layout(node)


def init_node_layout(parser, node, level_tokens=None):
    parser.ts.add_node_layout(node, level_tokens)


def init_free_layout(parser, node, terminators):
    skip_indent(parser)
    parser.ts.add_free_code_layout(node, terminators)


def skip_indent(parser):
    if parser.token_type == TT_INDENT:
        advance(parser)


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


def parse_module(parser, termination_tokens):
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
        self.layout = None

        self.ambidextra = False
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
    assert ttype <= TT_UNKNOWN
    try:
        return parser.handlers[ttype]
    except:
        if ttype == TT_UNKNOWN:
            return parse_error(parser, u"Invalid token", parser.node)

        if parser.allow_unknown is True:
            return parser_operator(parser, TT_UNKNOWN)
        return parse_error(parser, u"Invalid token %s" % tokens.token_type_to_s(ttype), parser.node)


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

def node_nud(parser, node):
    handler = node_operator(parser, node)
    if not handler.nud:
        parse_error(parser, u"Unknown token nud", node)
    return handler.nud(parser, handler, node)


def node_std(parser, node):
    handler = node_operator(parser, node)
    if not handler.std:
        parse_error(parser, u"Unknown token std", node)

    # print tokens.token_type_to_s(nodes.node_token_type(node))
    return handler.std(parser, handler, node)


def node_has_nud(parser, node):
    handler = node_operator(parser, node)
    return handler.nud is not None


def node_has_layout(parser, node):
    handler = node_operator(parser, node)
    return handler.layout is not None


def node_has_led(parser, node):
    handler = node_operator(parser, node)
    return handler.led is not None


def node_has_std(parser, node):
    handler = node_operator(parser, node)
    return handler.std is not None


def node_lbp(parser, previous, node):
    op = node_operator(parser, node)
    lbp = op.lbp
    if op.ambidextra is True:
        # print "Ambidextra"
        prev_pos = nodes.node_position_i(previous)
        cur_pos = nodes.node_position_i(node)
        # 2- - 1
        next_tok = parser.ts.lookup_next_token()
        if nodes.node_token_type(node) == tokens.token_type(next_tok):
        # if tokens.is_infix_token_type(nodes.node_token_type(previous)):
            # print '!!!!!1'
            return lbp

        prev_length = nodes.node_length(previous)
        # 2-1 -> infix
        if cur_pos - (prev_pos + prev_length) == 0:
            # print '!!!!!2'
            return lbp

        # pow -1 -> infix
        next_pos = tokens.token_position_i(next_tok)
        cur_length = nodes.node_length(node)

        if next_pos - (cur_pos + cur_length) == 0:
            # print '!!!!!3'
            return -1

        # Anything else go to infix

    # if lbp < 0:
    #   parse_error(parser, u"Left binding power error", node)

    return lbp


def node_led(parser, node, left):
    handler = node_operator(parser, node)
    if not handler.led:
        parse_error(parser, u"Unknown token led", node)

    return handler.led(parser, handler, node, left)


def node_layout(parser, node):
    handler = node_operator(parser, node)
    if not handler.layout:
        parse_error(parser, u"Unknown token layout", node)

    return handler.layout(parser, handler, node)


def parser_set_layout(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.layout = fn
    return h


def __check_ambidextrity(op):
    if op.led and op.nud:
        op.ambidextra = True


def parser_set_nud(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.nud = fn
    __check_ambidextrity(h)

    return h


def parser_set_std(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.std = fn
    return h


def parser_set_led(parser, ttype, lbp, fn):
    h = get_or_create_operator(parser, ttype)
    h.lbp = lbp
    h.led = fn
    __check_ambidextrity(h)
    return h


def operator_infix(h, lbp, led, infix_fn):
    h.lbp = lbp
    h.led = led
    h.infix_function = infix_fn
    __check_ambidextrity(h)
    return h


def operator_prefix(h, nud, prefix_fn):
    h.nud = nud
    h.prefix_function = prefix_fn
    __check_ambidextrity(h)
    return h


def token_is_one_of(parser, types):
    return parser.token_type in types


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser, u"Wrong token type, expected %s, got %s" % (tokens.token_type_to_s(type),
                                                                        tokens.token_type_to_s(parser.token_type)),
                    parser.node)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, u"Wrong token type, expected one of %s, got %s" %
                    (unicode([tokens.token_type_to_s(type) for type in types]),
                     tokens.token_type_to_s(parser.token_type)), parser.node)


def check_list_node_types(parser, node, expected_types):
    for child in node:
        check_node_types(parser, child, expected_types)


def check_node_type(parser, node, expected_type):
    ntype = nodes.node_type(node)
    if ntype != expected_type:
        parse_error(parser, u"Wrong node type, expected  %s, got %s" %
                    (node_type_to_s(expected_type),
                     node_type_to_s(ntype)), node)


def check_node_types(parser, node, types):
    ntype = nodes.node_type(node)
    if ntype not in types:
        parse_error(parser, u"Wrong node type, expected one of %s, got %s" %
                    (unicode([node_type_to_s(type) for type in types]),
                     node_type_to_s(ntype)), node)


def advance(parser):
    if parser.isend():
        return None

    node = parser.next_token()
    # print "ADVANCE", node
    return node


def advance_expected(parser, ttype):
    check_token_type(parser, ttype)

    return advance(parser)


def advance_expected_one_of(parser, ttypes):
    check_token_types(parser, ttypes)

    if parser.isend():
        return None

    return parser.next_token()


def advance_end(parser):
    advance_expected_one_of(parser, TERM_BLOCK)


def on_endofexpression(parser):
    if parser.isend():
        return None
    if parser.token_type in TERM_BLOCK:
        return parser.node
    if parser.token_type == TT_END_EXPR:
        return advance(parser)
    return False


def endofexpression(parser):
    res = on_endofexpression(parser)
    if res is False:
        parse_error(parser, u"Expected end of expression mark got '%s'" % tokens.token_value_s(parser.token),
                    parser.node)

    return res


def base_expression(parser, _rbp, terminators=None):
    previous = parser.node
    if node_has_layout(parser, previous):
        node_layout(parser, previous)

    advance(parser)

    left = node_nud(parser, previous)
    while True:
        # if parser.is_newline_occurred:
        #     break

        if terminators is not None:
            if parser.token_type in terminators:
                return left

        _lbp = node_lbp(parser, previous, parser.node)

        # juxtaposition support
        if _lbp < 0:
            if parser.break_on_juxtaposition is True:
                return left

            op = parser_operator(parser, TT_JUXTAPOSITION)
            _lbp = op.lbp

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
    return left


def expect_expression_of(parser, _rbp, expected_type, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_type(parser, exp, expected_type)
    return exp


def expect_expression_of_types(parser, _rbp, expected_types, terminators=None):
    exp = expression(parser, _rbp, terminators=terminators)
    check_node_types(parser, exp, expected_types)
    return exp


def skip_end_expression(parser):
    if parser.token_type == TT_END_EXPR:
        advance(parser)


def expression(parser, _rbp, terminators=None):
    if terminators is None:
        terminators = TERM_EXP
    expr = base_expression(parser, _rbp, terminators)
    expr = postprocess(parser, expr)
    return expr


# INFIXR
def rexpression(parser, op):
    return expression(parser, op.lbp - 1)


def expression_with_optional_end_of_expression(parser, _rbp, terminators):
    exp = expression(parser, _rbp, terminators)
    skip_end_expression(parser)
    return exp


def juxtaposition_as_list(parser, terminators):
    node = parser.node
    exp = expression(parser, 0, terminators)
    if not nodes.is_list_node(exp):
        return nodes.create_list_node(node, [exp])

    return nodes.create_list_node_from_list(node, exp)


def juxtaposition_as_tuple(parser, terminators):
    node = parser.node
    exp = expression(parser, 0, terminators)
    if not nodes.is_list_node(exp):
        return nodes.create_tuple_node(node, [exp])

    return nodes.create_tuple_node_from_list(node, exp)


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
            return postprocess(parser, flatten)
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
    return expression(parser, 97)


def statement(parser):
    node = parser.node
    if node_has_std(parser, node):
        advance(parser)
        value = node_std(parser, node)
        return value

    value = expression(parser, 0)
    return value


def statement_no_end_expr(parser):
    node = parser.node
    if node_has_std(parser, node):
        advance(parser)
        value = node_std(parser, node)
        return value

    value = expression(parser, 0)
    return value


def statements(parser, endlist):
    stmts = []
    while True:
        if token_is_one_of(parser, endlist):
            break
        s = statement(parser)
        end_exp = on_endofexpression(parser)
        if s is None:
            continue
        stmts.append(s)
        if end_exp is False:
            break

    length = len(stmts)
    if length == 0:
        return parse_error(parser, u"Expected one or more expressions", parser.node)

    return nodes.list_node(stmts)


# def statements(parser, endlist):
#     return _statements(parser, statement, endlist)
#
#
# def module_statements(parser, endlist):
#     return _statements(parser, statement_no_end_expr, endlist)


def infix(parser, ttype, lbp, led):
    parser_set_led(parser, ttype, lbp, led)


def prefix(parser, ttype, nud, layout=None):
    parser_set_nud(parser, ttype, nud)
    parser_set_layout(parser, ttype, layout)


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


def empty(parser, op, node):
    print "EMPTY"
    return expression(parser, 0)
    # return None


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


def check_if_assignment(parser, node):
    if is_assignment_node(node):
        parse_error(parser, u"Assignment operators not allowed in conditions", node)