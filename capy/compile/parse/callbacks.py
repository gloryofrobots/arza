from capy.compile.parse.basic import *
from capy.compile.parse.node_type import *
from capy.compile.parse import nodes
from capy.compile.parse.nodes import (node_token as get_node_token, node_0, node_1, node_2, node_3, node_4,
                                      list_node, empty_node)
from capy.types import space
from capy.misc import strutil
from capy.builtins import lang_names


def _init_default_current_0(parser):
    ntype = node_prefix_node_type(parser, parser.token)
    return nodes.node_0(ntype, parser.token)


##############################################################
# INFIX
##############################################################

#
def led_infix(parser, op, token, left):
    exp = expression(parser, op.lbp)
    ntype = node_infix_node_type(parser, token)
    return node_2(ntype, token, left, exp)


def led_infixr(parser, op, token, left):
    exp = expression(parser, op.lbp - 1)
    ntype = node_infix_node_type(parser, token)
    return node_2(ntype, token, left, exp)


def prefix_nud_function(parser, op, token):
    exp = expression(parser, op.pbp)
    sym = nodes.create_symbol_node_s(token, op.prefix_function)
    lookup = nodes.create_lookup_index_node(token, exp, sym)
    return nodes.create_call_node_0(token, lookup)


def led_infix_function(parser, op, token, left):
    exp = expression(parser, op.lbp)
    sym = nodes.create_symbol_node_s(token, api.to_s(op.infix_function))
    lookup = nodes.create_lookup_node(token, left, sym)
    return nodes.create_call_node_1(token, lookup, exp)


def led_infixr_function(parser, op, token, left):
    exp = expression(parser, op.lbp - 1)
    sym = nodes.create_symbol_node_s(token, op.infix_function)
    lookup = nodes.create_lookup_index_node(token, left, sym)
    return nodes.create_call_node_1(token, lookup, exp)


def led_assign(parser, op, token, left):
    # status = open_code_layout(parser, parser.token, None, None)
    exp = expression(parser, 9)
    # close_layout(parser, status)
    return node_2(NT_ASSIGN, token, left, exp)


def layout_try(parser, op, node):
    open_statement_layout(parser, node, LEVELS_TRY, INDENTS_TRY)

def layout_if(parser, op, node):
    open_statement_layout(parser, node, LEVELS_IF, INDENTS_IF)


def layout_fun(parser, op, node):
    open_statement_layout(parser, node, None, INDENTS_FUN)


def layout_decorator(parser, op, node):
    open_statement_layout(parser, node, LEVELS_DECORATOR, INDENTS_DECORATOR)


def layout_lparen(parser, op, node):
    open_free_layout(parser, node, [TT_RPAREN], delimiter=TT_COMMA)


def layout_lcurly(parser, op, node):
    open_free_layout(parser, node, [TT_RCURLY], delimiter=TT_COMMA)


def layout_lsquare(parser, op, node):
    open_free_layout(parser, node, [TT_RSQUARE], delimiter=TT_COMMA)


def infix_when(parser, op, token, left):
    branches = []
    condition = expression(parser, 0, TERM_WHEN_EXPRESSION)
    branches.append(list_node([condition, list_node([left])]))
    advance_expected(parser, TT_ELSE)
    false_exp = expression(parser, 0)
    branches.append(list_node([empty_node(), list_node([false_exp])]))
    return node_1(NT_CONDITION, token, list_node(branches))


def infix_arrow(parser, op, token, left):
    args = ensure_tuple(left)
    exp = expression(parser, 0)
    return nodes.create_lambda_node(token, args, exp)


