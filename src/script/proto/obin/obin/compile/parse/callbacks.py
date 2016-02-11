from obin.compile.parse.basic import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes
from obin.compile.parse.nodes import (node_token as __ntok, node_0, node_1, node_2, node_3)
from obin.types import space

NODE_TYPE_MAPPING = {
    TT_DOT: NT_LOOKUP_SYMBOL,
    TT_TRUE: NT_TRUE,
    TT_FALSE: NT_FALSE,
    TT_NIL: NT_NIL,
    TT_INT: NT_INT,
    TT_FLOAT: NT_FLOAT,
    TT_STR: NT_STR,
    TT_CHAR: NT_CHAR,
    TT_WILDCARD: NT_WILDCARD,
    TT_NAME: NT_NAME,
    TT_BACKTICK: NT_SPECIAL_NAME,
    TT_DEF: NT_DEF,
    TT_IF: NT_IF,
    TT_WHEN: NT_WHEN,
    TT_MATCH: NT_MATCH,
    TT_IMPORT: NT_IMPORT,
    TT_EXPORT: NT_EXPORT,
    TT_USE: NT_USE,
    TT_LOAD: NT_LOAD,
    TT_TRAIT: NT_TRAIT,
    TT_GENERIC: NT_GENERIC,
    TT_SPECIFY: NT_SPECIFY,
    TT_RETURN: NT_RETURN,
    TT_THROW: NT_THROW,
    TT_BREAK: NT_BREAK,
    TT_CONTINUE: NT_CONTINUE,
    TT_FOR: NT_FOR,
    TT_WHILE: NT_WHILE,
    TT_ELLIPSIS: NT_REST,
    TT_ASSIGN: NT_ASSIGN,
    TT_OF: NT_OF,
    TT_AS: NT_AS,
    TT_ISA: NT_ISA,
    TT_NOTA: NT_NOTA,
    TT_AND: NT_AND,
    TT_OR: NT_OR,
    TT_DOUBLE_DOT: NT_RANGE,
    TT_COLON: NT_SYMBOL,
    TT_KINDOF: NT_KINDOF,
    TT_ID: NT_NAME,
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
def led_infix(parser, node, left):
    h = node_operator(parser, node)
    # TODO CHECK IF THIS CYCLE IS STILL NEEDED
    exp = None
    while exp is None:
        exp = expression(parser, h.lbp)

    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr(parser, node, left):
    h = node_operator(parser, node)
    exp = expression(parser, h.lbp - 1)
    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr_function(parser, node, left):
    exp = expression(parser, op.lbp - 1)
    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def prefix_nud_function(parser, node):
    # TODO WHY 70 here?!!!!
    exp = expression(parser, 70)
    return nodes.create_call_node_name(node, op.prefix_function, [exp])


def led_infix_function(parser, node, left):
    exp = None
    while exp is None:
        exp = expression(parser, op.lbp)

    return nodes.create_call_node_name(node, op.infix_function, [left, exp])


def led_infixr_assign(parser, node, left):
    ltype = nodes.node_token_type(left)

    if ltype != TT_DOT and ltype != TT_LSQUARE \
            and ltype != TT_NAME and ltype != TT_LCURLY and ltype != TT_LPAREN:
        parse_error(parser, u"Bad lvalue in assignment", left)

    if ltype == TT_LPAREN and nodes.node_arity(left) != 1:
        parse_error(parser, u"Bad lvalue in assignment, wrong tuple destructuring", left)

    if ltype == TT_LCURLY and nodes.node_arity(left) == 0:
        parse_error(parser, u"Bad lvalue in assignment, empty map", left)

    exp = expression(parser, 9)

    return node_2(__ntype(node), __ntok(node), left, exp)


def infix_when(parser, node, left):
    first = condition(parser)
    advance_expected(parser, TT_ELSE)
    exp = expression(parser, 0)
    return node_3(NT_WHEN, __ntok(node), first, left, exp)


def infix_dot(parser, node, left):
    check_token_type(parser, TT_NAME)
    symbol = _init_default_current_0(parser)
    advance(parser)
    return node_2(NT_LOOKUP_SYMBOL, __ntok(node), left, symbol)


def infix_lcurly(parser, node, left):
    items = []
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_COLON, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expression(parser, 10)

            advance_expected(parser, TT_ASSIGN)
            value = expression(parser, 0)

            items.append(nodes.list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    return node_2(NT_MODIFY, __ntok(node), left, nodes.list_node(items))


def infix_lsquare(parser, node, left):
    exp = expression(parser, 0)
    advance_expected(parser, TT_RSQUARE)
    return node_2(NT_LOOKUP, __ntok(node), left, exp)


def infix_simple_pair(parser, node, left):
    check_token_type(parser, TT_NAME)
    name = _init_default_current_0(parser)
    advance(parser)
    return node_2(__ntype(node), __ntok(node), left, name)


def infix_lparen(parser, node, left):
    items = []
    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)

    if nodes.node_token_type(left) == TT_DOT:
        return node_3(NT_CALL_MEMBER, __ntok(node),
                      nodes.node_first(left),
                      nodes.node_second(left),
                      nodes.list_node(items))
    else:
        return node_2(NT_CALL, __ntok(node), left, nodes.list_node(items))


def infix_at(parser, node, left):
    ltype = nodes.node_token_type(left)
    if ltype != TT_NAME:
        parse_error(parser, u"Bad lvalue in pattern binding", left)

    exp = expression(parser, 9)
    return node_2(NT_BIND, __ntok(node), left, exp)


##############################################################
# INFIX
##############################################################




def _prefix_nud(parser, node_type, node):
    # TODO WHY 70 here?!!!!
    exp = expression(parser, 70)
    return node_1(node_type, __ntok(node), exp)


def prefix_nud(parser, node):
    return _prefix_nud(parser, __ntype(node), node)


def itself(parser, node):
    return node_0(__ntype(node), __ntok(node))


def prefix_colon(parser, node):
    check_token_types(parser, [TT_NAME, TT_BACKTICK])
    exp = expression(parser, 70)
    check_node_types(parser, exp, [NT_NAME, NT_SPECIAL_NAME])
    return node_1(__ntype(node), __ntok(node), exp)


def symbol_wildcard(parser, node):
    return parse_error(parser, u"Invalid use of _ pattern", node)


def prefix_if(parser, node):
    branches = []

    cond = prefix_condition(parser)
    body = (statements(parser, TERM_IF))

    branches.append(nodes.list_node([cond, body]))
    check_token_types(parser, TERM_IF)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = prefix_condition(parser)
        body = statements(parser, TERM_IF)

        branches.append(nodes.list_node([cond, body]))
        check_token_types(parser, TERM_IF)

    advance_expected(parser, TT_ELSE)
    body = statements(parser, TERM_BLOCK)
    branches.append(nodes.list_node([nodes.empty_node(), body]))
    advance_end(parser)

    return node_1(NT_IF, __ntok(node), nodes.list_node(branches))


# separate lparen handle for match case declarations
def prefix_lparen_tuple(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

    items = []
    while True:
        exp = expression(parser, 0)
        items.append(exp)
        if parser.token_type != TT_COMMA:
            break

        advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), nodes.list_node(items))


