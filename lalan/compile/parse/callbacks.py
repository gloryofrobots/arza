from lalan.compile.parse.basic import *
from lalan.compile.parse.node_type import *
from lalan.compile.parse import nodes
from lalan.compile.parse.nodes import (node_token as __ntok, node_0, node_1, node_2, node_3, list_node, empty_node)
from lalan.types import space
from lalan.misc import strutil
from lalan.builtins import lang_names

NODE_TYPE_MAPPING = {
    TT_COLON: NT_IMPORTED_NAME,
    TT_TRUE: NT_TRUE,
    TT_FALSE: NT_FALSE,
    TT_INT: NT_INT,
    TT_FLOAT: NT_FLOAT,
    TT_STR: NT_STR,
    TT_MULTI_STR: NT_MULTI_STR,
    TT_CHAR: NT_CHAR,
    TT_WILDCARD: NT_WILDCARD,
    TT_NAME: NT_NAME,
    TT_TICKNAME: NT_NAME,
    TT_IF: NT_CONDITION,
    TT_MATCH: NT_MATCH,
    TT_EXPORT: NT_EXPORT,
    TT_IMPORT: NT_IMPORT,
    TT_TRAIT: NT_TRAIT,
    TT_THROW: NT_THROW,
    TT_ELLIPSIS: NT_REST,
    TT_ASSIGN: NT_ASSIGN,
    TT_OF: NT_OF,
    TT_AS: NT_AS,
    TT_AND: NT_AND,
    TT_NOT: NT_NOT,
    TT_OR: NT_OR,
    TT_SHARP: NT_SYMBOL,
    TT_OPERATOR: NT_NAME,
    TT_DOUBLE_COLON: NT_CONS,
    # TT_COMMA: NT_COMMA,
    TT_CASE: NT_CASE,
    # TT_END_EXPR: -100,
}


def __ntype(node):
    node_type = NODE_TYPE_MAPPING[nodes.node_token_type(node)]
    return node_type


def _init_default_current_0(parser):
    return nodes.node_0(__ntype(parser.node), __ntok(parser.node))


##############################################################
# INFIX
##############################################################

#
def led_infix(parser, op, node, left):
    exp = expression(parser, op.lbp)
    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return node_2(__ntype(node), __ntok(node), left, exp)


def prefix_nud_function(parser, op, node):
    exp = expression(parser, op.pbp)
    return nodes.create_call_node_name(node, op.prefix_function, [exp])