def infix_comma(parser, op, token, left):
    # it would be very easy, if not needed for trailing commas, aka postfix
    # operators
    tt = parser.token_type
    # check for end expr because it will be auto inserted and it has nud which
    # produces empty node
    if not node_has_nud(parser, parser.token) \
            or tt == TT_END_EXPR:
        # check some corner cases with 1,2,.name or 1,2,,
        if tt == TT_DOT or tt == TT_COMMA:
            parse_error(parser, "Invalid tuple syntax", token)

        return left
    right = expression(parser, op.lbp)
    return node_2(NT_COMMA, token, left, right)


def infix_dot(parser, op, token, left):
    if parser.token_type == TT_INT:
        idx = _init_default_current_0(parser)
        advance(parser)
        return node_2(NT_LOOKUP, token, left, idx)

    symbol = expect_expression_of(parser, op.lbp + 1, NT_NAME)
    # symbol = grab_name(parser)
    return node_2(NT_LOOKUP, token, left, nodes.create_symbol_node(get_node_token(symbol), symbol))


def infix_lcurly_dot(parser, op, token, left):
    if parser.token_type == TT_INT:
        idx = _init_default_current_0(parser)
        advance(parser)
        return node_2(NT_LOOKUP, token, left, idx)

    exp = expression(parser, op.lbp - 1)
    # symbol = grab_name(parser)
    return node_2(NT_LOOKUP, token, left, nodes.create_symbol_node(get_node_token(exp), exp))


def _parse_modify_value(parser, key):
    if parser.token_type == TT_OR:
        advance_expected(parser, TT_OR)
        ntype = NT_OR
        if nodes.node_type(key) == NT_LOOKUP:
            parse_error(parser, u"default values are not supported for branch keys", nodes.node_token(key))
    else:
        advance_expected(parser, TT_ASSIGN)
        ntype = NT_ASSIGN

    value = expression(parser, 0, TERM_COMMA)
    return nodes.node_2(ntype, nodes.node_token(value), key, value)


def infix_lcurly(parser, op, token, left):
    items = []
    if parser.token_type != TT_RCURLY:
        key = expression(parser.modify_key_parser, 0)

        # field access
        if parser.token_type == TT_RCURLY:
            if nodes.node_type(key) == NT_NAME:
                key = nodes.create_symbol_node(nodes.node_token(key), key)

            advance_expected(parser, TT_RCURLY)
            return node_2(NT_LOOKUP, token, left, key)

        item = _parse_modify_value(parser, key)
        items.append(item)

        if parser.token_type != TT_RCURLY:
            advance_expected(parser, TT_COMMA)
            while parser.token_type != TT_RCURLY:
                key = expression(parser.modify_key_parser, 0)
                item = _parse_modify_value(parser, key)
                items.append(item)

                if parser.token_type != TT_COMMA:
                    break

                advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)

    return node_2(NT_MODIFY, token, left, list_node(items))


def _parse_comma_separated(parser, terminator, expected=None,
                           initial=None, advance_first=None,
                           not_empty=False, is_free=False):
    token = parser.token

    if is_free:
        open_free_layout(parser, token, [terminator], delimiter=TT_COMMA)

    if advance_first:
        advance_expected(parser, advance_first)

    if not initial:
        items = []
    else:
        items = initial
    if parser.token_type != terminator:
        while True:
            e = expression(parser, 0)
            if expected:
                check_node_types(parser, e, expected)

            items.append(e)
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, terminator)

    if not_empty and len(items) == 0:
        parse_error(parser, u"Expected one or more expressions", token)

    return list_node(items)


def _parse_comma_separated_to_one_of(parser, terminators, initial=None, advance_terminator=True, is_free=False):
    if not initial:
        items = []
    else:
        items = initial

    if is_free:
        open_free_layout(parser, parser.token, terminators, delimiter=TT_COMMA)

    if parser.token_type not in terminators:
        while True:
            e = expression(parser, 0)
            items.append(e)
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    if advance_terminator:
        advance_expected_one_of(parser, terminators)

    return list_node(items)


