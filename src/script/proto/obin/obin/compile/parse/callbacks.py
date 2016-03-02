from obin.compile.parse.basic import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes, tokens
from obin.compile.parse.nodes import (node_token as __ntok, node_0, node_1, node_2, node_3)
from obin.types import space
from obin.misc import strutil

NODE_TYPE_MAPPING = {
    TT_DOT: NT_LOOKUP_SYMBOL,
    TT_COLON: NT_LOOKUP_MODULE,
    TT_TRUE: NT_TRUE,
    TT_FALSE: NT_FALSE,
    TT_NIL: NT_NIL,
    TT_INT: NT_INT,
    TT_FLOAT: NT_FLOAT,
    TT_STR: NT_STR,
    TT_CHAR: NT_CHAR,
    TT_WILDCARD: NT_WILDCARD,
    TT_NAME: NT_NAME,
    TT_TYPENAME: NT_NAME,
    TT_IF: NT_CONDITION,
    TT_WHEN: NT_TERNARY_CONDITION,
    TT_MATCH: NT_MATCH,
    TT_EXPORT: NT_EXPORT,
    TT_IMPORT: NT_IMPORT,
    TT_TRAIT: NT_TRAIT,
    TT_GENERIC: NT_GENERIC,
    TT_SPECIFY: NT_SPECIFY,
    TT_THROW: NT_THROW,
    TT_BREAK: NT_BREAK,
    TT_CONTINUE: NT_CONTINUE,
    TT_FOR: NT_FOR,
    TT_WHILE: NT_WHILE,
    TT_ELLIPSIS: NT_REST,
    TT_ASSIGN: NT_ASSIGN,
    TT_OF: NT_OF,
    TT_AS: NT_AS,
    TT_AND: NT_AND,
    TT_OR: NT_OR,
    TT_DOUBLE_DOT: NT_RANGE,
    TT_SHARP: NT_SYMBOL,
    TT_OPERATOR: NT_NAME,
    TT_COMMA: NT_COMMA,
}


def node_tuple_juxtaposition(parser, terminators):
    node, args = juxtaposition_list(parser, terminators)
    return nodes.node_1(NT_TUPLE, nodes.node_token(node), nodes.list_node(args))


def node_list_juxtaposition(parser, terminators):
    node, args = juxtaposition_list(parser, terminators)
    return nodes.node_1(NT_LIST, nodes.node_token(node), nodes.list_node(args))


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
    exp = expressions(parser, op.lbp)
    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr(parser, op, node, left):
    exp = expressions(parser, op.lbp - 1)
    return node_2(__ntype(node), __ntok(node), left, exp)


def prefix_nud_function(parser, op, node):
    exp = literal_expression(parser)
    return nodes.create_call_node_name(node, op.prefix_function, [exp])


def led_infix_function(parser, op, node, left):
    exp = expressions(parser, op.lbp)
    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def led_infixr_function(parser, op, node, left):
    exp = expressions(parser, op.lbp - 1)
    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def led_infixr_assign(parser, op, node, left):
    ltype = nodes.node_token_type(left)

    if ltype != TT_DOT and ltype != TT_LSQUARE \
            and ltype != TT_NAME and ltype != TT_LCURLY and ltype != TT_LPAREN:
        parse_error(parser, u"Bad lvalue in assignment", left)

    if ltype == TT_LPAREN and nodes.node_arity(left) != 1:
        parse_error(parser, u"Bad lvalue in assignment, wrong tuple destructuring", left)

    if ltype == TT_LCURLY and nodes.node_arity(left) == 0:
        parse_error(parser, u"Bad lvalue in assignment, empty map", left)

    exp = expressions(parser, 9)

    return node_2(__ntype(node), __ntok(node), left, exp)


def infix_backtick(parser, op, node, left):
    funcname = strutil.cat_both_ends(nodes.node_value_s(node))
    if not funcname:
        return parse_error(parser, u"invalid variable name in backtick expression", node)
    funcnode = nodes.create_name_node(node, funcname)

    right = expressions(parser, op.lbp)
    return nodes.create_call_node_2(node, funcnode, left, right)


