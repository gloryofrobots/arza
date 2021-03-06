from arza.compile.parse.token_type import *
from arza.compile.parse.indenter import (open_free_layout, open_code_layout,
                                         open_statement_layout, open_offside_layout)
from arza.compile.parse.node_type import *
from arza.compile.parse import nodes
from arza.compile.parse import tokens
from arza.types import space, api, root, plist, environment
from arza.runtime import error
from arza.misc.strutil import get_line, get_line_for_position

TERM_LPAREN = [TT_RPAREN]
TERM_COMMA = [TT_COMMA]

TERM_IF_BODY = [TT_ELSE, TT_ELIF]
TERM_IF_CONDITION = [TT_THEN]
TERM_WHEN_EXPRESSION = [TT_ELSE]

TERM_FILE = [TT_ENDSTREAM]

TERM_CASE = [TT_CASE]
TERM_TRY = [TT_CATCH, TT_FINALLY]
TERM_CATCH_CASE = [TT_CASE, TT_FINALLY]
TERM_SINGLE_CATCH = [TT_FINALLY]

TERM_LET = [TT_IN]

TERM_PATTERN = [TT_WHEN]
TERM_BLOCK = [TT_DEDENT]

TERM_CASE_FUN_BLOCK = TERM_BLOCK + [TT_CASE]
TERM_FUN_GUARD = [TT_ASSIGN]
TERM_FUN_PATTERN = [TT_WHEN, TT_ASSIGN]
TERM_FUN_SIGNATURE = [TT_ASSIGN, TT_CASE]

TERM_TRAIT_SIGNATURE = [TT_ASSIGN]
TERM_TRAIT_GUARD = [TT_ASSIGN]

TERM_FROM_IMPORTED = [TT_IMPORT, TT_HIDE]
TERM_DEF_SIGNATURE = [TT_CASE, TT_ASSIGN, TT_AS]

NAME_NODES = [NT_NAME, NT_IMPORTED_NAME]
IMPORT_NODES = [NT_IMPORT, NT_INCLUDE, NT_INCLUDE_HIDING, NT_IMPORT_HIDING]
LET_NODES = [NT_DECORATOR, NT_TRY, NT_FUN, NT_ASSIGN]
EXPORT_NODES = [NT_NAME, NT_TUPLE]
DEF_ARGS_NODES = [NT_NAME, NT_WILDCARD]

LAYOUT_LPAREN = [TT_RPAREN]
LAYOUT_LCURLY = [TT_RCURLY]
LAYOUT_LSQUARE = [TT_RSQUARE]

LEVELS_IF = [TT_ELSE, TT_ELIF]
LEVELS_FUN = [TT_CASE]
LEVELS_INIT = [TT_CASE]
LEVELS_TRY = [TT_CATCH, TT_FINALLY]
LEVELS_LET = [TT_IN]
LEVELS_USE = LEVELS_LET
LEVELS_TRAIT = None
LEVELS_TYPE = None
LEVELS_INTERFACE = None
LEVELS_MATCH = [TT_CASE]
LEVELS_RECEIVE = [TT_CASE]

LEVELS_DECORATOR = []

INDENTS_CODE = [TT_DOUBLE_COLON, TT_COLON,
                TT_OPERATOR, TT_DOT, TT_OR, TT_AND,
                TT_ARROW,
                TT_ASSIGN,
                TT_LPAREN,
                TT_LCURLY,
                TT_LSQUARE,
                TT_INFIX_DOT_LCURLY,
                TT_INFIX_DOT_LSQUARE
                ]