def infix_lparen_pattern(parser, op, token, left):
    # right = _parse_lparen_tuple(parser, token)
    items = _prefix_lcurly(parser, parser.map_key_parser, TT_RPAREN)
    right = node_1(NT_MAP, token, items)
    return node_2(NT_OF, token, right, left)


def infix_lparen(parser, op, token, left):
    unpack_call = False
    items = []
    index = 0

    if parser.token_type != TT_RPAREN:
        while True:
            if parser.token_type == TT_ELLIPSIS:
                unpack_call = True

            e = expression(parser, 0)
            items.append(e)

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)
            index += 1

    advance_expected(parser, TT_RPAREN)
    # END PARSING
    # CREATING CALL NODE
    # UNPACKING IS A SYNTACTIC SUGAR for apply function
    # f(x, y, z, ...a, ...b, y) =  apply(f, [x, y, z] ++ to_seq(a)  ++ to_seq(b) ++ [x])
    if unpack_call is False:
        body = node_2(NT_CALL, token, left, list_node(items))
    else:
        seqs = []
        l = []
        for item in items:
            if nodes.node_type(item) == NT_REST:
                if len(l) != 0:
                    seqs.append(nodes.create_array_node(token, l))
                    l = []
                seq = nodes.node_first(item)
                if nodes.node_type(seq) == NT_WILDCARD:
                    seq = nodes.create_fargs_node(nodes.node_token(seq))

                seqs.append(seq)
            else:
                l.append(item)
        if len(l) != 0:
            seqs.append(nodes.create_array_node(token, l))
        body = nodes.create_unpack_call(token, left, list_node(seqs))
    return body


def infix_lsquare(parser, op, token, left):
    exp = expression(parser, 0)
    advance_expected(parser, TT_RSQUARE)
    return node_2(NT_LOOKUP, token, left, exp)


def infix_name_pair(parser, op, token, left):
    check_token_type(parser, TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)

    ntype = node_infix_node_type(parser, token)
    return node_2(ntype, token, left, name)


def infix_bind(parser, op, token, left):
    name = expression(parser, 9)
    if nodes.node_token_type(name) != TT_NAME:
        parse_error(parser, u"Bad right value in pattern binding. Name expected", name)

    return node_2(NT_BIND, token, name, left)


##############################################################
# INFIX
##############################################################

def prefix_nud(parser, op, token):
    exp = expression(parser, op.pbp)
    ntype = node_prefix_node_type(parser, token)
    return node_1(ntype, token, exp)


def itself(parser, op, token):
    ntype = node_prefix_node_type(parser, token)
    return node_0(ntype, token)


def symbol_comma_nud(parser, op, token):
    parse_error(parser,
                u"Invalid use of , operator. To construct tuple put expressions inside parens", token)
    return None


def prefix_sharp(parser, op, token):
    check_token_types(parser, [TT_NAME, TT_MULTI_STR, TT_STR, TT_OPERATOR])

    ntype = node_prefix_node_type(parser, parser.token)
    exp = node_0(ntype, parser.token)
    advance(parser)
    return node_1(NT_SYMBOL, token, exp)


def prefix_not(parser, op, token):
    exp = expression(parser, 90)
    return node_1(NT_NOT, token, exp)


# most ambiguous operator,
# it can be tuple (1,2,3)
# single expression 2 * (2+3)
# list of expressions ( print(data) write(file, data) )
def prefix_lparen(parser, op, token):
    # unit
    if parser.token_type == TT_RPAREN:
        return parse_error(parser, u"Expected expression inside ()", parser.token)

    # single
    e = expression(parser, 0)
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return e

    # tuple
    if parser.token_type == TT_COMMA:
        items = [e]
        advance_expected(parser, TT_COMMA)
        items = _parse_comma_separated(parser, TT_RPAREN, initial=items)
        return node_1(NT_ARRAY, token, items)

    parse_error(parser, u"Invalid syntax inside parenthesis. Expect () (<exp>) or (<exp> , ...<exp>)", parser.token)
    # # group expression
    # rest = statements(parser, TERM_LPAREN)
    # advance_expected(parser, TT_RPAREN)
    # stmts = plist.cons(e, rest)
    # return stmts