def infix_if(parser, op, node, left):
    first = condition(parser)
    advance_expected(parser, TT_ELSE)
    exp = expressions(parser, 0)
    return node_3(NT_TERNARY_CONDITION, __ntok(node), first, left, exp)


def infix_dot(parser, op, node, left):
    check_token_type(parser, TT_NAME)
    symbol = _init_default_current_0(parser)
    advance(parser)
    return node_2(NT_LOOKUP_SYMBOL, __ntok(node), left, symbol)


def infix_lcurly(parser, op, node, left):
    items = []
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_SHARP, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expressions(parser, 10)

            advance_expected(parser, TT_ASSIGN)
            value = expressions(parser, 0)

            items.append(nodes.list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return node_2(NT_MODIFY, __ntok(node), left, nodes.list_node(items))


def infix_lsquare(parser, op, node, left):
    exp = expressions(parser, 0)
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

    exp = expressions(parser, 9)
    return node_2(NT_BIND, __ntok(node), left, exp)


##############################################################
# INFIX
##############################################################


def prefix_nud(parser, op, node):
    exp = literal_expression(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def itself(parser, op, node):
    return node_0(__ntype(node), __ntok(node))


def _parse_name(parser):
    if parser.token_type == TT_SHARP:
        node = parser.node
        advance(parser)
        return _parse_symbol(parser, node)

    check_token_types(parser, [TT_STR, TT_NAME])
    node = parser.node
    advance(parser)
    return node_0(__ntype(node), __ntok(node))


def _parse_symbol(parser, node):
    check_token_types(parser, [TT_NAME, TT_STR, TT_OPERATOR])
    exp = node_0(__ntype(parser.node), __ntok(parser.node))
    advance(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def prefix_sharp(parser, op, node):
    return _parse_symbol(parser, node)


# def prefix_backtick(parser, op, node):
#     val = strutil.cat_both_ends(nodes.node_value_s(node))
#     if not val:
#         return parse_error(parser, u"invalid variable name", node)
#     return nodes.create_name_node(node, val)



# def prefix_sharp(parser, op, node):
#     check_token_types(parser, [TT_NAME, TT_STR, TT_OPERATOR])
#     if parser.token_type == TT_OPERATOR:
#         exp = node_0(NT_NAME, __ntok(parser.node))
#         advance(parser)
#     else:
#         exp = literal_expression(parser)
#         check_node_types(parser, exp, [NT_NAME, NT_STR])
#
#     return node_1(__ntype(node), __ntok(node), exp)


def symbol_wildcard(parser, op, node):
    return parse_error(parser, u"Invalid use of _ pattern", node)


def prefix_condition(parser, op, node):
    branches = []
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)

        if parser.token_type == TT_OTHERWISE:
            break

        cond = condition_terminated_expression(parser, TERM_CONDITION_CONDITION)
        body = statements(parser, TERM_CONDITION_BODY)
        check_token_types(parser, TERM_CONDITION_BODY)
        branches.append(nodes.list_node([cond, body]))

    advance_expected(parser, TT_OTHERWISE)
    advance_expected(parser, TT_ARROW)
    body = statements(parser, TERM_BLOCK)
    branches.append(nodes.list_node([nodes.empty_node(), body]))
    advance_end(parser)
    return node_1(NT_CONDITION, __ntok(node), nodes.list_node(branches))


# def prefix_if(parser, op, node):
#     branches = []
#     cond = condition_terminated_expression(parser, TERM_IF_CONDITION)
#     ifbody = expressions(parser, 0, TERM_IF_BODY)
#
#     branches.append(nodes.list_node([cond, ifbody]))
#     check_token_types(parser, TERM_IF_BODY)
#
#     advance_expected(parser, TT_ELSE)
#     elsebody = expressions(parser, 0)
#
#     branches.append(nodes.list_node([nodes.empty_node(), elsebody]))
#     return node_1(NT_CONDITION, __ntok(node), nodes.list_node(branches))


# separate lparen handle for match case declarations
def prefix_lparen_tuple(parser, op, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

    items = []
    while True:
        exp = expressions(parser, 0)
        items.append(exp)
        if parser.token_type != TT_COMMA:
            break

        advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), nodes.list_node(items))


def prefix_lparen(parser, op, node):
    if parser.token_type == TT_OPERATOR:
        name = _init_default_current_0(parser)
        op = nodes.create_name_from_operator(node, name)
        advance(parser)
        if parser.token_type != TT_RPAREN:
            parse_error(parser, u"Invalid syntax for operator in prefix mode, use (op)", node)

        advance_expected(parser, TT_RPAREN)
        return op

    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

    e = expressions(parser, 0)

    if parser.token_type != TT_COMMA:
        advance_expected(parser, TT_RPAREN)
        return process_juxtaposition_expression(parser, e)

    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expressions(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), nodes.list_node(items))