def led_infix_function(parser, op, node, left):
    exp = expression(parser, op.lbp)
    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def led_infixr_function(parser, op, node, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def led_let_assign(parser, op, node, left):
    exp = expression(parser.expression_parser, 9)
    return node_2(NT_ASSIGN, __ntok(node), left, exp)


def prefix_backtick_operator(parser, op, node):
    opname_s = strutil.cat_both_ends(nodes.node_value_s(node))
    if opname_s == "::":
        return nodes.create_name_node_s(node, lang_names.CONS)

    opname = space.newstring_s(opname_s)
    op = parser_find_operator(parser, opname)
    if op is None or space.isvoid(op):
        return parse_error(parser, u"Invalid operator", node)
    if op.infix_function is None:
        return parse_error(parser, u"Expected infix operator", node)

    return nodes.create_name_node(node, op.infix_function)


def infix_backtick_name(parser, op, node, left):
    funcname = strutil.cat_both_ends(nodes.node_value_s(node))
    if not funcname:
        return parse_error(parser, u"invalid variable name in backtick expression", node)
    funcnode = nodes.create_name_node_s(node, funcname)

    right = expression(parser, op.lbp)
    return nodes.create_call_node_2(node, funcnode, left, right)


def infix_when(parser, op, node, left):
    branches = []
    condition = expression(parser, 0, TERM_WHEN_EXPRESSION)
    branches.append(list_node([condition, list_node([left])]))
    advance_expected(parser, TT_ELSE)
    false_exp = expression(parser, 0)
    branches.append(list_node([empty_node(), list_node([false_exp])]))
    return node_1(NT_CONDITION, __ntok(node), list_node(branches))


def infix_arrow(parser, op, node, left):
    args = ensure_tuple(left)
    exp = expression(parser, 0)
    return nodes.create_lambda_node(node, args, exp)


def infix_comma(parser, op, node, left):
    # it would be very easy, if not needed for trailing commas, aka postfix
    # operators
    tt = parser.token_type
    # check for end expr because it will be auto inserted and it has nud which
    # produces empty node
    if not node_has_nud(parser, parser.node) \
            or tt == TT_END_EXPR:
        # check some corner cases with 1,2,.name or 1,2,,
        if tt == TT_DOT or tt == TT_COMMA:
            parse_error(parser, "Invalid tuple syntax", node)

        return left
    right = expression(parser, op.lbp)
    return node_2(NT_COMMA, __ntok(node), left, right)


def infix_dot(parser, op, node, left):
    if parser.token_type == TT_INT:
        idx = _init_default_current_0(parser)
        advance(parser)
        return node_2(NT_LOOKUP, __ntok(node), left, idx)

    symbol = expect_expression_of(parser, op.lbp + 1, NT_NAME)
    # symbol = grab_name(parser)
    return node_2(NT_LOOKUP, __ntok(node), left, nodes.create_symbol_node(symbol, symbol))


def infix_lcurly(parser, op, node, left):
    items = []
    if parser.token_type != TT_RCURLY:
        key = expression(parser.map_key_parser, 0)

        # field access
        if parser.token_type == TT_RCURLY:
            if nodes.node_type(key) == NT_NAME:
                key = nodes.create_symbol_node(key, key)

            advance_expected(parser, TT_RCURLY)
            return node_2(NT_LOOKUP, __ntok(node), left, key)

        advance_expected(parser, TT_ASSIGN)
        value = expression(parser, 0, [TT_COMMA])

        items.append(list_node([key, value]))

        if parser.token_type != TT_RCURLY:
            advance_expected(parser, TT_COMMA)

            while True:
                key = expression(parser, 0)
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0, [TT_COMMA])

                items.append(list_node([key, value]))

                if parser.token_type != TT_COMMA:
                    break

                advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)

    return node_2(NT_MODIFY, __ntok(node), left, list_node(items))


def _parse_comma_separated(parser, terminator, expected=None, initial=None, advance_first=None, not_empty=False):
    node = parser.node
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
        parse_error(parser, u"Expected one or more expressions", node)

    return list_node(items)


def _parse_comma_separated_to_one_of(parser, terminators, initial=None, advance_terminator=True):
    if not initial:
        items = []
    else:
        items = initial

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


def infix_lparen(parser, op, node, left):
    unpack_call = False
    items = []
    holes = []
    index = 0

    if parser.token_type != TT_RPAREN:
        while True:
            if parser.token_type == TT_WILDCARD:
                holes.append(index)
                items.append(nodes.create_name_node_s(parser.node, hole_arg(index)))
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
        body = node_2(NT_CALL, __ntok(node), left, list_node(items))
    else:
        seqs = []
        l = []
        for item in items:
            if nodes.node_type(item) == NT_REST:
                if len(l) != 0:
                    seqs.append(nodes.create_list_node(node, l))
                    l = []
                seq = nodes.node_first(item)
                if nodes.node_type(seq) == NT_WILDCARD:
                    seq = nodes.create_fargs_node(seq)

                seqs.append(seq)
            else:
                l.append(item)
        if len(l) != 0:
            seqs.append(nodes.create_list_node(node, l))
        body = nodes.create_unpack_call(node, left, list_node(seqs))

    if len(holes) == 0:
        return body

    sig = nodes.create_tuple_node(
        node,
        [nodes.create_name_node_s(node, hole_arg(hole)) for hole in holes]
    )

    func = nodes.create_lambda_node(node, sig, body)
    return func


def _infix_lparen(parser):
    args = _parse_comma_separated(parser, TT_RPAREN)
    return args


def infix_lsquare(parser, op, node, left):
    exp = expression(parser, 0)
    advance_expected(parser, TT_RSQUARE)
    return node_2(NT_LOOKUP, __ntok(node), left, exp)


def infix_name_pair(parser, op, node, left):
    check_token_type(parser, TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)
    return node_2(__ntype(node), __ntok(node), left, name)


def infix_at(parser, op, node, left):
    ltype = nodes.node_token_type(left)
    if ltype != TT_NAME:
        parse_error(parser, u"Bad lvalue in pattern binding", left)

    exp = expression(parser, 9)
    return node_2(NT_BIND, __ntok(node), left, exp)