INDENTS_IF = [TT_IF, TT_THEN, TT_ELSE] + INDENTS_CODE
INDENTS_LET = [TT_LET, TT_IN] + INDENTS_CODE
INDENTS_TRY = [TT_TRY, TT_FINALLY, TT_CATCH, TT_ASSIGN] + INDENTS_CODE
INDENTS_MATCH = [TT_MATCH, TT_CASE, TT_ASSIGN] + INDENTS_CODE
INDENTS_RECEIVE = [TT_RECEIVE, TT_CASE, TT_ASSIGN] + INDENTS_CODE
INDENTS_USE = [TT_USE, TT_IN]
INDENTS_FUN = [TT_FUN, TT_WHEN, TT_CASE, TT_ASSIGN] + INDENTS_CODE
INDENTS_INIT = [TT_INIT, TT_WHEN, TT_CASE, TT_ASSIGN] + INDENTS_CODE
INDENTS_DEF = [TT_DEF, TT_ASSIGN, TT_WHEN, TT_CASE] + INDENTS_CODE
INDENTS_INTERFACE = [TT_INTERFACE, TT_ASSIGN, TT_IS]
INDENTS_DESCRIBE = [TT_DESCRIBE]
INDENTS_TYPE = [TT_TYPE, TT_LPAREN, TT_INIT]
INDENTS_TRAIT = [TT_TRAIT, TT_FOR, TT_ASSIGN]
INDENTS_DECORATOR = [TT_FUN, TT_DEF, TT_OVERRIDE] + INDENTS_CODE


# if you want to remove ASSIGN
# INDENTS_TRAIT = [TT_TRAIT, TT_NAME, TT_DEF, TT_USE]

def parser_error_unknown(parser, position):
    line = get_line_for_position(parser.ts.src, position)
    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newstring(line),
                           space.newint(position),
                           space.newstring(u"Unknown Token"),
                       ]))