def prefix_lsquare(parser, op, node):
    items = []
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expressions(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RSQUARE)
    return node_1(NT_LIST, __ntok(node), nodes.list_node(items))


def on_bind_node(parser, key):
    if nodes.node_type(key) != NT_NAME:
        parse_error(parser, u"Invalid bind name", key)

    advance_expected(parser, TT_AT_SIGN)
    real_key, value = _parse_map_key_pair(parser, [TT_NAME, TT_SHARP, TT_STR], None)

    # allow syntax like {var1@ key}
    if nodes.node_type(real_key) == NT_NAME:
        real_key = nodes.create_symbol_node(real_key, real_key)

    bind_key = nodes.create_bind_node(key, key, real_key)
    return bind_key, value


# this callback used in pattern matching
def prefix_lcurly_patterns(parser, op, node):
    return _prefix_lcurly(parser, op, node, [TT_NAME, TT_SHARP, TT_STR], on_bind_node)


def prefix_lcurly(parser, op, node):
    return _prefix_lcurly(parser, op, node, [TT_NAME, TT_SHARP, TT_INT, TT_STR, TT_CHAR, TT_FLOAT], None)


def _parse_map_key_pair(parser, types, on_unknown):
    check_token_types(parser, types)
    # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
    key = expressions(parser, 10)

    if parser.token_type == TT_COMMA:
        value = nodes.empty_node()
    elif parser.token_type == TT_RCURLY:
        value = nodes.empty_node()
    elif parser.token_type == TT_ASSIGN:
        advance_expected(parser, TT_ASSIGN)
        value = expressions(parser, 0)
    else:
        if on_unknown is None:
            parse_error(parser, u"Invalid map declaration syntax", parser.node)
        key, value = on_unknown(parser, key)

    return key, value


def _prefix_lcurly(parser, op, node, types, on_unknown):
    # on_unknown used for pattern_match in binds {NAME @ name = "Alice"}
    items = []
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            key, value = _parse_map_key_pair(parser, types, on_unknown)
            items.append(nodes.list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return node_1(NT_MAP, __ntok(node), nodes.list_node(items))


def prefix_try(parser, op, node):
    # endofexpression(parser)
    trybody = statements(parser, TERM_TRY)
    catches = []
    check_token_type(parser, TT_CASE)
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)

        if parser.token_type == TT_FINALLY:
            break
        # pattern = expressions(parser.pattern_parser, 0)
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, TERM_CASE)
        catches.append(nodes.list_node([pattern, body]))

    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        advance_expected(parser, TT_ARROW)
        finallybody = statements(parser, TERM_BLOCK)
    else:
        finallybody = nodes.empty_node()

    advance_end(parser)
    return node_3(NT_TRY, __ntok(node), trybody, nodes.list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expressions(parser.pattern_parser, 0, TERM_PATTERN)
    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, TERM_FUN_GUARD)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def prefix_match(parser, op, node):
    exp = expression(parser, 0)
    pattern_parser = parser.pattern_parser
    branches = []
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, TERM_CASE)

        branches.append(nodes.list_node([pattern, body]))

    advance_end(parser)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    return node_2(NT_MATCH, __ntok(node), exp, nodes.list_node(branches))