##############################################################
# INFIX
##############################################################

def prefix_nud(parser, op, node):
    exp = expression(parser, op.pbp)
    return node_1(__ntype(node), __ntok(node), exp)


def itself(parser, op, node):
    return node_0(__ntype(node), __ntok(node))


def symbol_comma_nud(parser, op, node):
    parse_error(parser,
                u"Invalid use of , operator. To construct tuple put expressions inside parens", node)
    return None


def prefix_sharp(parser, op, node):
    check_token_types(parser, [TT_NAME, TT_MULTI_STR, TT_STR, TT_OPERATOR])
    exp = node_0(__ntype(parser.node), __ntok(parser.node))
    advance(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def prefix_not(parser, op, node):
    exp = expression(parser, 90)
    return node_1(NT_NOT, __ntok(node), exp)


# most ambiguous operator,
# it can be tuple (1,2,3)
# single expression 2 * (2+3)
# list of expressions ( print(data) write(file, data) )
def prefix_lparen(parser, op, node):
    # unit
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

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
        return node_1(NT_TUPLE, __ntok(node), items)

    # group expression
    rest = statements(parser, TERM_LPAREN)
    advance_expected(parser, TT_RPAREN)
    stmts = plist.cons(e, rest)
    return stmts


def prefix_lparen_tuple(parser, op, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)
        # return nodes.create_tuple_node(node, [])

    items = _parse_comma_separated(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), items)


def prefix_lparen_map_key(parser, op, node):
    e = expression(parser.expression_parser, 0)
    advance_expected(parser, TT_RPAREN)
    return e


def prefix_lparen_expression_only(parser, op, node):
    e = expression(parser, 0)
    advance_expected(parser, TT_RPAREN)
    return e


def prefix_lparen_expression(parser, op, node):
    # unit
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

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
        return node_1(NT_TUPLE, __ntok(node), items)

    parse_error(parser, u"Invalid syntax inside parenthesis. Expect () (<exp>) or (<exp> , ...<exp>)", parser.node)


def prefix_lsquare(parser, op, node):
    items = _parse_comma_separated(parser, TT_RSQUARE)
    return node_1(NT_LIST, __ntok(node), items)


def prefix_lsquare_name_list(parser, op, node):
    items = _parse_comma_separated(parser, TT_RSQUARE)
    if len(items) == 0:
        parse_error(parser, u"Expected one or more types", parser.node)

    return node_1(NT_LIST, __ntok(node), items)


def operator_as_symbol(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_symbol_from_operator(node, name)


# ------------------------- MAPS

def prefix_lcurly_pattern(parser, op, node):
    items = _prefix_lcurly(parser, parser.map_key_parser)
    return node_1(NT_MAP, __ntok(node), items)


# for rpython static analysis, same function as below but with different parser
def prefix_lcurly(parser, op, node):
    items = _prefix_lcurly(parser, parser.map_key_parser)
    return node_1(NT_MAP, __ntok(node), items)


def _prefix_lcurly(parser, key_parser):
    items = []
    if parser.token_type != TT_RCURLY:
        while True:
            key = expression(key_parser, 0, [TT_ASSIGN, TT_COMMA])
            if parser.token_type == TT_COMMA:
                value = empty_node()
            elif parser.token_type == TT_RCURLY:
                value = empty_node()
            elif parser.token_type == TT_ASSIGN:
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0, [TT_COMMA])
            else:
                return parse_error(parser, u"Invalid map syntax", parser.node)

            items.append(list_node([key, value]))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return list_node(items)


def infix_map_pattern_of(parser, op, node, left):
    typename = expression(parser, 0, [TT_ASSIGN, TT_COMMA])
    return nodes.create_of_node(node, left, typename)


def infix_map_pattern_at(parser, op, node, left):
    real_key = expression(parser, 0, [TT_ASSIGN, TT_COMMA])
    # allow syntax like {var1@ key}
    if nodes.node_type(real_key) == NT_NAME:
        real_key = nodes.create_symbol_node(real_key, real_key)

    return nodes.create_bind_node(left, left, real_key)


# ----------------------------------