def prefix_lparen_tuple(parser, op, token):
    return _parse_lparen_tuple(parser, token)


def _parse_lparen_tuple(parser, token):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(token)
        # return nodes.create_tuple_node(node, [])

    items = _parse_comma_separated(parser, TT_RPAREN)
    return node_1(NT_ARRAY, token, items)


def prefix_lparen_map_key(parser, op, token):
    e = expression(parser.expression_parser, 0)
    advance_expected(parser, TT_RPAREN)
    return e


def prefix_lparen_expression_only(parser, op, token):
    e = expression(parser, 0)
    advance_expected(parser, TT_RPAREN)
    return e


def prefix_lparen_module(parser, op, token):
    e = statement(parser)
    advance_expected(parser, TT_RPAREN)
    return e


def prefix_lsquare(parser, op, token):
    items = _parse_comma_separated(parser, TT_RSQUARE)
    return node_1(NT_ARRAY, token, items)


def prefix_lsquare_name_list(parser, op, token):
    items = _parse_comma_separated(parser, TT_RSQUARE)
    if len(items) == 0:
        parse_error(parser, u"Expected one or more types", parser.token)

    return node_1(NT_ARRAY, token, items)


def operator_as_symbol(parser, op, token):
    name = itself(parser, op, token)
    return nodes.create_symbol_from_operator(token, name)


# ------------------------- MAPS

def prefix_lcurly_pattern(parser, op, token):
    items = _prefix_lcurly(parser, parser.map_key_parser)
    return node_1(NT_MAP, token, items)


# for rpython static analysis, same function as below but with different parser
def prefix_lcurly(parser, op, token):
    items = _prefix_lcurly(parser, parser.map_key_parser)
    return node_1(NT_MAP, token, items)


def _prefix_lcurly(parser, key_parser, terminator=TT_RCURLY):
    items = []
    if parser.token_type != terminator:
        while True:
            key = expression(key_parser, 0, [TT_ASSIGN, TT_COMMA])
            if parser.token_type == TT_COMMA:
                value = empty_node()
            elif parser.token_type == terminator:
                value = empty_node()
            elif parser.token_type == TT_ASSIGN:
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0, [TT_COMMA])
            else:
                return parse_error(parser, u"Invalid syntax", parser.token)

            items.append(list_node([key, value]))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, terminator)
    return list_node(items)


def infix_map_pattern_of(parser, op, token, left):
    typename = expression(parser, 0, [TT_ASSIGN, TT_COMMA])
    return nodes.create_of_node(token, left, typename)


def infix_map_pattern_as(parser, op, token, left):
    # allow syntax like {key as var1}
    if nodes.node_type(left) == NT_NAME:
        left = nodes.create_symbol_node(nodes.node_token(left), left)

    name = expression(parser, 0, [TT_ASSIGN, TT_COMMA])
    return nodes.create_bind_node(nodes.node_token(left), name, left)


# ----------------------------------

