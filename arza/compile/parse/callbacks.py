from arza.compile.parse.basic import *
from arza.compile.parse.node_type import *
from arza.compile.parse import nodes
from arza.compile.parse.nodes import (node_token as get_node_token, node_0, node_1, node_2, node_3, node_4,
                                      list_node, empty_node)
from arza.types import space
from arza.misc import strutil
from arza.builtins import lang_names


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
    return nodes.create_call_node_name(token, op.prefix_function, [exp])


def led_infix_function(parser, op, token, left):
    exp = expression(parser, op.lbp)
    return nodes.create_call_node_name(token, op.infix_function, [left, exp])


def led_infixr_function(parser, op, token, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.create_call_node_name(token, op.infix_function, [left, exp])


def led_let_assign(parser, op, token, left):
    # status = open_code_layout(parser, parser.token, None, None)
    exp = expression(parser.expression_parser, 9)
    # close_layout(parser, status)
    return node_2(NT_ASSIGN, token, left, exp)


def layout_use(parser, op, node):
    open_statement_layout(parser, node, LEVELS_USE, INDENTS_USE)


def layout_trait(parser, op, node):
    open_statement_layout(parser, node, LEVELS_TRAIT, INDENTS_TRAIT)


def layout_type(parser, op, node):
    open_statement_layout(parser, node, None, INDENTS_TYPE)


def layout_interface(parser, op, node):
    open_statement_layout(parser, node, None, INDENTS_INTERFACE)


def layout_describe(parser, op, node):
    open_statement_layout(parser, node, None, INDENTS_DESCRIBE)


def layout_def(parser, op, node):
    open_statement_layout(parser, node, None, INDENTS_DEF)


def layout_match(parser, op, node):
    open_statement_layout(parser, node, LEVELS_MATCH, INDENTS_MATCH)


def layout_receive(parser, op, node):
    open_statement_layout(parser, node, LEVELS_MATCH, INDENTS_MATCH)


def layout_try(parser, op, node):
    open_statement_layout(parser, node, LEVELS_TRY, INDENTS_TRY)


def layout_let(parser, op, node):
    open_statement_layout(parser, node, LEVELS_LET, INDENTS_LET)


def layout_if(parser, op, node):
    open_statement_layout(parser, node, LEVELS_IF, INDENTS_IF)


def layout_fun(parser, op, node):
    open_statement_layout(parser, node, LEVELS_FUN, INDENTS_FUN)


def layout_decorator(parser, op, node):
    open_statement_layout(parser, node, LEVELS_DECORATOR, INDENTS_DECORATOR)


def layout_lparen(parser, op, node):
    open_free_layout(parser, node, [TT_RPAREN], delimiter=TT_COMMA)


def layout_lcurly(parser, op, node):
    open_free_layout(parser, node, [TT_RCURLY], delimiter=TT_COMMA)


def layout_lsquare(parser, op, node):
    open_free_layout(parser, node, [TT_RSQUARE], delimiter=TT_COMMA)


def prefix_backtick_operator(parser, op, token):
    opname_s = strutil.cat_both_ends(tokens.token_value_s(token))
    if opname_s == "::":
        return nodes.create_name_node_s(token, lang_names.CONS)

    opname = space.newstring_s(opname_s)
    op = parser_find_operator(parser, opname)
    if op is None or space.isvoid(op):
        return parse_error(parser, u"Invalid operator", token)
    if op.infix_function is None:
        return parse_error(parser, u"Expected infix operator", token)

    return nodes.create_name_node(token, op.infix_function)


def infix_backtick_name(parser, op, token, left):
    funcname = strutil.cat_both_ends(tokens.token_value_s(token))
    if not funcname:
        return parse_error(parser, u"invalid variable name in backtick expression", token)
    funcnode = nodes.create_name_node_s(token, funcname)

    right = expression(parser, op.lbp)
    return nodes.create_call_node_2(token, funcnode, left, right)


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


def hole_arg(index):
    return lang_names.HOLE_PREFIX + str(index)


def infix_lparen_pattern(parser, op, token, left):
    # right = _parse_lparen_tuple(parser, token)
    items = _prefix_lcurly(parser, parser.map_key_parser, TT_RPAREN)
    right = node_1(NT_MAP, token, items)
    return node_2(NT_OF, token, right, left)


def infix_lparen(parser, op, token, left):
    unpack_call = False
    items = []
    holes = []
    index = 0

    if parser.token_type != TT_RPAREN:
        while True:
            if parser.token_type == TT_WILDCARD:
                holes.append(index)
                items.append(nodes.create_name_node_s(parser.token, hole_arg(index)))
                advance(parser)
            else:
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
                    seqs.append(nodes.create_list_node(token, l))
                    l = []
                seq = nodes.node_first(item)
                if nodes.node_type(seq) == NT_WILDCARD:
                    seq = nodes.create_fargs_node(nodes.node_token(seq))

                seqs.append(seq)
            else:
                l.append(item)
        if len(l) != 0:
            seqs.append(nodes.create_list_node(token, l))
        body = nodes.create_unpack_call(token, left, list_node(seqs))

    if len(holes) == 0:
        return body

    sig = nodes.create_tuple_node(
        token,
        [nodes.create_name_node_s(token, hole_arg(hole)) for hole in holes]
    )

    func = nodes.create_lambda_node(token, sig, body)
    return func


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


def prefix_dollar(parser, op, token):
    advance_expected(parser, TT_LPAREN)
    check_token_type(parser, TT_NAME)
    exp = expect_expression_of(parser.modify_key_parser, 0, NT_LOOKUP, TERM_LPAREN)
    advance_expected(parser, TT_RPAREN)
    name_symbol = nodes.node_first(exp)
    name = nodes.node_first(name_symbol)
    path = nodes.node_second(exp)
    return node_2(NT_LENSE, token, name, path)


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
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(token)

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
        return node_1(NT_TUPLE, token, items)

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
    return node_1(NT_TUPLE, token, items)


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
    return node_1(NT_LIST, token, items)


def prefix_lsquare_name_list(parser, op, token):
    items = _parse_comma_separated(parser, TT_RSQUARE)
    if len(items) == 0:
        parse_error(parser, u"Expected one or more types", parser.token)

    return node_1(NT_LIST, token, items)


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


# if you want to allow optional TT_IN
# uncomment this and comment/delete func below
# you also need to implemente safguard against code like
# io:print(let x = 1 y = 2)
# but making let-in a statement not an option
# but let without in must be a statement
# may be something like parser.expression_level variable
# def prefix_let(parser, op, token):
#     letblock = statements(parser.let_parser, TERM_LET, LET_NODES)
#     if parser.token_type == TT_IN:
#         advance_expected(parser, TT_IN)
#         inexp = statements(parser, [])
#         return node_2(NT_LET, token, letblock, inexp)
#     else:
#         return letblock


def prefix_let(parser, op, token):
    letblock = statements(parser.let_parser, TERM_LET, LET_NODES)
    advance_expected(parser, TT_IN)
    inexp = statements(parser, [])
    return node_2(NT_LET, token, letblock, inexp)


def prefix_module_let(parser, op, token):
    exp = statements(parser.expression_parser.let_parser, [])
    if nodes.is_list_node(exp):
        check_list_node_type(parser, exp, NT_ASSIGN)
    else:
        check_node_type(parser, exp, NT_ASSIGN)
    return exp


def list_expression(parser, _rbp, terminators=None):
    return ensure_list_node(expression(parser, _rbp, terminators))


def prefix_try(parser, op, token):
    trybody = statements(parser, TERM_TRY)
    catches = []

    advance_expected(parser, TT_CATCH)

    if parser.token_type == TT_CASE:
        status = open_code_layout(parser, parser.token, level_tokens=LEVELS_MATCH, indentation_tokens=INDENTS_TRY)
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            pattern = _parse_pattern(parser)
            advance_expected(parser, TT_ASSIGN)
            body = statements(parser, TERM_CATCH_CASE)
            catches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ASSIGN)
        body = statements(parser, TERM_SINGLE_CATCH)
        catches.append(list_node([pattern, body]))

    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = statements(parser, [])
    else:
        finallybody = empty_node()

    return node_3(NT_TRY, token, trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expression(parser.pattern_parser, 0, TERM_PATTERN)
    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, TERM_FUN_GUARD)
        pattern = node_2(NT_WHEN, get_node_token(guard), pattern, guard)

    return pattern