def stmt_single(parser, op, node):
    exp = expressions(parser, 0)
    endofexpression(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def stmt_loop_flow(parser, op, node):
    endofexpression(parser)
    if parser.token_type not in LOOP_CONTROL_TOKENS:
        parse_error(parser, u"Unreachable statement", node)
    return node_0(__ntype(node), __ntok(node))


def stmt_when(parser, op, node):
    cond = condition_expression(parser)
    body = statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_2(NT_WHEN, __ntok(node), cond, body)


def stmt_for(parser, op, node):
    check_token_type(parser, TT_NAME)
    var = _init_default_current_0(parser)
    vars = nodes.list_node([var])
    advance(parser)
    advance_expected(parser, TT_BACKARROW)
    exp = expressions(parser, 0)
    # CALL endofexpression for one line for i <- 1..2; i end
    endofexpression(parser)

    stmts = statements(parser, TERM_BLOCK)

    advance_end(parser)
    return node_3(NT_FOR, __ntok(node), vars, exp, stmts)


def _parse_func_pattern(parser, arg_terminator, guard_terminator):
    pattern = node_tuple_juxtaposition(parser.pattern_parser, arg_terminator)
    args_type = nodes.node_type(pattern)

    if args_type != NT_TUPLE:
        parse_error(parser, u"Invalid  syntax in function arguments", pattern)

    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expression(parser.guard_parser, 0, guard_terminator)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def parse_function_variants(parser):
    funcs = []

    if parser.token_type == TT_CASE:
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            args = _parse_func_pattern(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD)
            advance_expected(parser, TT_ARROW)
            body = statements(parser, TERM_CASE)
            funcs.append(nodes.list_node([args, body]))
    else:
        if parser.token_type == TT_ARROW:
            return parse_error(parser, u"Empty function arguments pattern", parser.node)
            # args = nodes.create_unit_node(parser.node)
        else:
            args = _parse_func_pattern(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD)

        advance_expected(parser, TT_ARROW)
        body = statements(parser, TERM_BLOCK)
        funcs.append(nodes.list_node([args, body]))
    return nodes.list_node(funcs)


def parse_function(parser, allow_empty_name):
    if parser.token_type == TT_CASE:
        if allow_empty_name:
            name = nodes.empty_node()
        else:
            return parse_error(parser, u"Expected function name", parser.node)
    else:
        name = expect_expression(parser.name_parser, 0, NODE_FUNC_NAME,
                                 terminators=TERM_FUN_GUARD, error_on_juxtaposition=False)

    funcs = parse_function_variants(parser)
    advance_end(parser)
    return name, funcs


def prefix_lambda(parser, op, node):
    name = nodes.empty_node()
    if parser.token_type == TT_ARROW:
        return parse_error(parser, u"Empty function arguments pattern", parser.node)
    else:
        args = _parse_func_pattern(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD)

    advance_expected(parser, TT_ARROW)
    # body = statements(parser, TERM_BLOCK)
    body = nodes.list_node([expressions(parser, 0, terminators=None)])
    if isendofexpressiontoken(parser):
        endofexpression(parser)

    # advance_end(parser)
    return node_2(
        NT_FUN, __ntok(node), name, nodes.list_node([nodes.list_node([args, body])]))


def prefix_fun(parser, op, node):
    name, funcs = parse_function(parser, True)
    return node_2(NT_FUN, __ntok(node), name, funcs)


def prefix_module_fun(parser, op, node):
    name, funcs = parse_function(parser.expression_parser, False)
    return node_2(NT_FUN, __ntok(node), name, funcs)


###############################################################
# MODULE STATEMENTS
###############################################################

def parse_specify_fn(parser):
    _expression_parser = parser.expression_parser
    _signature_parser = parser.generic_signature_parser

    signature = node_tuple_juxtaposition(_signature_parser, TERM_FUN_GUARD)

    # if nodes.node_type(pattern) != NT_TUPLE:
    #     parse_error(parser, u"Invalid  syntax in specify function arguments", pattern)

    advance_expected(_expression_parser, TT_ARROW)
    body = statements(_expression_parser, TERM_CASE)
    return nodes.list_node([nodes.node_first(signature), body])


def parse_specify_funcs(parser):
    funcs = []
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)
        func = parse_specify_fn(parser)
        funcs.append(func)

    advance_end(parser)

    if len(funcs) == 0:
        parse_error(parser, u"Empty specify statement", parser.node)

    return nodes.list_node(funcs)