def parse_error(parser, message, token):
    if tokens.token_type(token) == TT_ENDSTREAM:
        line = u"Unclosed top level statement"
    else:
        line = get_line(parser.ts.src, api.to_i(tokens.token_line(token)))

    return error.throw(error.Errors.PARSE_ERROR,
                       space.newtuple([
                           space.newtuple([
                               tokens.token_line(token),
                               tokens.token_column(token),
                               tokens.token_position(token)]),
                           # tokens.token_to_string(token),
                           space.newstring(message),
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


def skip_indent(parser):
    if parser.token_type == TT_INDENT:
        advance(parser)


class ParserScope(root.W_Root):
    def __init__(self):
        self.operators = space.newassocarray()
        self.macro = space.newassocarray()


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


def parse_module(parser):
    parser_enter_scope(parser)
    stmts = module_statements(parser)
    scope = parser_exit_scope(parser)
    return stmts, scope


class W_Operator(root.W_Hashable):
    def __init__(self):
        root.W_Hashable.__init__(self)
        self.nud = None
        self.led = None
        self.std = None
        self.lbp = -1
        self.layout = None
        self.infix_layout = None

        self.ambidextra = False
        self.prefix_function = None
        self.infix_function = None
        self.prefix_node_type = None
        self.infix_node_type = None

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

        if self.prefix_node_type != other.prefix_node_type:
            return False

        if self.infix_node_type != other.infix_node_type:
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
            return parse_error(parser, u"Invalid token", parser.token)

        if parser.allow_unknown is True:
            return parser_operator(parser, TT_UNKNOWN)
        return parse_error(parser, u"Invalid token %s" % tokens.token_type_to_s(ttype), parser.token)


def get_or_create_operator(parser, ttype):
    if not parser_has_operator(parser, ttype):
        return parser_set_operator(parser, ttype, newoperator())
    return parser_operator(parser, ttype)


def parser_set_operator(parser, ttype, h):
    parser.handlers[ttype] = h
    return parser_operator(parser, ttype)


def node_operator(parser, token):
    ttype = tokens.token_type(token)
    if not parser.allow_overloading:
        return parser_operator(parser, ttype)

    if ttype != TT_OPERATOR:
        return parser_operator(parser, ttype)

    # in case of operator
    op = parser_find_operator(parser, tokens.token_value(token))
    if op is None or space.isvoid(op):
        return parse_error(parser, u"Invalid operator", token)
    return op


def node_nud(parser, token):
    handler = node_operator(parser, token)
    if not handler.nud:
        parse_error(parser, u"Unknown token nud", token)
    return handler.nud(parser, handler, token)


def node_std(parser, token):
    handler = node_operator(parser, token)
    if not handler.std:
        parse_error(parser, u"Unknown token std", token)

    # print tokens.token_type_to_s(nodes.node_token_type(node))
    return handler.std(parser, handler, token)


def node_has_nud(parser, token):
    handler = node_operator(parser, token)
    return handler.nud is not None


def node_has_led(parser, token):
    handler = node_operator(parser, token)
    return handler.led is not None


def node_has_std(parser, token):
    handler = node_operator(parser, token)
    return handler.std is not None


def node_has_layout(parser, token):
    handler = node_operator(parser, token)
    return handler.layout is not None


def node_has_infix_layout(parser, token):
    handler = node_operator(parser, token)
    return handler.infix_layout is not None


def node_lbp(parser, token):
    op = node_operator(parser, token)
    lbp = op.lbp
    if op.ambidextra is True:
        prev = parser.previous_token
        if not prev:
            return lbp

        prev_line = tokens.token_line_i(prev)
        cur_line = tokens.token_line_i(token)
        # if tokens on the same line it's infix otherwise it's prefix
        if prev_line == cur_line:
            return lbp
        else:
            return -1

    return lbp


def node_led(parser, token, left):
    handler = node_operator(parser, token)
    if not handler.led:
        parse_error(parser, u"Unknown token led", token)

    return handler.led(parser, handler, token, left)


def node_layout(parser, node):
    handler = node_operator(parser, node)
    if not handler.layout:
        parse_error(parser, u"Unknown token layout", node)

    return handler.layout(parser, handler, node)


def node_infix_layout(parser, node):
    handler = node_operator(parser, node)
    if not handler.infix_layout:
        parse_error(parser, u"Unknown token infix layout", node)

    return handler.infix_layout(parser, handler, node)


def parser_set_layout(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.layout = fn
    return h


def parser_set_infix_layout(parser, ttype, fn):
    h = get_or_create_operator(parser, ttype)
    h.infix_layout = fn
    return h


def node_prefix_node_type(parser, token):
    handler = node_operator(parser, token)
    if not handler.prefix_node_type:
        parse_error(parser, u"Unknown token prefix node type ", token)

    return handler.prefix_node_type


def node_infix_node_type(parser, token):
    handler = node_operator(parser, token)
    if not handler.infix_node_type:
        parse_error(parser, u"Unknown token infix node type ", token)

    return handler.infix_node_type


def __check_ambidextrity(op):
    if op.led and op.nud:
        op.ambidextra = True


def parser_set_nud(parser, ttype, ntype, fn, pbp=0):
    h = get_or_create_operator(parser, ttype)
    h.nud = fn
    h.pbp = pbp
    h.prefix_node_type = ntype
    __check_ambidextrity(h)

    return h


def parser_set_std(parser, ttype, ntype, fn):
    h = get_or_create_operator(parser, ttype)
    h.std = fn
    h.prefix_node_type = ntype
    return h


def parser_set_led(parser, ttype, ntype, lbp, fn):
    h = get_or_create_operator(parser, ttype)
    h.lbp = lbp
    h.led = fn
    h.infix_node_type = ntype
    __check_ambidextrity(h)
    return h


def operator_infix(h, lbp, led, infix_fn):
    h.lbp = lbp
    h.led = led
    h.infix_function = infix_fn
    h.infix_node_type = None
    __check_ambidextrity(h)
    return h


def operator_prefix(h, pbp, nud, prefix_fn):
    h.nud = nud
    h.pbp = pbp
    h.prefix_function = prefix_fn
    h.prefix_node_type = None
    __check_ambidextrity(h)
    return h


def token_is_one_of(parser, types):
    return parser.token_type in types


def check_token_type(parser, type):
    if parser.token_type != type:
        parse_error(parser, u"Wrong token type, expected %s, got %s" % (tokens.token_type_to_s(type),
                                                                        tokens.token_type_to_s(parser.token_type)),
                    parser.token)


def check_token_types(parser, types):
    if parser.token_type not in types:
        parse_error(parser, u"Wrong token type, expected one of %s, got %s" %
                    (unicode([tokens.token_type_to_s(type) for type in types]),
                     tokens.token_type_to_s(parser.token_type)), parser.token)


def check_list_node_type(parser, node, expected_type):
    for child in node:
        check_node_type(parser, child, expected_type)


def check_list_node_types(parser, node, expected_types):
    for child in node:
        check_node_types(parser, child, expected_types)


def check_node_type(parser, node, expected_type):
    ntype = nodes.node_type(node)
    if ntype != expected_type:
        parse_error(parser, u"Wrong node type, expected  %s, got %s" %
                    (node_type_to_s(expected_type),
                     node_type_to_s(ntype)), nodes.node_token(node))


def check_node_types(parser, node, types):
    ntype = nodes.node_type(node)
    if ntype not in types:
        parse_error(parser, u"Wrong node type, expected one of %s, got %s" %
                    (unicode([node_type_to_s(type) for type in types]),
                     node_type_to_s(ntype)), nodes.node_token(node))


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


def advance_dedent(parser):
    if parser.ts.current_layout().is_free():
        return
    advance_expected(parser, TT_DEDENT)


def on_endofexpression(parser):
    if parser.isend():
        return

    if parser.token_type == TT_END_EXPR:
        advance(parser)


def endofexpression(parser):
    res = on_endofexpression(parser)
    if res is False:
        parse_error(parser, u"Expected end of expression mark got '%s'" % tokens.token_value_s(parser.token),
                    parser.token)

    return res


def base_expression(parser, _rbp, terminators=None):
    previous = parser.token
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

        _lbp = node_lbp(parser, parser.token)

        # juxtaposition support
        if _lbp < 0:
            if parser.break_on_juxtaposition is True:
                return left

            op = parser_operator(parser, TT_JUXTAPOSITION)
            _lbp = op.lbp

            if _rbp >= _lbp:
                break
            previous = parser.token

            # advance(parser)

            if not op.led:
                parse_error(parser, u"Unknown token led", previous)

            if node_has_infix_layout(parser, previous):
                node_infix_layout(parser, previous)

            left = op.led(parser, op, previous, left)
        else:
            if _rbp >= _lbp:
                break

            previous = parser.token

            if node_has_infix_layout(parser, previous):
                node_infix_layout(parser, previous)

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
        terminators = []
    expr = base_expression(parser, _rbp, terminators)
    # expr = postprocess(parser, expr)
    return expr


def free_expression(parser, _rbp, terminators):
    open_free_layout(parser, parser.token, terminators)
    expr = base_expression(parser, _rbp, terminators)
    # expr = postprocess(parser, expr)
    return expr


# INFIXR
def rexpression(parser, op):
    return expression(parser, op.lbp - 1)


def flatten_infix(node, ntype):
    if nodes.node_type(node) == ntype:
        first = nodes.node_first(node)
        second = nodes.node_second(node)
        head = flatten_infix(first, ntype)
        tail = flatten_infix(second, ntype)
        return plist.concat(head, tail)
    else:
        return nodes.list_node([node])


def commas_as_list(parser, node):
    return flatten_infix(node, NT_COMMA)


def maybe_tuple(parser, node):
    if node.node_type == NT_COMMA:
        els = commas_as_list(parser, node)
        return nodes.node_1(NT_TUPLE, nodes.node_token(node), els)
    return node


def commas_as_list_if_commas(parser, node):
    if nodes.node_type(node) != NT_COMMA:
        return node

    return flatten_infix(node, NT_COMMA)


def postprocess(parser, node):
    if nodes.is_empty_node(node):
        return node
    elif nodes.is_list_node(node):
        children = []
        for c in node:
            children.append(postprocess(parser, c))
        return nodes.list_node(children)

    ntype = nodes.node_type(node)
    if ntype == NT_COMMA:
        items = commas_as_list(parser, node)
        flatten = nodes.node_1(NT_TUPLE, nodes.node_token(node), items)
        return postprocess(parser, flatten)
    else:
        children = []
        node_children = nodes.node_children(node)
        if node_children is None:
            return node

        for c in node_children:
            new_child = postprocess(parser, c)
            children.append(new_child)
        return nodes.newnode(nodes.node_type(node), nodes.node_token(node), children)


def transform(node, cb, args):
    return _transform(node, cb, 0, args)


def _transform(node, cb, level, args):
    if nodes.is_empty_node(node):
        return node
    elif nodes.is_list_node(node):
        children = []
        for c in node:
            children.append(_transform(c, cb, level + 1, args))
        return nodes.list_node(children)

    new_node = cb(node, level, args)
    if new_node is not None:
        return new_node
    else:
        children = []
        node_children = nodes.node_children(node)
        if node_children is None:
            return node

        for c in node_children:
            new_child = _transform(c, cb, level + 1, args)
            children.append(new_child)
        return nodes.newnode(nodes.node_type(node), nodes.node_token(node), children)


def literal_expression(parser):
    # Override most operators in literals
    # because of prefix operators
    return expression(parser, 70)


def statement(parser):
    token = parser.token
    if node_has_std(parser, token):
        if node_has_layout(parser, token):
            node_layout(parser, token)
        advance(parser)
        value = node_std(parser, token)
        return value

    value = expression(parser, 0)
    return value


def statement_no_end_expr(parser):
    token = parser.token
    if node_has_std(parser, token):
        advance(parser)
        value = node_std(parser, token)
        return value

    value = expression(parser, 0)
    return value


def module_statements(parser):
    stmts = []
    while True:
        # if parser.token_type == TT_DEDENT:
        #     advance(parser)
        if parser.token_type == TT_ENDSTREAM:
            break
        s = statement(parser)
        on_endofexpression(parser)
        if s is None:
            continue
        stmts.append(s)

    length = len(stmts)
    if length == 0:
        return parse_error(parser, u"Expected one or more expressions", parser.token)

    return nodes.list_node(stmts)


def statements(parser, endlist, expected_types=None):
    layout = parser.ts.current_layout()

    if layout.is_free():
        terminators = [] + endlist + layout.terminators
        if layout.delimiter is not None:
            terminators.append(layout.delimiter)
    else:
        terminators = [] + endlist

    layout = open_code_layout(parser, parser.token, None, terminators, INDENTS_CODE)
    stmts = _statements(parser, terminators, expected_types, layout)
    return stmts


def _statements(parser, terminators, expected_types, layout):
    stmts = []
    while True:
        # if status is True and parser.token_type == TT_DEDENT:
        #     break
        if token_is_one_of(parser, terminators):
            break

        if not layout.is_open():
            break

        s = statement(parser)
        if expected_types is not None:
            check_node_types(parser, s, expected_types)

        on_endofexpression(parser)
        if s is None:
            continue
        stmts.append(s)

    length = len(stmts)
    if length == 0:
        return parse_error(parser, u"Expected one or more expressions", parser.token)

    return nodes.list_node(stmts)


def infix(parser, ttype, infix_node_type, lbp, led, layout=None):
    parser_set_infix_layout(parser, ttype, layout)
    parser_set_led(parser, ttype, infix_node_type, lbp, led)


def prefix(parser, ttype, ntype, nud, pbp=0, layout=None):
    parser_set_layout(parser, ttype, layout)
    parser_set_nud(parser, ttype, ntype, nud, pbp)


def stmt(parser, ttype, ntype, std, layout=None):
    parser_set_layout(parser, ttype, layout)
    parser_set_std(parser, ttype, ntype, std)


def literal(parser, ttype, ntype):
    from arza.compile.parse.callbacks import itself
    parser_set_nud(parser, ttype, ntype, itself)


def symbol(parser, ttype):
    return symbol_nud(parser, ttype, None, None)


def symbol_nud(parser, ttype, ntype, nud):
    h = get_or_create_operator(parser, ttype)
    h.lbp = 0
    parser_set_nud(parser, ttype, ntype, nud)
    return h


def skip(parser, ttype):
    while parser.token_type == ttype:
        advance(parser)


def empty(parser, op, node):
    return expression(parser, 0)


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