def _parse_match_branches(parser, token, levels, indents):
    open_offside_layout(parser, parser.token, levels, indents)
    check_token_type(parser, TT_CASE)
    pattern_parser = parser.pattern_parser
    branches = []

    # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ASSIGN)
        body = statements(parser, TERM_CASE)

        branches.append(list_node([pattern, body]))

    if len(branches) == 0:
        parse_error(parser, u"Expected one or more patterns", token)

    return list_node(branches)


def prefix_match(parser, op, token):
    exp = free_expression(parser, 0, TERM_CASE)
    open_offside_layout(parser, parser.token, LEVELS_MATCH, INDENTS_MATCH)
    check_token_type(parser, TT_CASE)
    pattern_parser = parser.pattern_parser
    branches = []

    # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ASSIGN)
        body = statements(parser, TERM_CASE)

        branches.append(list_node([pattern, body]))

    if len(branches) == 0:
        parse_error(parser, u"Expected one or more patterns", token)

    return node_2(NT_MATCH, token, exp, list_node(branches))


def _parse_receive_branch(parser):
    pattern = _parse_pattern(parser)
    pattern = nodes.create_tuple_node(parser.token, [pattern])
    advance_expected(parser, TT_ASSIGN)
    body = statements(parser, TERM_CASE)
    return list_node([pattern, body])