def prefix_if(parser, op, token):
    branches = []

    cond = expression(parser, 0, TERM_IF_CONDITION)
    advance_expected_one_of(parser, TERM_IF_CONDITION)

    # TODO CHECK IF HERE LISTNODE REQUIRED
    body = statements(parser, TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    check_token_types(parser, TERM_IF_BODY)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = expression(parser, 0, TERM_IF_CONDITION)
        advance_expected_one_of(parser, TERM_IF_CONDITION)

        body = statements(parser, TERM_IF_BODY)
        check_token_types(parser, TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    advance_expected(parser, TT_ELSE)
    body = statements(parser, [])
    branches.append(list_node([empty_node(), body]))
    return node_1(NT_CONDITION, token, list_node(branches))


def prefix_try(parser, op, token):
    trybody = statements(parser, TERM_TRY)
    catches = []

    advance_expected(parser, TT_CATCH)

    if parser.token_type == TT_CATCH:
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_COLON)
        body = statements(parser, TERM_CATCH)
        catches.append(list_node([pattern, body]))

    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = statements(parser, [])
    else:
        finallybody = empty_node()

    return node_3(NT_TRY, token, trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expression(parser.pattern_parser, 0, TERM_BLOCK_START)
    return pattern


def prefix_throw(parser, op, token):
    exp = expression(parser, 0)
    return node_1(NT_THROW, token, exp)


# FUNCTION STUFF################################

def _parse_func_pattern(parser, arg_terminator):
    curtoken = parser.token
    open_free_layout(parser, parser.token, LAYOUT_LPAREN, delimiter=TT_COMMA)
    advance_expected(parser, TT_LPAREN)
    if parser.token_type == TT_RPAREN:
        pattern = nodes.create_unit_node(curtoken)
    else:
        els = _parse_comma_separated_to_one_of(parser.pattern_parser, arg_terminator,
                                               advance_terminator=False)
        pattern = nodes.create_array_node_from_list(curtoken, els)
    advance_expected(parser, TT_RPAREN)

    check_token_types(parser, arg_terminator)
    return pattern


####################################################


def prefix_fun(parser, op, token):
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    check_token_types(parser, [TT_LPAREN, TT_CASE])
    signature = _parse_func_pattern(parser, TERM_BLOCK_START)

    check_token_type(parser, TT_COLON)
    advance(parser)
    body = statements(parser, [])
    func = nodes.create_function_variants(signature, body)
    return node_2(NT_FUN, token, name, func)


def prefix_decorator(parser, op, token):
    decname = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
    if parser.token_type == TT_LPAREN:
        args = _parse_comma_separated(parser.expression_parser, TT_RPAREN, advance_first=TT_LPAREN)
    else:
        args = list_node([])

    decorated = statement(parser)
    check_node_types(parser, decorated, [NT_FUN, NT_CLASS, NT_DECORATOR])
    return nodes.node_3(NT_DECORATOR, token, decname, args, decorated)


###############################################################
# MODULE STATEMENTS
###############################################################

def _load_path_s(node):
    if nodes.node_type(node) == NT_LOOKUP:
        return _load_path_s(nodes.node_first(node)) + '.' + nodes.node_value_s(nodes.node_second(node))
    else:
        return nodes.node_value_s(node)


def _load_module(parser, exp):
    if api.DEBUG_MODE:
        return

    from capy.runtime import load

    if nodes.node_type(exp) == NT_AS:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(nodes.node_first(exp))
    elif nodes.node_type(exp) == NT_LOOKUP:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(exp)
    else:
        assert nodes.node_type(exp) == NT_NAME
        import_name = exp
        module_path = nodes.node_value_s(exp)

    state = parser.close()
    module = load.import_class(state.process, space.newsymbol_s(state.process, module_path))
    parser.open(state)


def ensure_tuple(t):
    nt = nodes.node_type(t)
    if nt != NT_ARRAY and nt != NT_UNIT:
        return nodes.create_array_node(get_node_token(t), [t])
    return t


def ensure_list_node(t):
    if not nodes.is_list_node(t):
        return list_node([t])
    return t


def stmt_import(parser, op, token):
    imported = expression(parser.import_parser, 0, [TT_LPAREN, TT_HIDING])

    if parser.token_type == TT_HIDING:
        ntype = NT_IMPORT_HIDING
        hiding = True
        advance(parser)
    else:
        hiding = False
        ntype = NT_IMPORT

    if parser.token_type == TT_LPAREN:
        names = expect_expression_of(parser.import_names_parser, 0, NT_ARRAY)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    else:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", token)
        names = empty_node()

    _load_module(parser, imported)
    return node_2(ntype, token, imported, names)


def stmt_include(parser, op, token):
    imported = expression(parser.import_parser, 0, [TT_LPAREN, TT_HIDING])

    if parser.token_type == TT_HIDING:
        ntype = NT_INCLUDE_HIDING
        hiding = True
        advance(parser)
    else:
        hiding = False
        ntype = NT_INCLUDE

    if parser.token_type == TT_LPAREN:
        names = expect_expression_of(parser.import_names_parser, 0, NT_ARRAY)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    else:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", token)
        names = empty_node()

    _load_module(parser, imported)
    return node_2(ntype, token, imported, names)


def symbol_or_name_value(parser, name):
    ntype = nodes.node_type(name)
    if ntype == NT_SYMBOL:
        data = nodes.node_first(name)
        if nodes.node_type(data) == NT_NAME:
            return nodes.node_value(data)
        elif nodes.node_type(data) == NT_STR:
            return strutil.unquote_w(nodes.node_value(data))
        else:
            assert False, "Invalid symbol"
    elif ntype == NT_NAME:
        return nodes.node_value(name)
    else:
        assert False, "Invalid name"


def prefix_name_as_symbol(parser, op, token):
    name = itself(parser, op, token)
    return nodes.create_symbol_node(token, name)


def symbol_operator_name(parser, op, token):
    name = itself(parser, op, token)
    return nodes.create_name_from_operator(token, name)

# DERIVE

def layout_class(parser, op, node):
    open_statement_layout(parser, node, LEVELS_CLASS, INDENTS_CLASS)


def prefix_class(parser, op, token):
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    if parser.token_type == TT_LPAREN:
        advance_expected(parser, TT_LPAREN)
        parent = expression(parser, 0)
        advance_expected(parser, TT_RPAREN)
    else:
        parent = nodes.empty_node()

    advance_expected(parser, TT_COLON)
    code = statements(parser, TERM_BLOCK)
    return nodes.node_3(NT_CLASS, token, name, parent, code)

# OPERATORS

def stmt_prefix(parser, op, token):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_ARRAY)

    length = nodes.array_node_length(t)
    if length != 3:
        return parse_error(parser, u"Expected tuple of 3 elements", token)

    children = nodes.node_first(t)
    op_node = children[0]
    check_node_type(parser, op_node, NT_NAME)
    func_node = children[1]
    check_node_types(parser, func_node, NAME_NODES)

    precedence_node = children[2]
    check_node_type(parser, precedence_node, NT_INT)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    try:
        precedence = strutil.string_to_int(nodes.node_value_s(precedence_node))
    except:
        return parse_error(parser, u"Invalid infix operator precedence", precedence_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_prefix(op, precedence, prefix_nud_function, func_value)

    parser_current_scope_add_operator(parser, op_value, op)
    return nodes.create_nil_node(token)


def stmt_infixl(parser, op, token):
    return _meta_infix(parser, token, led_infix_function)


def stmt_infixr(parser, op, token):
    return _meta_infix(parser, token, led_infixr_function)


def _meta_infix(parser, token, infix_function):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_ARRAY)
    children = nodes.node_first(t)

    length = nodes.array_node_length(t)
    if length != 3:
        return parse_error(parser, u"Expected tuple of 3 elements", token)

    op_node = children[0]
    check_node_type(parser, op_node, NT_NAME)

    func_node = children[1]
    check_node_types(parser, func_node, NAME_NODES)

    precedence_node = children[2]
    check_node_type(parser, precedence_node, NT_INT)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    try:
        precedence = strutil.string_to_int(nodes.node_value_s(precedence_node))
    except:
        return parse_error(parser, u"Invalid infix operator precedence", precedence_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_infix(op, precedence, infix_function, func_value)
    parser_current_scope_add_operator(parser, op_value, op)
    return nodes.create_nil_node(token)