def generic_name(parser):
    return expect_expression(parser.name_parser, 0, NODE_SPECIFY_NAME, terminators=TERM_CASE,
                             error_on_juxtaposition=False)


def stmt_specify(parser, op, node):
    # name = closed_expression(parser.name_parser, 0)
    name = generic_name(parser)
    # name = terminated_expression(parser.name_parser, 0, [TT_CASE])
    # check_node_types(parser, name, [NT_NAME, NT_LOOKUP_MODULE])

    check_token_types(parser, [TT_CASE])
    # name = _parse_name(parser)
    # check_node_types(parser, name, [NT_SYMBOL, NT_NAME])

    funcs = parse_specify_funcs(parser)
    return node_2(NT_SPECIFY, __ntok(node), name, funcs)


def stmt_generic(parser, op, node):
    # name = literal_expression(parser.name_parser)
    # name = _parse_name(parser)
    # name = terminated_expression(parser.name_parser, 0, [TT_CASE, TT_LPAREN])
    name = generic_name(parser)

    if parser.token_type == TT_CASE:
        funcs = parse_specify_funcs(parser)
        return node_2(NT_GENERIC, __ntok(node), name, funcs)
    else:
        return node_1(NT_GENERIC, __ntok(node), name)


def stmt_module(parser, op, node):
    name = literal_terminated_expression(parser)
    check_node_type(parser, name, NT_NAME)
    stmts, scope = parse_env_statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_3(NT_MODULE, __ntok(node), name, stmts, scope)


def _load_path_s(node):
    if nodes.node_type(node) == NT_LOOKUP_MODULE:
        return _load_path_s(nodes.node_first(node)) + ':' + nodes.node_value_s(nodes.node_second(node))
    else:
        return nodes.node_value_s(node)


def _load_module(parser, exp):
    from obin.runtime import load

    if nodes.node_type(exp) == NT_AS:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(nodes.node_first(exp))
    elif nodes.node_type(exp) == NT_LOOKUP_MODULE:
        import_name = nodes.node_second(exp)
        module_path = _load_path_s(exp)
    else:
        assert nodes.node_type(exp) == NT_NAME
        import_name = exp
        module_path = nodes.node_value_s(exp)

    state = parser.close()
    module = load.import_module(state.process, space.newsymbol_s(state.process, module_path))
    parser.open(state)


def stmt_import(parser, op, node):
    if parser.token_type == TT_FROM:
        ntype1 = NT_IMPORT_FROM
        advance(parser)
    else:
        ntype1 = NT_IMPORT

    imported = expression(parser.import_parser, 0, [TT_LPAREN, TT_HIDING])
    if parser.token_type == TT_HIDING:
        hiding = True
        if ntype1 == NT_IMPORT:
            ntype = NT_IMPORT_HIDING
        else:
            ntype = NT_IMPORT_FROM_HIDING
        advance(parser)
    else:
        hiding = False
        ntype = ntype1

    if parser.token_type == TT_LPAREN:
        names = expressions(parser.import_names_parser, 0)
        check_node_type(parser, names, NT_TUPLE)
        if hiding is True:
            # hiding names can't have as binding
            check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    else:
        if hiding is True:
            parse_error(parser, u"expected definitions tuple", node)
        names = nodes.empty_node()

    # _load_module(parser, imported)
    return node_2(ntype, __ntok(node), imported, names)