def prefix_receive(parser, op, token):
    branches = []
    if parser.token_type != TT_CASE:
        branch = _parse_receive_branch(parser)
        branches.append(branch)
    else:
        open_offside_layout(parser, parser.token, LEVELS_RECEIVE, INDENTS_RECEIVE)
        check_token_type(parser, TT_CASE)

        # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            branch = _parse_receive_branch(parser)
            branches.append(branch)

    if len(branches) == 0:
        parse_error(parser, u"Expected one or more patterns", token)

    return node_1(NT_RECEIVE, token, list_node(branches))


def prefix_throw(parser, op, token):
    exp = expression(parser, 0)
    return node_1(NT_THROW, token, exp)


# FUNCTION STUFF################################

def _parse_func_pattern(parser, arg_terminator, guard_terminator):
    curtoken = parser.token
    if parser.token_type == TT_LPAREN:
        open_free_layout(parser, parser.token, LAYOUT_LPAREN, delimiter=TT_COMMA)
        advance_expected(parser, TT_LPAREN)
        if parser.token_type == TT_RPAREN:
            pattern = nodes.create_unit_node(curtoken)
        else:
            els = _parse_comma_separated_to_one_of(parser.fun_pattern_parser, arg_terminator,
                                                   advance_terminator=False)
            pattern = nodes.create_tuple_node_from_list(curtoken, els)
        advance_expected(parser, TT_RPAREN)
    else:
        e = expression(parser.fun_pattern_parser, 0)
        if parser.token_type == TT_COMMA:
            return parse_error(parser, u"Expected function arguments enclosed in parenthesis", curtoken)

        pattern = ensure_tuple(e)

    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, guard_terminator)
        pattern = node_2(NT_WHEN, get_node_token(guard), pattern, guard)
    else:
        check_token_types(parser, arg_terminator)

    return pattern


####################################################


def _parse_single_function(parser, signature):
    """
    fun f (x, y, z) = (exp)
    """
    check_token_type(parser, TT_ASSIGN)
    advance(parser)
    body = statements(parser, [])
    return nodes.create_function_variants(signature, body)


####################################################


def _parse_case_function(parser, term_pattern,
                         term_guard):
    """
    fun f
        | x, y, z = (exp)
        | (a, b, c) = (exp)
    """
    # bind to different name for not confusing reading code
    # it serves as basenode for node factory functions

    open_offside_layout(parser, parser.token, LEVELS_MATCH, INDENTS_FUN)
    check_token_type(parser, TT_CASE)

    funcs = []
    arity = None
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)
        args = _parse_func_pattern(parser, term_pattern, term_guard)
        if nodes.node_type(args) == NT_WHEN:
            args_sig = nodes.node_first(args)
        else:
            args_sig = args

        current_arity = nodes.tuple_node_length(args_sig)
        if arity is None:
            arity = current_arity
        elif arity != current_arity:
            return parse_error(parser, u"Inconsistent clause arity", args)

        advance_expected(parser, TT_ASSIGN)
        body = statements(parser, TERM_CASE)
        funcs.append(list_node([
            args, list_node([body])
        ]))

    return list_node(funcs)


####################################################