def prefix_if(parser, op, node):
    branches = []

    cond = expression(parser, 0, TERM_IF_CONDITION)
    advance_expected_one_of(parser, TERM_IF_CONDITION)

    # TODO CHECK IF HERE LISTNODE REQUIRED
    body = expression(parser, 0, TERM_IF_BODY)

    branches.append(list_node([cond, body]))
    check_token_types(parser, TERM_IF_BODY)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = expression(parser, 0, TERM_IF_CONDITION)
        advance_expected_one_of(parser, TERM_IF_CONDITION)

        body = expression(parser, 0, TERM_IF_BODY)
        check_token_types(parser, TERM_IF_BODY)
        branches.append(list_node([cond, body]))

    advance_expected(parser, TT_ELSE)

    body = expression(parser, 0)
    branches.append(list_node([empty_node(), body]))
    return node_1(NT_CONDITION, __ntok(node), list_node(branches))


def prefix_let(parser, op, node):
    letblock = statements(parser.let_parser, TERM_LET, [NT_TRY, NT_FUN, NT_ASSIGN])
    advance_expected(parser, TT_IN)
    inexp = ensure_list_node(expression(parser, 0))
    return node_2(NT_LET, __ntok(node), letblock, inexp)


def prefix_module_let(parser, op, node):
    exp = expression(parser.expression_parser.let_parser, 0)
    if nodes.is_list_node(exp):
        check_list_node_type(parser, exp, NT_ASSIGN)
    else:
        check_node_type(parser, exp, NT_ASSIGN)
    return exp


def list_expression(parser, _rbp, terminators=None):
    return ensure_list_node(expression(parser, _rbp, terminators))


def prefix_try(parser, op, node):
    trybody = expression(parser, 0, TERM_TRY)
    catches = []

    check_token_type(parser, TT_CATCH)
    advance(parser)

    if parser.token_type == TT_CASE:
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            # pattern = expressions(parser.pattern_parser, 0)
            pattern = _parse_pattern(parser)
            advance_expected(parser, TT_ASSIGN)
            body = list_expression(parser, 0, TERM_CATCH_CASE)
            catches.append(list_node([pattern, body]))
    else:
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ASSIGN)
        body = list_expression(parser, 0, TERM_SINGLE_CATCH)
        catches.append(list_node([pattern, body]))

    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = list_expression(parser, 0)
    else:
        finallybody = empty_node()

    return node_3(NT_TRY, __ntok(node), trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expression(parser.pattern_parser, 0, TERM_PATTERN)
    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, TERM_FUN_GUARD)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def _parse_match(parser, node, exp):
    check_token_type(parser, TT_CASE)
    pattern_parser = parser.pattern_parser
    branches = []

    # TODO COMMON PATTERN MAKE ONE FUNC with try/fun/match
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = _parse_pattern(parser)

        advance_expected(parser, TT_ASSIGN)
        body = list_expression(parser, 0, TERM_CASE)

        branches.append(list_node([pattern, body]))

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    return node_2(NT_MATCH, __ntok(node), exp, list_node(branches))


def prefix_match(parser, op, node):
    exp = expression(parser, 0)
    return _parse_match(parser, node, exp)


def prefix_throw(parser, op, node):
    exp = expression(parser, 0)
    return node_1(__ntype(node), __ntok(node), exp)


# FUNCTION STUFF################################

def _parse_func_pattern(parser, arg_terminator, guard_terminator, allow_guards=True):
    curnode = parser.node
    if parser.token_type == TT_LPAREN:
        advance_expected(parser, TT_LPAREN)
        if parser.token_type == TT_RPAREN:
            pattern = nodes.create_unit_node(curnode)
        else:
            els = _parse_comma_separated_to_one_of(parser.fun_pattern_parser, arg_terminator,
                                                   advance_terminator=False)
            pattern = nodes.create_tuple_node_from_list(curnode, els)
        advance_expected(parser, TT_RPAREN)
    else:
        e = expression(parser.fun_pattern_parser, 0)
        if parser.token_type == TT_COMMA:
            return parse_error(parser, u"Expected function arguments enclosed in parenthesis", curnode)

        pattern = ensure_tuple(e)

    if parser.token_type == TT_WHEN:
        if not allow_guards:
            return parse_error(parser, u"Unexpected guard expression", curnode)

        advance(parser)
        guard = expression(parser.guard_parser, 0, guard_terminator)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)
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
    body = expression(parser, 0)
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
        body = expression(parser, 0)
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
        body = expression(parser, 0)
        funcs.append(list_node([
            args, list_node([body])
        ]))

    func = nodes.create_fun_node(node, name, list_node(funcs))

    fargs_node = nodes.create_fargs_node(node)

    call_list = []

    for i, arg in enumerate(sig_args):
        ntype = nodes.node_type(arg)

        # special treatment of ...pattern in signature

        if ntype == NT_REST:
            arg_n = nodes.node_first(arg)
        else:
            arg_n = nodes.create_lookup_index_node(node, fargs_node, i)

        call_list.append(arg_n)

    body = list_node([nodes.create_call_node(node, func, list_node(call_list))])
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
                parse_error(parser, u"Expected name for such type of function", parser.node)

            funcs = _parse_recursive_function(parser, name, signature, term_pattern, term_guard)
        else:
            funcs = _parse_single_function(parser, signature)

    return funcs


