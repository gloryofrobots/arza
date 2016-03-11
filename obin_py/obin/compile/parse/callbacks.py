from obin.compile.parse.basic import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes, tokens
from obin.compile.parse.nodes import (node_token as __ntok, node_0, node_1, node_2, node_3, list_node, empty_node)
from obin.types import space
from obin.misc import strutil

NODE_TYPE_MAPPING = {
    TT_DOT: NT_LOOKUP_SYMBOL,
    TT_COLON: NT_LOOKUP_MODULE,
    TT_TRUE: NT_TRUE,
    TT_FALSE: NT_FALSE,
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


def node_tuple_juxtaposition(parser, terminators, skip=None):
    node, args = juxtaposition_list(parser, terminators, skip)
    # return nodes.node_1(NT_TUPLE, nodes.node_token(node), list_node(args))
    return nodes.create_tuple_node(node, args)


def node_list_juxtaposition(parser, terminators, skip=None):
    node, args = juxtaposition_list(parser, terminators, skip)
    return nodes.create_list_node(node, args)


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
    ntype = nodes.node_type(left)
    if ntype == NT_LOOKUP or ntype == NT_LOOKUP_SYMBOL:
        parse_error(parser, u"Bad left value in assignment expression, use operator .{} "
                            u"for creating new data structures", left)

    # ltype = nodes.node_token_type(left)

    # if ltype != TT_DOT and ltype != TT_LSQUARE \
    #         and ltype != TT_NAME and ltype != TT_LCURLY and ltype != TT_LPAREN:
    #     parse_error(parser, u"Bad lvalue in assignment", left)
    #
    # if ltype == TT_LPAREN and nodes.node_arity(left) != 1:
    #     parse_error(parser, u"Bad lvalue in assignment, wrong tuple destructuring", left)
    #
    # if ltype == TT_LCURLY and nodes.node_arity(left) == 0:
    #     parse_error(parser, u"Bad lvalue in assignment, empty map", left)

    exp = expressions(parser, 9)

    return node_2(__ntype(node), __ntok(node), left, exp)


def infix_backtick(parser, op, node, left):
    funcname = strutil.cat_both_ends(nodes.node_value_s(node))
    if not funcname:
        return parse_error(parser, u"invalid variable name in backtick expression", node)
    funcnode = nodes.create_name_node(node, funcname)

    right = expressions(parser, op.lbp)
    return nodes.create_call_node_2(node, funcnode, left, right)


def infix_juxtaposition(parser, op, node, left):
    right, _ = base_expression(parser, op.lbp)
    # right = expressions(parser, op.lbp)
    return nodes.node_2(NT_JUXTAPOSITION, __ntok(node), left, right)


def infix_if(parser, op, node, left):
    first = condition(parser)
    advance_expected(parser, TT_ELSE)
    exp = expressions(parser, 0)
    return node_3(NT_TERNARY_CONDITION, __ntok(node), first, left, exp)


def infix_dot(parser, op, node, left):
    if parser.token_type == TT_INT:
        idx = _init_default_current_0(parser)
        advance(parser)
        return node_2(NT_LOOKUP, __ntok(node), left, idx)

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

            items.append(list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return node_2(NT_MODIFY, __ntok(node), left, list_node(items))


def infix_lparen(parser, op, node, left):
    exp = expressions(parser, 0)
    advance_expected(parser, TT_RPAREN)
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


def prefix_amp(parser, op, node):
    return grab_name_or_operator(parser)


# def prefix_backtick(parser, op, node):
#     val = strutil.cat_both_ends(nodes.node_value_s(node))
#     if not val:
#         return parse_error(parser, u"invalid variable name", node)
#     return nodes.create_name_node(node, val)


def symbol_wildcard(parser, op, node):
    return parse_error(parser, u"Invalid use of _ pattern", node)


def prefix_condition(parser, op, node):
    branches = []
    while parser.token_type == TT_CASE:
        advance_expected(parser, TT_CASE)

        if parser.token_type == TT_ELSE:
            break

        cond = condition_terminated_expression(parser, TERM_CONDITION_CONDITION)
        body = statements(parser, TERM_CONDITION_BODY)
        check_token_types(parser, TERM_CONDITION_BODY)
        branches.append(list_node([cond, body]))

    advance_expected(parser, TT_ELSE)
    advance_expected(parser, TT_ARROW)
    body = statements(parser, TERM_BLOCK)
    branches.append(list_node([empty_node(), body]))
    advance_end(parser)
    return node_1(NT_CONDITION, __ntok(node), list_node(branches))


# def prefix_if(parser, op, node):
#     branches = []
#     cond = condition_terminated_expression(parser, TERM_IF_CONDITION)
#     ifbody = expressions(parser, 0, TERM_IF_BODY)
#
#     branches.append(list_node([cond, ifbody]))
#     check_token_types(parser, TERM_IF_BODY)
#
#     advance_expected(parser, TT_ELSE)
#     elsebody = expressions(parser, 0)
#
#     branches.append(list_node([empty_node(), elsebody]))
#     return node_1(NT_CONDITION, __ntok(node), list_node(branches))


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
    return node_1(NT_TUPLE, __ntok(node), list_node(items))


# MOST complicated operator
# expressions (f 1 2 3) (2 + 3) (-1)
# tuples (1,2,3,4,5)
def prefix_lparen(parser, op, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

    e = expressions(parser, 0, [TT_RPAREN])

    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return e

    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expressions(parser, 0, [TT_COMMA]))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), list_node(items))