def _parse_recursive_function(parser, name, signature, term_pattern, term_guard):
    """
    parse fun f x y z
        | x y z -> (body)
        | a b c -> (body)
    """
    # bind to different name for not confusing reading code
    # it serves as basenode for node factory functions
    open_offside_layout(parser, parser.token, level_tokens=LEVELS_MATCH, indentation_tokens=INDENTS_FUN)
    node = signature

    if nodes.node_type(signature) == NT_WHEN:
        sig_node = nodes.node_first(signature)
    else:
        sig_node = signature
    sig_arity = nodes.tuple_node_length(sig_node)
    sig_args = nodes.node_first(sig_node)

    check_token_type(parser, TT_CASE)

    funcs = []

    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)
        args = _parse_func_pattern(parser, term_pattern, term_guard)
        if nodes.node_type(args) == NT_WHEN:
            args_sig = nodes.node_first(args)
        else:
            args_sig = args

        if nodes.tuple_node_length(args_sig) != sig_arity:
            return parse_error(parser, u"Inconsistent clause arity with function signature", args)

        advance_expected(parser, TT_ASSIGN)
        body = statements(parser, TERM_CASE)
        funcs.append(list_node([
            args, list_node([body])
        ]))

    func = nodes.create_fun_node(nodes.node_token(node), name, list_node(funcs))

    fargs_node = nodes.create_fargs_node(nodes.node_token(node))

    call_list = []

    for i, arg in enumerate(sig_args):
        ntype = nodes.node_type(arg)

        # special treatment of ...pattern in signature

        if ntype == NT_REST:
            arg_n = nodes.node_first(arg)
        else:
            arg_n = nodes.create_lookup_index_node(nodes.node_token(node), fargs_node, i)

        call_list.append(arg_n)

    body = list_node([nodes.create_call_node(nodes.node_token(node), func, list_node(call_list))])
    main_func = nodes.create_function_variants(signature, body)

    return main_func


####################################################

def _parse_case_or_simple_function(parser, term_pattern, term_guard):
    if parser.token_type == TT_CASE:
        funcs = _parse_case_function(parser, term_pattern, term_guard)
    else:
        signature = _parse_func_pattern(parser, TERM_FUN_SIGNATURE, term_guard)
        check_token_type(parser, TT_ASSIGN)
        funcs = _parse_single_function(parser, signature)
    return funcs


def _parse_function(parser, name, term_pattern, term_guard):
    if parser.token_type == TT_CASE:
        funcs = _parse_case_function(parser, term_pattern, term_guard)
    else:
        signature = _parse_func_pattern(parser, TERM_FUN_SIGNATURE, term_guard)
        if parser.token_type == TT_CASE:
            if nodes.is_empty_node(name):
                parse_error(parser, u"Expected name for such type of function", parser.token)

            funcs = _parse_recursive_function(parser, name, signature, term_pattern, term_guard)
        else:
            funcs = _parse_single_function(parser, signature)

    return funcs


def _parse_named_function(parser, token):
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    check_token_types(parser, [TT_LPAREN, TT_CASE])
    func = _parse_function(parser, name, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    return name, func


def prefix_let_fun(parser, op, token):
    name, funcs = _parse_named_function(parser.expression_parser, token)
    return node_2(NT_FUN, token, name, funcs)


def prefix_nameless_fun(parser, op, token):
    name = empty_node()
    funcs = _parse_function(parser, name, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    return node_2(NT_FUN, token, name, funcs)


def prefix_module_fun(parser, op, token):
    name, funcs = _parse_named_function(parser.expression_parser, token)
    return node_2(NT_FUN, token, name, funcs)


def prefix_decorator(parser, op, token):
    decname = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
    if parser.token_type == TT_LPAREN:
        args = _parse_comma_separated(parser.expression_parser, TT_RPAREN, advance_first=TT_LPAREN)
    else:
        args = list_node([])

    decorated = statement(parser)
    check_node_types(parser, decorated, [NT_FUN, NT_DEF, NT_DEF_PLUS, NT_DECORATOR])
    # decorated = expect_expression_of_types(parser, 0, [NT_FUN, NT_DEF, NT_DEF_PLUS, NT_DECORATOR])
    # if parser.token_type in [TT_DEF, TT_FUN, TT_AT_SIGN]:
    #     name, funcs = _parse_named_function(parser.expression_parser, token)
    #
    #     pass
    return nodes.node_3(NT_DECORATOR, token, decname, args, decorated)


###############################################################
# MODULE STATEMENTS
###############################################################


def _load_path_s(node):
    if nodes.node_type(node) == NT_IMPORTED_NAME:
        return _load_path_s(nodes.node_first(node)) + ':' + nodes.node_value_s(nodes.node_second(node))
    else:
        return nodes.node_value_s(node)


def _load_module(parser, exp):
    if api.DEBUG_MODE:
        return

    from arza.runtime import load

    if nodes.node_type(exp) == NT_AS:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(nodes.node_first(exp))
    elif nodes.node_type(exp) == NT_IMPORTED_NAME:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(exp)
    else:
        assert nodes.node_type(exp) == NT_NAME
        import_name = exp
        module_path = nodes.node_value_s(exp)

    state = parser.close()
    module = load.import_module(state.process, space.newsymbol_s(state.process, module_path))
    parser.open(state)


def ensure_tuple(t):
    nt = nodes.node_type(t)
    if nt != NT_TUPLE and nt != NT_UNIT:
        return nodes.create_tuple_node(get_node_token(t), [t])
    return t


def ensure_list_node(t):
    if not nodes.is_list_node(t):
        return list_node([t])
    return t


def stmt_from(parser, op, token):
    imported = expression(parser.import_parser, 0, TERM_FROM_IMPORTED)
    check_token_types(parser, [TT_IMPORT, TT_HIDE])
    if parser.token_type == TT_IMPORT:
        hiding = False
        ntype = NT_IMPORT_FROM
    else:
        hiding = True
        ntype = NT_IMPORT_FROM_HIDING

    advance(parser)
    if parser.token_type == TT_WILDCARD:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", token)

        names = empty_node()
        advance(parser)
    else:
        names = expect_expression_of(parser.import_names_parser, 0, NT_TUPLE)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])

    _load_module(parser, imported)
    return node_2(ntype, token, imported, names)


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
        names = expect_expression_of(parser.import_names_parser, 0, NT_TUPLE)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    else:
        if hiding is True:
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", token)
        names = empty_node()

    _load_module(parser, imported)
    return node_2(ntype, token, imported, names)