def _parse_named_function(parser, node):
    name = expect_expression_of(parser.name_parser, 0, NT_NAME)
    check_token_types(parser, [TT_LPAREN, TT_CASE])
    func = _parse_function(parser, name, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    return name, func


def prefix_let_fun(parser, op, node):
    name, funcs = _parse_named_function(parser.expression_parser, node)
    return node_2(NT_FUN, __ntok(node), name, funcs)


def prefix_nameless_fun(parser, op, node):
    name = empty_node()
    funcs = _parse_function(parser, name, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    return node_2(NT_FUN, __ntok(node), name, funcs)


def prefix_module_fun(parser, op, node):
    name, funcs = _parse_named_function(parser.expression_parser, node)
    return node_2(NT_FUN, __ntok(node), name, funcs)


###############################################################
# MODULE STATEMENTS
###############################################################


def _load_path_s(node):
    if nodes.node_type(node) == NT_IMPORTED_NAME:
        return _load_path_s(nodes.node_first(node)) + ':' + nodes.node_value_s(nodes.node_second(node))
    else:
        return nodes.node_value_s(node)


def _load_module(parser, exp):
    from lalan.runtime import load

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
        return nodes.create_tuple_node(t, [t])
    return t


def ensure_list_node(t):
    if not nodes.is_list_node(t):
        return list_node([t])
    return t


def stmt_from(parser, op, node):
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
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", node)

        names = empty_node()
        advance(parser)
    else:
        names = expect_expression_of(parser.import_names_parser, 0, NT_TUPLE)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])

    _load_module(parser, imported)
    return node_2(ntype, __ntok(node), imported, names)


def stmt_import(parser, op, node):
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
            return parse_error(parser, u"Invalid usage of hide keyword. Symbol(s) expected", node)
        names = empty_node()

    _load_module(parser, imported)
    return node_2(ntype, __ntok(node), imported, names)


def stmt_export(parser, op, node):
    check_token_types(parser, [TT_LPAREN, TT_NAME])
    names = expect_expression_of(parser.import_names_parser, 0, NT_TUPLE)
    check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    return node_1(NT_EXPORT, __ntok(node), names)


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