def prefix_lparen(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.create_unit_node(node)

    e = expression(parser, 0)
    if parser.token_type != TT_COMMA:
        advance_expected(parser, TT_RPAREN)
        return e

    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node_1(NT_TUPLE, __ntok(node), nodes.list_node(items))


def prefix_lsquare(parser, node):
    items = []
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RSQUARE)
    return node_1(NT_LIST, __ntok(node), nodes.list_node(items))


def on_bind_node(parser, key):
    if nodes.node_type(key) != NT_NAME:
        parse_error(parser, u"Invalid bind name", key)

    advance_expected(parser, TT_AT_SIGN)
    real_key, value = _parse_map_key_pair(parser, [TT_NAME, TT_COLON, TT_STR], None)

    # allow syntax like {var1@ key}
    if nodes.node_type(real_key) == NT_NAME:
        real_key = nodes.create_symbol_node(real_key, real_key)

    bind_key = nodes.create_bind_node(key, key, real_key)
    return bind_key, value


# this callback used in pattern matching
def prefix_lcurly_patterns(parser, node):
    return _prefix_lcurly(parser, node, [TT_NAME, TT_COLON, TT_STR], on_bind_node)


def prefix_lcurly(parser, node):
    return _prefix_lcurly(parser, node, [TT_NAME, TT_COLON, TT_INT, TT_STR, TT_CHAR, TT_FLOAT], None)