def stmt_export(parser, op, token):
    check_token_types(parser, [TT_LPAREN, TT_NAME])
    names = ensure_tuple(expect_expression_of_types(parser.import_names_parser, 0, EXPORT_NODES))
    check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    return node_1(NT_EXPORT, token, names)


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
    elif ntype == NT_IMPORTED_NAME:
        return nodes.imported_name_to_string(name)
    else:
        assert False, "Invalid name"


def prefix_name_as_symbol(parser, op, token):
    name = itself(parser, op, token)
    return nodes.create_symbol_node(token, name)


def symbol_operator_name(parser, op, token):
    name = itself(parser, op, token)
    return nodes.create_name_from_operator(token, name)


# TYPE ************************

def _parse_type_fields(parser, token):
    items = _parse_comma_separated(parser.type_parser, TT_RPAREN, advance_first=TT_LPAREN, is_free=True)
    fields = nodes.create_list_node_from_list(token, items)
    return fields


def stmt_type(parser, op, token):
    """
    complicated operator, possible syntaxes
    type T1 is (T4, T5) = (v1, v2, v3)
    type T1 = (v1, v2, v3)
    type T1 (v1, v2, v3)
    type T1
    """
    check_token_type(parser, TT_NAME)
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    if parser.token_type == TT_IS:
        advance_expected(parser, TT_IS)
        mixins_list = _parse_struct_or_name(parser.name_parser, TT_LPAREN, TT_RPAREN, NAME_NODES)
        mixins = nodes.create_list_node_from_list(token, mixins_list)
        advance_expected(parser, TT_ASSIGN)
        fields = _parse_type_fields(parser, token)
    else:
        mixins = empty_node()
        if parser.token_type == TT_ASSIGN:
            advance_expected(parser, TT_ASSIGN)
            fields = _parse_type_fields(parser, token)
        elif parser.token_type == TT_LPAREN:
            fields = _parse_type_fields(parser, token)
        else:
            fields = empty_node()

    return nodes.node_3(NT_TYPE, token, name, fields, mixins)


# DERIVE

def _parse_struct_or_name(parser, lterm, rterm, expected=None):
    if parser.token_type == lterm:
        items = _parse_comma_separated(parser, rterm, advance_first=lterm, is_free=True)
    else:
        item = expect_expression_of_types(parser, 0, expected)
        items = list_node([item])
    return items


def stmt_describe(parser, op, token):
    types = _parse_struct_or_name(parser.name_parser, TT_LPAREN, TT_RPAREN, NAME_NODES)

    advance_expected(parser, TT_AS)
    interfaces = nodes.create_list_node_from_list(
        token,
        _parse_struct_or_name(parser.name_parser, TT_LPAREN, TT_RPAREN, NAME_NODES)
    )

    derives = []
    for _type in types:
        derive = nodes.node_2(NT_DESCRIBE, token, _type, interfaces)
        derives.append(derive)

    return list_node(derives)