def stmt_export(parser, op, node):
    check_token_type(parser, TT_LPAREN)
    names = expressions(parser.import_names_parser, 0)
    check_node_type(parser, names, NT_TUPLE)
    check_list_node_types(parser, nodes.node_first(names), [NT_NAME])
    return node_1(NT_EXPORT, __ntok(node), names)


def symbol_or_name_value(parser, name):
    if nodes.node_type(name) == NT_SYMBOL:
        data = nodes.node_first(name)
        if nodes.node_type(data) == NT_NAME:
            return nodes.node_value(data)
        elif nodes.node_type(data) == NT_STR:
            return strutil.unquote_w(nodes.node_value(data))
        else:
            assert False, "Invalid symbol"
    elif nodes.node_type(name) == NT_NAME:
        return nodes.node_value(name)
    else:
        assert False, "Invalid name"


def stmt_module_at(parser, op, node):
    """
    @infixl(#+, ___add, 10)
    @infixr(#::, ___cons, 10)
    @prefix(#+, ___unary_plus)
    """
    check_token_type(parser, TT_NAME)
    type_node = parser.node
    advance(parser)
    if nodes.node_value_s(type_node) == "prefix":
        return _meta_prefix(parser, node)
    elif nodes.node_value_s(type_node) == "infixl":
        return _meta_infix(parser, node, led_infix_function)
    elif nodes.node_value_s(type_node) == "infixr":
        return _meta_infix(parser, node, led_infixr_function)
    else:
        return parse_error(parser, u"Invalid operator type expected infixl, infixr or prefix", parser.node)


# TYPES ************************

def _parse_construct(parser, node):
    funcs = []
    check_token_type(parser, TT_CASE)
    fenv_node = nodes.create_fenv_node(node)
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)
        args = _parse_func_pattern(parser, TERM_CONSTRUCT_PATTERN, TERM_CONSTRUCT_GUARD)
        if parser.token_type == TT_ARROW:
            advance_expected(parser, TT_ARROW)
            body = statements(parser, TERM_CASE)
            body = plist.append(body, fenv_node)
        elif parser.token_type == TT_CASE or parser.token_type == TT_END:
            body = nodes.list_node([fenv_node])
        else:
            return parse_error(parser, u"Invalid construct syntax", parser.node)

        funcs.append(nodes.list_node([args, body]))
    advance_end(parser)

    return nodes.list_node(funcs)