def _parse_map_key_pair(parser, types, on_unknown):
    check_token_types(parser, types)
    # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
    key = expression(parser, 10)

    if parser.token_type == TT_COMMA:
        value = nodes.empty_node()
    elif parser.token_type == TT_RCURLY:
        value = nodes.empty_node()
    elif parser.token_type == TT_ASSIGN:
        advance_expected(parser, TT_ASSIGN)
        value = expression(parser, 0)
    else:
        if on_unknown is None:
            parse_error(parser, u"Invalid map declaration syntax", parser.node)
        key, value = on_unknown(parser, key)

    return key, value


def _prefix_lcurly(parser, node, types, on_unknown):
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


def parse_function(parser, can_has_empty_name):
    if parser.token_type == TT_NAME:
        name = _init_default_current_0(parser)
        advance(parser)
    else:
        if can_has_empty_name is True:
            name = nodes.empty_node()
        else:
            return parse_error(parser, u"Expected function name", parser.node)

    funcs = []
    pattern_parser = parser.pattern_parser

    if parser.token_type == TT_CASE:
        while pattern_parser.token_type == TT_CASE:
            advance_expected(pattern_parser, TT_CASE)
            args = expression(pattern_parser, 0)
            args_type = nodes.node_type(args)
            if args_type != NT_UNIT and args_type != NT_TUPLE:
                parse_error(parser, u"Invalid  syntax in function arguments", args)

            advance_expected(parser, TT_ARROW)
            body = statements(parser, TERM_CASE)
            funcs.append(nodes.list_node([args, body]))
    else:
        if parser.token_type == TT_ARROW:
            args = nodes.create_unit_node(parser.node)
        else:
            args = expression(pattern_parser, 0)

        advance_expected(parser, TT_ARROW)
        body = statements(parser, TERM_BLOCK)
        funcs.append(nodes.list_node([args, body]))

    advance_end(parser)
    return name, nodes.list_node(funcs)


def prefix_def(parser, node):
    name, funcs = parse_function(parser.expression_parser, False)
    return node_2(NT_DEF, __ntok(node), name, funcs)


def prefix_fun(parser, node):
    name, funcs = parse_function(parser, True)
    return node_2(NT_FUN, __ntok(node), name, funcs)


def prefix_try(parser, node):
    endofexpression(parser)
    trybody = statements(parser, TERM_TRY)

    advance_expected(parser, TT_CATCH)
    check_token_type(parser, TT_NAME)
    varname = expression(parser, 0)
    catchstmts = statements(parser, TERM_CATCH)
    catchbody = nodes.list_node([varname, catchstmts])
    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = statements(parser, TERM_BLOCK)
    else:
        finallybody = nodes.empty_node()

    advance_end(parser)
    return node_3(NT_TRY, __ntok(node), trybody, catchbody, finallybody)


def prefix_match(parser, node):
    exp = expression(parser, 0)

    pattern_parser = parser.pattern_parser
    branches = []
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = expression(pattern_parser, 0)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, TERM_CASE)

        branches.append(nodes.list_node([pattern, body]))

    advance_end(parser)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    return node_2(NT_MATCH, __ntok(node), exp, nodes.list_node(branches))