# DEF

def _parse_def_body(parser, token, signature):
    if parser.token_type == TT_AS:
        # TODO check if all args are wildcards
        advance_expected(parser, TT_AS)
        method = expression(parser, 0)
    else:
        funcs = _parse_single_function(parser, signature)
        method = node_2(NT_FUN, token, empty_node(), funcs)
    return method


def _parse_def_signature(parser, token):
    signature = _parse_func_pattern(parser, TERM_DEF_SIGNATURE, TERM_FUN_GUARD)
    dispatch = []
    fun_signature = []
    if nodes.node_type(signature) == NT_WHEN:
        sig_node = nodes.node_first(signature)
    else:
        sig_node = signature

    if nodes.node_type(sig_node) == NT_UNIT:
        parse_error(parser, u"Missing method arguments", token)
    sig_args = nodes.node_first(sig_node)

    for arg in sig_args:
        ntype = nodes.node_type(arg)
        if ntype == NT_OF:
            _subject = nodes.node_first(arg)
            _type = nodes.node_second(arg)
            if nodes.is_empty_node(_subject):
                _fun_arg = nodes.create_wildcard_node(nodes.node_token(_type))
                dispatch.append(_type)
            else:
                _fun_arg = _subject
                dispatch.append(_type)
            fun_signature.append(_fun_arg)
        elif ntype == NT_INTERFACE:
            inter = nodes.node_first(arg)
            fun_signature.append(inter)
            # tuple in generic function mean value arg
            tok = nodes.node_token(inter)
            sym = nodes.create_symbol_node_s(tok, lang_names.SVALUEOF)
            dispatch.append(nodes.create_tuple_node(tok, [sym, inter]))
        else:

            if ntype == NT_INT:
                _type = lang_names.TINT
            elif ntype == NT_FLOAT:
                _type = lang_names.TFLOAT
            elif ntype == NT_TRUE or ntype == NT_FALSE:
                _type = lang_names.TBOOL
            elif ntype == NT_CHAR:
                _type = lang_names.TCHAR
            elif ntype == NT_SYMBOL:
                _type = lang_names.TSYMBOL
            elif ntype == NT_STR or ntype == NT_MULTI_STR:
                _type = lang_names.TSTRING
            elif ntype == NT_LIST or ntype == NT_CONS:
                _type = lang_names.TLIST
            elif ntype == NT_MAP:
                _type = lang_names.TMAP
            elif ntype == NT_TUPLE or ntype == NT_UNIT:
                _type = lang_names.TTUPLE
            else:
                _type = None

            if not _type:
                _type = nodes.create_void_node(get_node_token(arg))
            else:
                _type = nodes.create_name_node_s(token, _type)
            dispatch.append(_type)
            fun_signature.append(arg)

    new_signature = nodes.create_tuple_node(nodes.node_token(signature), fun_signature)
    if nodes.node_type(signature) == NT_WHEN:
        new_signature = nodes.create_when_node(nodes.node_token(signature),
                                               new_signature, nodes.node_second(signature))

    return new_signature, dispatch


def _parse_def(parser, op, token, allow_non_determined):
    func_name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
    signature, dispatch_types = _parse_def_signature(parser.def_parser, token)

    if not allow_non_determined:
        checked = False
        for arg in dispatch_types:
            if nodes.node_type(arg) != NT_VOID:
                checked = True
                break
        if not checked:
            parse_error(parser, u"Expected one or more dispatch specification", token)

    dispatch_signature = nodes.create_list_node(token, dispatch_types)
    # TODO recursives
    # if parser.token_type == TT_CASE:
    #     funcs = _parse_recursive_function(parser, func_name, signature, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    # else:
    #     funcs = _parse_single_function(parser, signature)
    method = _parse_def_body(parser.def_parser.expression_parser, token, signature)
    return node_4(NT_DEF, token, func_name, dispatch_signature, method, signature)


def stmt_def(parser, op, token):
    return _parse_def(parser, op, token, False)


def prefix_def_of(parser, op, token):
    _type = expect_expression_of_types(parser, 0, NAME_NODES)
    return node_2(NT_OF, token, empty_node(), _type)


def infix_def_of(parser, op, token, left):
    _type = expect_expression_of_types(parser, 0, NAME_NODES)
    return node_2(NT_OF, token, left, _type)


# DEFPLUS