def prefix_name_as_symbol(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_symbol_node(name, name)


def symbol_operator_name(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_name_from_operator(node, name)


# TYPES ************************

def symbol_list_to_arg_tuple(parser, node, symbols):
    args = []
    children = nodes.node_first(symbols)
    for child in children:
        assert nodes.node_type(child) == NT_SYMBOL
        name = nodes.node_first(child)
        args.append(name)

    return nodes.node_1(NT_TUPLE, nodes.node_token(node), list_node(args))


def _symbols_to_args(parser, node, symbols):
    args = []
    for child in symbols:
        assert nodes.node_type(child) == NT_SYMBOL
        name = nodes.node_first(child)
        args.append(name)

    return nodes.node_1(NT_TUPLE, nodes.node_token(node), list_node(args))


def stmt_type(parser, op, node):
    nodes = ensure_list_node(expression(parser.type_parser, 0))
    return nodes


def prefix_typename(parser, op, node):
    typename = itself(parser, op, node)

    # expect for infix_lparen_type to finish the job
    if parser.token_type == TT_LPAREN:
        return typename
    # support for singleton type
    return nodes.node_2(NT_TYPE, __ntok(node), typename, empty_node())


def infix_lparen_type(parser, op, node, left):
    check_node_type(parser, left, NT_NAME)
    items = _infix_lparen(parser.symbol_list_parser)
    fields = node_1(NT_LIST, __ntok(node), items)
    return node_2(NT_TYPE, __ntok(node), left, fields)


# INTERFACE

def stmt_interface(parser, op, node):
    nodes = list_expression(parser.interface_parser, 0)
    return nodes


def prefix_interface_name(parser, op, node):
    name = nodes.create_name_node(node, nodes.node_value(node))
    items = _parse_comma_separated(parser.interface_function_parser, TT_RPAREN, advance_first=TT_LPAREN)
    return node_2(NT_INTERFACE, __ntok(node), name, nodes.create_list_node_from_list(node, items))


def infix_interface_dot(parser, op, node, left):
    # supported syntax
    check_node_types(parser, left, NAME_NODES)
    position = expression(parser.int_parser, 0)
    return node_1(NT_TUPLE, __ntok(node), list_node([left, position]))


# DEF

def _parse_def_body(parser, node, signature):
    if parser.token_type == TT_AS:
        # TODO check if all args are wildcards
        advance_expected(parser, TT_AS)
        method = expression(parser, 0)
    else:
        if parser.token_type == TT_CASE:
            body = _parse_match(parser, node, nodes.create_fargs_node(node))
            funcs = nodes.create_function_variants(signature, body)
        else:
            funcs = _parse_single_function(parser, signature)

        method = node_2(NT_FUN, __ntok(node), empty_node(), funcs)
    return method


def _parse_def_signature(parser, node):
    signature = _parse_func_pattern(parser, TERM_FUN_SIGNATURE, TERM_FUN_GUARD, allow_guards=False)
    dispatch = []
    fun_signature = []
    sig_args = nodes.node_first(signature)
    for arg in sig_args:
        if nodes.node_type(arg) == NT_DISPATCH:
            _subject = nodes.node_first(arg)
            _type = nodes.node_second(arg)
            if nodes.is_empty_node(_subject):
                _fun_arg = nodes.create_wildcard_node(_type)
                dispatch.append(_type)
            else:
                _fun_arg = _subject
                dispatch.append(_type)
            fun_signature.append(_fun_arg)
        else:
            fun_signature.append(arg)
            dispatch.append(nodes.create_void_node(arg))

    new_signature = nodes.create_tuple_node(signature, fun_signature)
    dispatch_signature = nodes.create_list_node(node, dispatch)
    return new_signature, dispatch_signature


def stmt_def(parser, op, node):
    func_name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)

    # TODO recursives
    # if parser.token_type == TT_CASE:
    #     funcs = _parse_recursive_function(parser, func_name, signature, TERM_FUN_PATTERN, TERM_FUN_GUARD)
    # else:
    #     funcs = _parse_single_function(parser, signature)

    signature, dispatch_signature = _parse_def_signature(parser.def_parser, node)

    if nodes.list_node_length(dispatch_signature) == 0:
        parse_error(parser, u"Expected one or more dispatch specification", node)

    method = _parse_def_body(parser.expression_parser, node, signature)
    return node_3(NT_DEF, __ntok(node), func_name, dispatch_signature, method)


def stmt_generic(parser, op, node):
    generics = ensure_list_node(expression(parser.generic_parser, 0))
    return generics


def prefix_generic_name(parser, op, node):
    name = itself(parser, op, node)
    return _parse_generic_signature(parser, op, node, name)


def prefix_generic_operator(parser, op, node):
    name = symbol_operator_name(parser, op, node)
    return _parse_generic_signature(parser, op, node, name)


def _parse_generic_signature(parser, op, node, generic_name):
    check_node_type(parser, generic_name, NT_NAME)
    items = _parse_comma_separated(parser.generic_signature_parser, TT_RPAREN, advance_first=TT_LPAREN)
    args = node_1(NT_LIST, __ntok(node), items)
    return node_2(NT_GENERIC, __ntok(node), generic_name, args)


def prefix_def_dispatch(parser, op, node):
    _type = expect_expression_of_types(parser, 0, NAME_NODES)
    return node_2(NT_DISPATCH, __ntok(node), empty_node(), _type)


def infix_def_dispatch(parser, op, node, left):
    _type = expect_expression_of_types(parser, 0, NAME_NODES)
    return node_2(NT_DISPATCH, __ntok(node), left, _type)


# EXTEND
def _parse_name_or_list(parser):
    if parser.token_type == TT_LSQUARE:
        types = _parse_comma_separated(parser, TT_RSQUARE, advance_first=TT_LSQUARE)
    else:
        types = list_node([expect_expression_of_types(parser, 0, NAME_NODES)])
    return types


def _extend_transform(parser, node, signature, methods):
    result = []
    for method in methods:
        # flatten
        if nodes.is_list_node(method):
            result += _extend_transform(parser, node, signature, method)
        else:
            method_name = nodes.node_first(method)
            method_body = nodes.node_second(method)
            new_method = node_3(NT_DEF, __ntok(node), method_name, signature, method_body)
            result.append(new_method)
    return result


def stmt_extend(parser, op, node):
    types = []
    while parser.token_type != TT_WITH:
        _type_e = _parse_name_or_list(parser.name_parser)
        signature = nodes.create_list_node_from_list(node, _type_e)
        types.append(signature)

    advance_expected(parser, TT_WITH)
    if len(types) == 0:
        return parse_error(parser, u"Expected one or more signatures in extend statement", parser.node)

    methods = list_expression(parser.extend_parser, 0)

    result = []
    # unrolling signatures
    for signature in types:
        # Inserting signature
        result += _extend_transform(parser, node, signature, methods)

    return list_node(result)


def prefix_extend_def(parser, op, node):
    # def (f1, f2, ...fn) with [T1, T2, ...Tn]
    if parser.token_type == TT_LPAREN:
        funcs = _parse_comma_separated(parser.name_parser, TT_RPAREN, advance_first=TT_LPAREN)
        advance_expected(parser, TT_WITH)
        types = nodes.create_list_node_from_list(parser.node, _parse_name_or_list(parser.name_parser))
        defs = []
        for f in funcs:
            e = nodes.create_lookup_node(f, f, types)
            defs.append(node_2(NT_DEF, __ntok(node), f, e))
        return list_node(defs)
    # def {f1, f2, ...fn} from expression()
    elif parser.token_type == TT_LCURLY:
        funcs = _parse_comma_separated(parser.name_parser, TT_RCURLY, advance_first=TT_LCURLY)
        advance_expected(parser, TT_FROM)
        source = expression(parser.expression_parser, 0)
        defs = []
        for f in funcs:
            e = nodes.create_lookup_node(source, source, f)
            defs.append(node_2(NT_DEF, __ntok(node), f, e))
        return list_node(defs)
    # same as top module def but without types
    else:
        func_name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)

        if parser.token_type == TT_LSQUARE:
            return parse_error(parser, u"This definition of generic method could not have signature", parser.node)

        method = _parse_def_body(parser, node)
        return node_2(NT_DEF, __ntok(node), func_name, method)