def prefix_lsquare(parser, op, node):
    items = []
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expressions(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RSQUARE)
    return node_1(NT_LIST, __ntok(node), list_node(items))


def on_bind_node(parser, key):
    if nodes.node_type(key) != NT_NAME:
        parse_error(parser, u"Invalid bind name", key)
    if parser.token_type == TT_OF:
        advance_expected(parser, TT_OF)
        check_token_type(parser, TT_NAME)
        typename = grab_name(parser)
        return nodes.create_of_node(key, key, typename), empty_node()

    advance_expected(parser, TT_AT_SIGN)
    real_key, value = _parse_map_key_pair(parser, [TT_NAME, TT_SHARP, TT_STR], None)

    # allow syntax like {var1@ key}
    if nodes.node_type(real_key) == NT_NAME:
        real_key = nodes.create_symbol_node(real_key, real_key)

    bind_key = nodes.create_bind_node(key, key, real_key)
    return bind_key, value


# this callback used in pattern matching
def prefix_lcurly_patterns(parser, op, node):
    return _prefix_lcurly(parser, op, node, [TT_NAME, TT_SHARP, TT_INT, TT_STR, TT_CHAR, TT_FLOAT], on_bind_node)


def prefix_lcurly(parser, op, node):
    return _prefix_lcurly(parser, op, node, [TT_NAME, TT_SHARP, TT_INT, TT_STR, TT_CHAR, TT_FLOAT], on_bind_node)


def _parse_map_key_pair(parser, types, on_unknown):
    check_token_types(parser, types)
    # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
    key = expressions(parser, 10)

    if parser.token_type == TT_COMMA:
        value = empty_node()
    elif parser.token_type == TT_RCURLY:
        value = empty_node()
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
            items.append(list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return node_1(NT_MAP, __ntok(node), list_node(items))


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
        catches.append(list_node([pattern, body]))

    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        advance_expected(parser, TT_ARROW)
        finallybody = statements(parser, TERM_BLOCK)
    else:
        finallybody = empty_node()

    advance_end(parser)
    return node_3(NT_TRY, __ntok(node), trybody, list_node(catches), finallybody)


def _parse_pattern(parser):
    pattern = expressions(parser.pattern_parser, 0, TERM_PATTERN)
    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expressions(parser.guard_parser, 0, TERM_FUN_GUARD)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def prefix_match(parser, op, node):
    exp = expressions(parser, 0)
    pattern_parser = parser.pattern_parser
    branches = []
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = _parse_pattern(parser)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, TERM_CASE)

        branches.append(list_node([pattern, body]))

    advance_end(parser)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    return node_2(NT_MATCH, __ntok(node), exp, list_node(branches))


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
    vars = list_node([var])
    advance(parser)
    advance_expected(parser, TT_BACKARROW)
    exp = expressions(parser, 0)
    # CALL endofexpression for one line for i <- 1..2; i end
    endofexpression(parser)

    stmts = statements(parser, TERM_BLOCK)

    advance_end(parser)
    return node_3(NT_FOR, __ntok(node), vars, exp, stmts)