def _parse_defplus(parser, op, token, allow_non_determined=False):
    advance_expected(parser, TT_LPAREN)
    super_name = expression(parser.def_parser.def_plus_super_parser, 0)
    advance_expected(parser, TT_RPAREN)
    method = _parse_def(parser, op, token, allow_non_determined)
    return nodes.node_2(NT_DEF_PLUS, token, super_name, method)


def stmt_def_plus(parser, op, token):
    return _parse_defplus(parser, op, token, False)


# INTERFACE

def prefix_interface_valueof(parser, op, token):
    name = expect_expression_of(parser, 0, NT_SYMBOL)
    sym = nodes.create_symbol_node_s(token, lang_names.SVALUEOF)
    return node_1(NT_TUPLE, token, list_node([sym, name]))


def prefix_interface_generic_fun(parser, op, token):
    generic_name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    items = _parse_comma_separated(parser.generic_signature_parser, TT_RPAREN, advance_first=TT_LPAREN, is_free=True)
    args = node_1(NT_LIST, token, items)
    return node_2(NT_GENERIC, token, generic_name, args)


def prefix_interface_fun(parser, op, token):
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    args = _parse_comma_separated(parser.function_parser, TT_RPAREN, advance_first=TT_LPAREN, is_free=True)
    return node_2(NT_GENERIC, token, name, args)


def prefix_interface_use(parser, op, token):
    name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
    args = _parse_comma_separated(parser.function_parser, TT_RPAREN, advance_first=TT_LPAREN, is_free=True)
    return node_2(NT_USE, token, name, args)


def _parse_interface_fun_indexes(parser, alias, sig):
    args = []
    indexes = []
    index = 0
    for arg in sig:
        if nodes.is_list_node(arg):
            name = arg[0]
            typename = arg[1]
            if api.equal_b(nodes.node_value(typename), alias):
                indexes.append(nodes.create_int_node(nodes.node_token(name), index))
                args.append(name)
            else:
                args.append(name)
        else:
            if api.equal_b(nodes.node_value(arg), alias):
                indexes.append(nodes.create_int_node(nodes.node_token(arg), index))

            args.append(arg)

        index += 1

    if len(indexes) == 0:
        parse_error(parser, u"Missing interface role in method", nodes.node_token(args[0]))

    args_l = list_node(args)
    indexes_l = list_node(indexes)
    return args_l, indexes_l


def infix_interface_of(parser, op, token, left):
    typename = expect_expression_of(parser, 0, NT_SYMBOL)
    return list_node([left, typename])


def stmt_interface(parser, op, token):
    if parser.token_type == TT_ASSIGN:
        advance_expected(parser, TT_ASSIGN)
        return statements(parser.interface_parser.generic_parser, TERM_BLOCK)

    name = expect_expression_of(parser.name_parser, 0, NT_NAME)

    if parser.token_type == TT_LPAREN:
        advance(parser)
        alias = expect_expression_of(parser.name_parser, 0, NT_NAME)
        advance_expected(parser, TT_RPAREN)
    else:
        alias = name

    alias = nodes.node_value(alias)

    if parser.token_type == TT_IS:
        advance_expected(parser, TT_IS)
        subs = _parse_struct_or_name(parser.name_parser, TT_LPAREN, TT_RPAREN, NAME_NODES)
    else:
        subs = list_node([])

    if parser.token_type != TT_ASSIGN:
        return node_3(NT_INTERFACE, token, name,
                      nodes.create_list_node(token, []),
                      nodes.create_list_node_from_list(token, subs))

    advance_expected(parser, TT_ASSIGN)
    funcs = statements(parser.interface_parser, TERM_BLOCK)
    new_generics = []
    generics = []

    for func in funcs:
        generic_name = nodes.node_first(func)
        func_args = nodes.node_second(func)
        args, indexes = _parse_interface_fun_indexes(parser, alias, func_args)

        for index in indexes:
            item = node_1(NT_TUPLE, nodes.node_token(index), list_node([generic_name, index]))
            generics.append(item)

        if nodes.node_type(func) == NT_GENERIC:
            new_generics.append(
                node_2(NT_GENERIC,
                       token, generic_name,
                       nodes.create_list_node_from_list(token, args)))

    interface = node_3(NT_INTERFACE, token, name,
                       nodes.create_list_node(token, generics),
                       nodes.create_list_node_from_list(token, subs))
    if len(new_generics) == 0:
        return interface
    else:
        return list_node([list_node(new_generics), interface])