def stmt_single(parser, node):
    exp = expression(parser, 0)
    endofexpression(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def stmt_loop_flow(parser, node):
    endofexpression(parser)
    if parser.token_type not in LOOP_CONTROL_TOKENS:
        parse_error(parser, u"Unreachable statement", node)
    return node_0(__ntype(node), __ntok(node))


def stmt_operator(parser, node):
    pass


def stmt_while(parser, node):
    cond = prefix_condition(parser)
    stmts = statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_2(NT_WHILE, __ntok(node), cond, stmts)


def stmt_for(parser, node):
    # set big lbp to overriding IN binding power
    variables = [expression(parser, 70)]
    while parser.token_type == TT_COMMA:
        advance(parser)
        if parser.token_type != TT_NAME:
            parse_error(parser, u"Wrong variable name in for loop", node)

        variables.append(expression(parser, 0))

    vars = nodes.list_node(variables)
    advance_expected(parser, TT_IN)
    exp = expression(parser, 0)
    # CALL endofexpression for one line for i in 1..2; i end
    endofexpression(parser)

    stmts = statements(parser, TERM_BLOCK)

    advance_end(parser)
    return node_3(NT_FOR, __ntok(node), vars, exp, stmts)


def stmt_when(parser, node):
    cond = prefix_condition(parser)
    body = statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_2(NT_WHEN_NO_ELSE, __ntok(node), cond, body)


###############################################################
# MODULE STATEMENTS
###############################################################

def parse_specify_fn(_parser, _signature_parser):
    signature = []

    advance_expected(_parser, TT_LPAREN)
    while _parser.token_type != TT_RPAREN:
        sig = expression(_signature_parser, 0)
        signature.append(sig)

        if _parser.token_type != TT_COMMA:
            break

        advance_expected(_signature_parser, TT_COMMA)

    advance_expected(_parser, TT_RPAREN)
    advance_expected(_parser, TT_ARROW)

    body = statements(_parser, TERM_CASE)
    return nodes.list_node([nodes.list_node(signature), body])


def parse_specify_funcs(parser):
    generic_signature_parser = parser.generic_signature_parser
    funcs = []
    if parser.token_type == TT_LPAREN:
        func = parse_specify_fn(parser.expression_parser, generic_signature_parser)
        funcs.append(func)
        advance_end(parser)
    else:
        # advance_expected(parser, TT_COLON)
        while parser.token_type == TT_CASE:
            advance_expected(generic_signature_parser, TT_CASE)
            func = parse_specify_fn(parser.expression_parser, generic_signature_parser)
            funcs.append(func)

        advance_end(parser)

    if len(funcs) == 0:
        parse_error(parser, u"Empty specify statement", parser.node)

    return nodes.list_node(funcs)


def stmt_specify(parser, node):
    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)

    funcs = parse_specify_funcs(parser)
    return node_2(NT_SPECIFY, __ntok(node), name, funcs)


def stmt_module(parser, node):
    if parser.token_type != TT_NAME:
        parse_error(parser, u"Invalid module name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)
    stmts = statements(parser, TERM_BLOCK)
    advance_end(parser)
    return node_2(NT_MODULE, __ntok(node), name, stmts)


def stmt_generic(parser, node):
    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)

    if parser.token_type == TT_CASE or parser.token_type == TT_LPAREN:
        funcs = parse_specify_funcs(parser)
        return node_2(NT_GENERIC, __ntok(node), name, funcs)
    else:
        return node_1(NT_GENERIC, __ntok(node), name)


def trait_name(parser):
    check_token_type(parser, TT_NAME)
    exp = expression(parser, 0)
    if nodes.node_type(exp) != NT_NAME:
        parse_error(parser, u"Invalid trait name", parser.node)
    return exp


def stmt_trait(parser, node):
    names = [trait_name(parser)]
    while parser.token_type == TT_COMMA:
        advance_expected(parser, TT_COMMA)
        names.append(trait_name(parser))

    return node_1(NT_TRAIT, __ntok(node), nodes.list_node(names))


def stmt_load(parser, node):
    imported = expression(parser.load_parser, 0)
    return node_1(NT_LOAD, __ntok(node), imported)