def _parse_func_pattern(parser, arg_terminator, guard_terminator):
    pattern = node_tuple_juxtaposition(parser.pattern_parser, arg_terminator, [TT_JUXTAPOSITION])
    args_type = nodes.node_type(pattern)

    if args_type != NT_TUPLE:
        parse_error(parser, u"Invalid  syntax in function arguments", pattern)

    if parser.token_type == TT_WHEN:
        advance(parser)
        guard = expressions(parser.guard_parser, 0, guard_terminator)
        pattern = node_2(NT_WHEN, __ntok(guard), pattern, guard)

    return pattern


def parse_function_variants(parser, term_pattern, term_guard, term_case_body, term_single_body):
    funcs = []

    if parser.token_type == TT_CASE:
        while parser.token_type == TT_CASE:
            advance_expected(parser, TT_CASE)
            args = _parse_func_pattern(parser, term_pattern, term_guard)
            advance_expected(parser, TT_ARROW)
            body = statements(parser, term_case_body)
            funcs.append(list_node([args, body]))
    else:
        if parser.token_type == TT_ARROW:
            return parse_error(parser, u"Empty function arguments pattern", parser.node)
            # args = nodes.create_unit_node(parser.node)
        args = _parse_func_pattern(parser, term_pattern, term_guard)
        advance_expected(parser, TT_ARROW)
        body = statements(parser, term_single_body)
        funcs.append(list_node([args, body]))
    return list_node(funcs)


def parse_function(parser, allow_empty_name):
    if parser.token_type == TT_CASE:
        if allow_empty_name:
            name = empty_node()
        else:
            return parse_error(parser, u"Expected function name", parser.node)
    else:
        name = expect_expression_of(parser.name_parser, 0, NT_NAME, TERM_FUN_GUARD)

    funcs = parse_function_variants(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_CASE, TERM_BLOCK)
    advance_end(parser)
    return name, funcs


def prefix_lambda(parser, op, node):
    name = empty_node()
    if parser.token_type == TT_ARROW:
        return parse_error(parser, u"Empty function arguments pattern", parser.node)
    else:
        args = _parse_func_pattern(parser, TERM_FUN_PATTERN, TERM_FUN_GUARD)

    advance_expected(parser, TT_ARROW)
    # body = statements(parser, TERM_BLOCK)
    body = list_node([expressions(parser, 0, terminators=None)])
    if isendofexpressiontoken(parser):
        endofexpression(parser)

    # advance_end(parser)
    return node_2(
        NT_FUN, __ntok(node), name, list_node([list_node([args, body])]))


def prefix_fun(parser, op, node):
    name, funcs = parse_function(parser, True)
    return node_2(NT_FUN, __ntok(node), name, funcs)


def prefix_module_fun(parser, op, node):
    name, funcs = parse_function(parser.expression_parser, False)
    return node_2(NT_FUN, __ntok(node), name, funcs)


###############################################################
# MODULE STATEMENTS
###############################################################

def stmt_module(parser, op, node):
    name = expressions(parser.name_parser, 0)
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

    imported = expressions(parser.import_parser, 0, [TT_LPAREN, TT_HIDING])
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
        names = empty_node()

    _load_module(parser, imported)
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
            body = list_node([fenv_node])
        else:
            return parse_error(parser, u"Invalid construct syntax", parser.node)

        funcs.append(list_node([args, body]))
    advance_end(parser)

    return list_node(funcs)


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

    return nodes.node_1(NT_TUPLE, nodes.node_token(node), list_node(args))

def grab_name_or_tuple(parser, term):
    if parser.token_type == TT_NAME:
        return grab_name(parser)
    if parser.token_type != TT_LPAREN:
        parse_error(parser, u"Expected name or tuple of names", parser.node)

    exp = expressions(parser, 0, term)
    check_node_type(parser, exp, NT_TUPLE)
    check_list_node_types(parser, nodes.node_first(exp), [NT_NAME])
    return exp

def grab_name_or_tuple_as_tuple(parser, term):
    exp = grab_name_or_tuple(parser, term)
    if nodes.node_type(exp) == NT_NAME:
        return nodes.create_tuple_node(exp, [exp])
    return exp