# TRAIT

def _trait_for_ensure_tuple(node):
    if not nodes.is_list_node(node):
        return list_node([node])
    else:
        return node


def prefix_trait_def_plus(parser, op, token):
    return _parse_defplus(parser, op, token, True)


def prefix_trait_def(parser, op, token):
    return _parse_def(parser, op, token, True)


def infix_trait_signature_of(parser, op, token, left):
    exp = expression(parser.name_parser, op.lbp)
    return node_2(NT_IS_IMPLEMENTED, token, left, exp)


def prefix_lparen_trait_for(parser, op, token):
    return _parse_comma_separated(parser.name_parser, TT_RPAREN)


def _parser_trait_for(parser, token, name, signature):
    result = []
    advance_expected(parser, TT_FOR)
    if parser.token_type == TT_LSQUARE:
        _types = _parse_comma_separated(parser.trait_parser.for_parser, TT_RSQUARE,
                                        advance_first=TT_LSQUARE,
                                        is_free=True)

        types = map(_trait_for_ensure_tuple, _types)
    elif parser.token_type == TT_LPAREN:
        sig = _parse_comma_separated(parser.name_parser, TT_RPAREN,
                                     advance_first=TT_LPAREN,
                                     is_free=True)

        types = list_node([sig])
    else:
        type_name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
        types = list_node([list_node([type_name])])

    result.append(
        _parse_trait_body(parser, token, name, signature)
    )

    if types is not None:
        for args in types:
            result.append(nodes.create_call_node(token, name, args))

    return list_node(result)


def has_name_in_list_node(parser, token, sig, alias):
    alias_val = nodes.node_value(alias)
    for arg in sig:
        arg_val = nodes.node_value(arg)
        if api.equal_b(arg_val, alias_val):
            return True
    return False


def _check_trait_type(parser, token, aliases, sig):
    for alias in aliases:
        if not has_name_in_list_node(parser, token, sig, alias):
            parse_error(parser, u"Missing type in method signature", token)


def _check_trait_type_any(parser, token, aliases, sig):
    for alias in aliases:
        if has_name_in_list_node(parser, token, sig, alias):
            return
    parse_error(parser, u"Missing type in method signature", token)


def _check_trait_statements(parser, token, aliases, body):
    for exp in body:
        if nodes.is_list_node(exp):
            _check_trait_statements(parser, token, aliases, exp)
            continue

        check_token = nodes.node_token(exp)
        ntype = nodes.node_type(exp)
        if ntype == NT_DEF:
            method_signature = nodes.node_second(exp)
            sig = nodes.node_first(method_signature)
            _check_trait_type(parser, check_token, aliases, sig)
        elif ntype == NT_CALL:
            args = nodes.node_second(exp)
            _check_trait_type_any(parser, check_token, aliases, args)


def _get_trait_aliases(parser, signature):
    aliases = []
    for node in signature:
        if nodes.node_type(node) == NT_IS_IMPLEMENTED:
            aliases.append(nodes.node_first(node))
        else:
            aliases.append(node)
    return list_node(aliases)


def _parse_trait_body(parser, token, name, signature):
    advance_expected(parser, TT_ASSIGN)

    body = statements(parser.trait_parser, [])

    aliases = _get_trait_aliases(parser, signature)
    _check_trait_statements(parser, token, aliases, body)

    args = nodes.create_tuple_node_from_list(token, signature)
    funcs = nodes.create_function_variants(args, body)
    return node_2(NT_FUN, token, name, funcs)


def stmt_trait(parser, op, token):
    if parser.token_type == TT_LPAREN:
        name = nodes.create_random_trait_name(token)
    else:
        name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    signature = _parse_comma_separated(parser.trait_parser.pattern_parser, TT_RPAREN, advance_first=TT_LPAREN,
                                       is_free=True)
    if parser.token_type == TT_FOR:
        return _parser_trait_for(parser, token, name, signature)
    return _parse_trait_body(parser, token, name, signature)


# OPERATORS

def stmt_prefix(parser, op, token):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_TUPLE)

    length = nodes.tuple_node_length(t)
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


def stmt_infixl(parser, op, token):
    return _meta_infix(parser, token, led_infix_function)


def stmt_infixr(parser, op, token):
    return _meta_infix(parser, token, led_infixr_function)


def _meta_infix(parser, token, infix_function):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_TUPLE)
    children = nodes.node_first(t)

    length = nodes.tuple_node_length(t)
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