def literal_type_field(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_symbol_node(name, name)


def symbol_list_to_arg_tuple(parser, node, symbols):
    args = []
    children = nodes.node_first(symbols)
    for child in children:
        assert nodes.node_type(child) == NT_SYMBOL
        name = nodes.node_first(child)
        args.append(name)

    return nodes.node_1(NT_TUPLE, nodes.node_token(node), nodes.list_node(args))


# TODO BETTER PARSE ERRORS HERE
def stmt_type(parser, op, node):
    type_parser = parser.type_parser
    check_token_type(type_parser, TT_NAME)
    typename = _init_default_current_0(type_parser)
    advance(type_parser)

    if parser.token_type == TT_END:
        fields = nodes.empty_node()
        construct_funcs = nodes.empty_node()
    else:
        fields = node_list_juxtaposition(type_parser, TERM_TYPE_ARGS)
        if parser.token_type == TT_CONSTRUCT:
            advance(parser)
            construct_funcs = _parse_construct(parser.expression_parser, node)
        else:
            # default constructor
            args = symbol_list_to_arg_tuple(parser, node, fields)
            body = nodes.list_node([nodes.create_fenv_node(node)])
            construct_funcs = nodes.list_node([nodes.list_node([args, body])])

    advance_end(parser)
    return nodes.node_3(NT_TYPE, __ntok(node), typename, fields, construct_funcs)


# TRAIT
def symbol_operator_name(parser, op, node):
    name = itself(parser, op, node)
    return nodes.create_name_from_operator(node, name)


def grab_name(parser):
    check_token_type(parser, TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)
    return name

def grab_name_or_operator(parser):
    check_token_types(parser, [TT_NAME, TT_OPERATOR])
    name = _init_default_current_0(parser)
    if parser.token_type == TT_OPERATOR:
        name = nodes.create_name_from_operator(name, name)
    advance(parser)
    return name


def stmt_trait(parser, op, node):
    type_parser = parser.type_parser
    sig_parser = parser.method_signature_parser
    name = grab_name(type_parser)
    instance_name = grab_name(type_parser)
    methods = []
    while parser.token_type == TT_METHOD:
        advance_expected(parser, TT_METHOD)
        method_name = grab_name_or_operator(parser)
        check_token_type(parser, TT_NAME)

        sig = node_list_juxtaposition(sig_parser, TERM_METHOD_SIG)
        check_node_type(parser, sig, NT_LIST)

        methods.append(nodes.list_node([method_name, sig]))
    advance_end(parser)
    return nodes.node_3(NT_TRAIT, __ntok(node), name, instance_name, nodes.list_node(methods))


def stmt_implement(parser, op, node):
    type_parser = parser.type_parser
    trait_name = grab_name(type_parser)
    advance_expected(parser, TT_FOR)
    type_name = grab_name(type_parser)

    methods = []

    check_token_type(parser, TT_METHOD)
    while parser.token_type == TT_METHOD:
        advance_expected(parser, TT_METHOD)

        funcs = []
        method_name = grab_name_or_operator(parser.name_parser)
        check_token_type(parser, TT_CASE)
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            args = _parse_func_pattern(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD)
            advance_expected(parser, TT_ARROW)
            body = statements(parser.expression_parser, TERM_IMPL_BODY)
            funcs.append(nodes.list_node([args, body]))
        methods.append(nodes.list_node([method_name, nodes.list_node(funcs)]))

    advance_end(parser)
    return nodes.node_3(NT_IMPLEMENT, __ntok(node), trait_name, type_name, nodes.list_node(methods))

def _meta_infix(parser, node, infix_function):
    # options_tuple = expressions(parser.name_parser, 0)
    # check_node_type(parser, options_tuple, NT_TUPLE)
    _, options = juxtaposition_list_while_not_breaks(parser.name_parser)
    # options = nodes.node_first(options_tuple)
    if api.length_i(options) != 3:
        return parse_error(parser, u"Invalid prefix operator options", parser.node)
    op_node = options[0]
    func_node = options[1]
    precedence_node = options[2]
    check_node_type(parser, op_node, NT_NAME)
    check_node_types(parser, func_node, [NT_NAME, NT_SYMBOL])
    check_node_type(parser, precedence_node, NT_INT)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)
    try:
        precedence = strutil.string_to_int(nodes.node_value_s(precedence_node))
    except:
        return parse_error(parser, u"Invalid infix operator precedence", precedence_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_infix(op, precedence, infix_function, func_value)
    endofexpression(parser)
    parser_current_scope_add_operator(parser, op_value, op)


def _meta_prefix(parser, node):
    # options_tuple = expressions(parser.name_parser, 0)
    # check_node_type(parser, options_tuple, NT_TUPLE)
    # options = nodes.node_first(options_tuple)
    _, options = juxtaposition_list_while_not_breaks(parser.name_parser)
    if api.length_i(options) != 2:
        return parse_error(parser, u"Invalid prefix operator options", parser.node)
    op_node = options[0]
    func_node = options[1]
    check_node_type(parser, op_node, NT_NAME)
    check_node_types(parser, func_node, [NT_NAME, NT_SYMBOL])

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_prefix(op, prefix_nud_function, func_value)

    endofexpression(parser)
    parser_current_scope_add_operator(parser, op_value, op)