# OPERATORS

def stmt_prefix(parser, op, node):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_TUPLE)

    length = nodes.tuple_node_length(t)
    if length != 3:
        return parse_error(parser, u"Expected tuple of 3 elements", node)

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


def stmt_infixl(parser, op, node):
    return _meta_infix(parser, node, led_infix_function)


def stmt_infixr(parser, op, node):
    return _meta_infix(parser, node, led_infixr_function)


def _meta_infix(parser, node, infix_function):
    t = expect_expression_of(parser.name_tuple_parser, 0, NT_TUPLE)
    children = nodes.node_first(t)

    length = nodes.tuple_node_length(t)
    if length != 3:
        return parse_error(parser, u"Expected tuple of 3 elements", node)

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

# # TRAIT
#
#
#
# def grab_name(parser):
#     check_token_type(parser, TT_NAME)
#     name = _init_default_current_0(parser)
#     advance(parser)
#     return name
#
#
# def _parser_trait_header(parser, node):
#     name = expect_expression_of(parser.name_parser, 0, NT_NAME)
#
#     signature = _parse_comma_separated(parser.name_parser, TT_RSQUARE, [NT_NAME], advance_first=TT_LSQUARE)
#
#     constraints = nodes.create_empty_list_node(node)
#     return name, signature, constraints
#
#
# def __signature_has_type(signature, type):
#     type_name = nodes.node_value(type)
#     for node in signature:
#         nval = nodes.node_value(node)
#         if api.equal_b(nval, type_name):
#             return True
#     return False
#
#
# def _process_trait_signature(parser, node, signature):
#     result = [nodes.create_symbol_node(node, node) for node in signature]
#     return nodes.create_list_node(node, result)
#
#
# def _process_trait_methods(parser, signature, methods):
#     new_methods = []
#     for method in methods:
#         method_name = nodes.node_first(method)
#         method_signature = nodes.list_node_items(nodes.node_second(method))
#         method_body = nodes.node_third(method)
#
#         find = False
#         new_signature = []
#         for _type in method_signature:
#             if __signature_has_type(signature, _type):
#                 find = True
#                 new_signature.append(nodes.create_symbol_node(_type, _type))
#             else:
#                 new_signature.append(_type)
#
#         if not find:
#             return parse_error(parser, u"None of the trait types used in method", method)
#         else:
#             new_method = node_3(NT_DEF, __ntok(method),
#                                 method_name,
#                                 nodes.create_list_node(method, new_signature), method_body)
#             new_methods.append(new_method)
#
#     return list_node(new_methods)
#
#
# def stmt_trait(parser, op, node):
#     name, signature, constraints = _parser_trait_header(parser, node)
#     check_token_type(parser, TT_LPAREN)
#     methods = list_expression(parser.trait_parser, 0)
#
#     new_methods = _process_trait_methods(parser, signature, methods)
#     new_signature = _process_trait_signature(parser, node, signature)
#
#     return nodes.node_4(NT_TRAIT, __ntok(node), name,
#                         new_signature,
#                         constraints, new_methods)
#
#
# def prefix_trait_def(parser, op, node):
#     return _parse_def(parser, node)
#
#
# # USE
#
# def stmt_use(parser, op, node):
#     if parser.token_type == TT_LPAREN:
#         exported_items = _parse_comma_separated(parser.name_parser, TT_RPAREN,
#                                                 advance_first=TT_LPAREN,
#                                                 not_empty=True)
#         advance_expected(parser, TT_FROM)
#     else:
#         exported_items = list_node([])
#
#     exported = nodes.create_list_node_from_list(node, exported_items)
#
#     name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
#     types = _parse_comma_separated(parser.name_parser, TT_RSQUARE, advance_first=TT_LSQUARE, not_empty=True)
#     signature = nodes.create_list_node_from_list(node, types)
#     return node_3(NT_USE, __ntok(node), name, exported, signature)