def stmt_derive(parser, op, node):
    traits = grab_name_or_tuple_as_tuple(parser.name_parser, TERM_DERIVE)
    advance_expected(parser, TT_FOR)
    types = grab_name_or_tuple_as_tuple(parser.name_parser, None)
    return node_2(NT_DERIVE, __ntok(node), traits, types)

# TODO BETTER PARSE ERRORS HERE
def stmt_type(parser, op, node):
    typename = grab_name(parser.type_parser)
    if parser.token_type != TT_NAME:
        if parser.token_type == TT_END:
            advance_end(parser)
        return nodes.node_3(NT_TYPE, __ntok(node), typename, empty_node(), empty_node())

    if parser.token_type == TT_NAME:
        fields = node_list_juxtaposition(parser.type_parser, TERM_TYPE_ARGS)
        if parser.token_type == TT_CONSTRUCT:
            advance(parser)
            construct_funcs = _parse_construct(parser.expression_parser, node)
        else:
            # default constructor
            args = symbol_list_to_arg_tuple(parser, node, fields)
            body = list_node([nodes.create_fenv_node(node)])
            construct_funcs = nodes.create_function_variants(args, body)
    else:
        fields = empty_node()
        construct_funcs = empty_node()

    advance_end(parser)
    return nodes.node_3(NT_TYPE, __ntok(node), typename, fields, construct_funcs)


# TRAIT*************************
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
    check_token_type(parser, TT_FOR)
    advance(parser)
    instance_name = grab_name(type_parser)
    if parser.token_type == TT_OF:
        advance(parser)
        constraints = node_list_juxtaposition(parser.name_parser, TERM_METHOD_CONSTRAINTS)
    else:
        constraints = nodes.create_empty_list_node(node)

    methods = []
    while parser.token_type == TT_METHOD:
        advance_expected(parser, TT_METHOD)
        method_name = grab_name_or_operator(parser)
        check_token_type(parser, TT_NAME)

        sig = node_list_juxtaposition(sig_parser, TERM_METHOD_SIG)
        check_node_type(parser, sig, NT_LIST)
        if parser.token_type == TT_ARROW:
            advance(parser)
            args = symbol_list_to_arg_tuple(parser, node, sig)
            body = statements(parser.expression_parser, TERM_METHOD_DEFAULT_BODY)
            default_impl = nodes.create_function_variants(args, body)
        else:
            default_impl = empty_node()

        methods.append(list_node([method_name, sig, default_impl]))
    advance_end(parser)
    return nodes.node_4(NT_TRAIT, __ntok(node), name, instance_name, constraints, list_node(methods))


def stmt_implement(parser, op, node):
    type_parser = parser.type_parser
    trait_name = grab_name(type_parser)
    advance_expected(parser, TT_FOR)
    type_name = grab_name(type_parser)

    methods = []
    while parser.token_type == TT_METHOD:
        advance_expected(parser, TT_METHOD)
        method_name = grab_name_or_operator(parser.name_parser)
        funcs = parse_function_variants(parser.expression_parser,
                                        TERM_FUN_PATTERN, TERM_FUN_GUARD, TERM_IMPL_BODY, TERM_IMPL_BODY)
        methods.append(list_node([method_name, funcs]))

    advance_end(parser)
    return nodes.node_3(NT_IMPLEMENT, __ntok(node), trait_name, type_name, list_node(methods))


# OPERATORS

def stmt_prefix(parser, op, node):
    op_node = expect_expression_of(parser.name_parser, 0, NT_NAME)
    func_node = expect_expression_of(parser.name_parser, 0, NT_NAME)

    op_value = symbol_or_name_value(parser, op_node)
    func_value = symbol_or_name_value(parser, func_node)

    op = parser_current_scope_find_operator_or_create_new(parser, op_value)
    op = operator_prefix(op, prefix_nud_function, func_value)

    endofexpression(parser)
    parser_current_scope_add_operator(parser, op_value, op)


def stmt_infixl(parser, op, node):
    return _meta_infix(parser, node, led_infix_function)


def stmt_infixr(parser, op, node):
    return _meta_infix(parser, node, led_infixr_function)


def _meta_infix(parser, node, infix_function):
    op_node = expect_expression_of(parser.name_parser, 0, NT_NAME)
    func_node = expect_expression_of(parser.name_parser, 0, NT_NAME)
    precedence_node = expect_expression_of(parser.name_parser, 0, NT_INT)

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