# def _parse_def(parser, node, skip_signature=False):
#     func_name = expect_expression_of_types(parser.name_parser, 0, NAME_NODES)
#     if nodes.node_type(func_name) == NT_IMPORTED_NAME:
#         pass
#
#     signature = _parse_def_signature(parser, node, skip_signature)
#     method = _parse_def_body(parser, node)
#
#     return node_3(NT_DEF, __ntok(node), func_name, signature, method)


# def _parse_def_signature(parser, node, skip):
#     items = _parse_comma_separated(parser.name_parser, TT_RSQUARE, expected=NAME_NODES, advance_first=TT_LSQUARE)
#     signature = nodes.create_list_node_from_list(node, items)
#     return signature
#
#
# def _parse_def_body(parser, node):
#     if parser.token_type == TT_AS:
#         advance_expected(parser, TT_AS)
#         method = expression(parser.expression_parser, 0)
#     else:
#         funcs = _parse_case_or_simple_function(parser.expression_parser,
#                                                TERM_FUN_PATTERN, TERM_FUN_GUARD)
#         # TODO create fancy name <generic_name SIGNATURE>
#         method = node_2(NT_FUN, __ntok(node), empty_node(), funcs)
#     return method



# if len(dispatch) == 0:
#     for arg in sig_args:
#         _subject = nodes.node_first(arg)
#         if nodes.is_empty_node(_subject):
#             continue
#         if nodes.node_type(_subject) not in [NT_NAME, NT_IMPORTED_NAME, NT_WILDCARD]:
#             parse_error(parser, u"Expected one or more dispatch specification", _subject)
#
#     if parser.token_type == TT_ASSIGN or parser.token_type == TT_CASE:
#         parse_error(parser, u"Generic function declaration can't have body", node)
