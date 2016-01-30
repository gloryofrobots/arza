from obin.compile.parse.basic import *
from obin.compile.parse.node_type import *
from obin.compile.parse import nodes
from obin.compile.parse.nodes import (node_token as __ntok, node_0, node_1, node_2, node_3, node_4)

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
    TT_FUNC: NT_FUNC,
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
    TT_IN: NT_IN,
    TT_NOTIN: NT_NOTIN,
    TT_IS: NT_IS,
    TT_ISNOT: NT_ISNOT,
    TT_ISA: NT_ISA,
    TT_NOTA: NT_NOTA,
    TT_AND: NT_AND,
    TT_OR: NT_OR,
    TT_NOT: NT_NOT,
    TT_EQ: NT_EQ,
    TT_LE: NT_LE,
    TT_GE: NT_GE,
    TT_NE: NT_NE,
    TT_BITAND: NT_BITAND,
    TT_BITNOT: NT_BITNOT,
    TT_BITOR: NT_BITOR,
    TT_BITXOR: NT_BITXOR,
    TT_SUB: NT_SUB,
    TT_ADD: NT_ADD,
    TT_MUL: NT_MUL,
    TT_DIV: NT_DIV,
    TT_MOD: NT_MOD,
    TT_LT: NT_LT,
    TT_GT: NT_GT,
    TT_RSHIFT: NT_RSHIFT,
    TT_URSHIFT: NT_URSHIFT,
    TT_LSHIFT: NT_LSHIFT,
    TT_DOUBLE_COLON: NT_CONS,
    TT_DOUBLE_DOT: NT_RANGE,
    TT_COLON: NT_SYMBOL
}


def __ntype(node):
    node_type = NODE_TYPE_MAPPING[nodes.node_token_type(node)]
    return node_type


def _init_default_current_0(parser):
    return nodes.node_0(__ntype(parser.node), __ntok(parser.node))


def led_infix(parser, node, left):
    h = node_handler(parser, node)
    exp = None
    while exp is None:
        exp = expression(parser, h.lbp)

    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr(parser, node, left):
    h = node_handler(parser, node)
    exp = expression(parser, h.lbp - 1)
    return node_2(__ntype(node), __ntok(node), left, exp)


def led_infixr_assign(parser, node, left):
    ltype = nodes.node_token_type(left)
    # NOT TUPLE ASSIGNMENT
    if ltype != TT_DOT and ltype != TT_LSQUARE \
            and ltype != TT_NAME and ltype != TT_COMMA \
            and ltype != TT_LCURLY and ltype != TT_LPAREN:
        parse_error(parser, u"Bad lvalue in assignment", left)

    if ltype == TT_LPAREN and nodes.node_arity(left) != 1:
        parse_error(parser, u"Bad lvalue in assignment, wrong tuple destructuring", left)

    if ltype == TT_LCURLY and nodes.node_arity(left) == 0:
        parse_error(parser, u"Bad lvalue in assignment, empty map", left)

    exp = expression(parser, 9)

    return node_2(__ntype(node), __ntok(node), left, exp)


def _prefix_nud(parser, node_type, node):
    exp = expression(parser, 70)
    return node_1(node_type, __ntok(node), exp)


def prefix_nud(parser, node):
    node_type = __ntype(node)
    return _prefix_nud(parser, node_type, node)


def itself(parser, node):
    return node_0(__ntype(node), __ntok(node))


def prefix_colon(parser, node):
    check_token_types(parser, [TT_NAME, TT_BACKTICK])
    return _prefix_nud(parser, NT_SYMBOL, node)


def prefix_unary_minus(parser, node):
    return _prefix_nud(parser, NT_UNARY_MINUS, node)


def prefix_unary_plus(parser, node):
    return _prefix_nud(parser, NT_UNARY_PLUS, node)


def nud_wildcard(parser, node):
    return parse_error(parser, u"Invalid use of _ pattern", node)


def infix_when(parser, node, left):
    nodes.node_init(node, NT_WHEN, 3)
    nodes.node_setfirst(node, condition(parser))
    nodes.node_setsecond(node, left)
    advance_expected(parser, TT_ELSE)
    nodes.node_setthird(node, expression(parser, 0))
    return node


def infix_dot(parser, node, left):
    nodes.node_init(node, NT_LOOKUP_SYMBOL, 2)
    nodes.node_setfirst(node, left)
    check_token_type(parser, TT_NAME)
    symbol = _init_default_current_0(parser)
    nodes.node_setsecond(node, symbol)
    advance(parser)
    return node


def infix_lcurly(parser, node, left):
    items = []
    nodes.node_init(node, NT_MODIFY, 2)
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
    nodes.node_setfirst(node, left)
    nodes.node_setsecond(node, nodes.list_node(items))
    return node


def infix_lsquare(parser, node, left):
    exp = expression(parser, 0)

    nodes.node_init(node, NT_LOOKUP, 2)
    nodes.node_setfirst(node, left)
    nodes.node_setsecond(node, exp)

    advance_expected(parser, TT_RSQUARE)
    return node


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
        nodes.node_init(node, NT_CALL_MEMBER, 3)
        nodes.node_setfirst(node, nodes.node_first(left))
        nodes.node_setsecond(node, nodes.node_second(left))
        nodes.node_setthird(node, nodes.list_node(items))
    else:
        nodes.node_init(node, NT_CALL, 2)
        nodes.node_setfirst(node, left)
        nodes.node_setsecond(node, nodes.list_node(items))
    return node


def prefix_if(parser, node):
    IF_TERMINATION_TOKENS = [TT_ELIF, TT_ELSE, TT_END]
    nodes.node_init(node, NT_IF, 1)
    branches = []

    cond = condition(parser)
    endofexpression(parser)
    body = (statements(parser, IF_TERMINATION_TOKENS))

    branches.append(nodes.list_node([cond, body]))
    check_token_types(parser, IF_TERMINATION_TOKENS)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = condition(parser)
        # call endofexpression to allow one line ifs
        endofexpression(parser)
        body = statements(parser, IF_TERMINATION_TOKENS)

        branches.append(nodes.list_node([cond, body]))
        check_token_types(parser, IF_TERMINATION_TOKENS)
    if parser.token_type == TT_ELSE:
        advance_expected(parser, TT_ELSE)
        body = statements(parser)
        branches.append(nodes.list_node([nodes.empty_node(), body]))
        advance_expected(parser, TT_END)
    else:
        advance_expected(parser, TT_END)
        branches.append(nodes.empty_node())

    # append else branch anyway
    nodes.node_setfirst(node, nodes.list_node(branches))
    return node


# TODO MADE it only one lparen handler
def prefix_lparen_tuple(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.empty_node()

    nodes.node_init(node, NT_TUPLE, 1)
    items = []
    while True:
        exp = expression(parser, 0)
        items.append(exp)
        if parser.token_type != TT_COMMA:
            break

        advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    nodes.node_setfirst(node, nodes.list_node(items))
    return node


def prefix_lparen(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return nodes.empty_node()

    e = expression(parser, 0)
    if parser.token_type != TT_COMMA:
        advance_expected(parser, TT_RPAREN)
        return e

    nodes.node_init(node, NT_TUPLE, 1)
    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    nodes.node_setfirst(node, nodes.list_node(items))
    return node


def prefix_lsquare(parser, node):
    items = []
    nodes.node_init(node, NT_LIST, 1)
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    nodes.node_setfirst(node, nodes.list_node(items))
    advance_expected(parser, TT_RSQUARE)
    return node


def prefix_lcurly(parser, node):
    items = []
    nodes.node_init(node, NT_MAP, 1)
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_COLON, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expression(parser, 10)

            if parser.token_type == TT_COMMA:
                value = nodes.empty_node()
            elif parser.token_type == TT_RCURLY:
                value = nodes.empty_node()
            else:
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0)

            items.append(nodes.list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    nodes.node_setfirst(node, nodes.list_node(items))
    return node


def parse_func(parser):
    if parser.token_type == TT_NAME:
        name = _init_default_current_0(parser)
        advance(parser)
    else:
        name = nodes.empty_node()
    args_parser = parser.args_parser
    if args_parser.token_type == TT_ARROW:
        args = nodes.empty_node()
    else:
        args = expression(args_parser, 0)

    advance_expected(parser, TT_ARROW)
    body = statements(parser)
    if not body:
        body = nodes.empty_node()
    advance_expected(parser, TT_END)
    return name, args, body


# REPEATING MYSELF HERE BECAUSE I DON`T WONT TO HAVE DEF AND FUNC,
# AND MODULE FUNC IS DIFFERENT FROM EXPRESSION FUNC. IT DIDN'T HAVE ACCESS TO TRAIT GENERIC SPECIFY ...

def prefix_module_func(parser, node):
    nodes.node_init(node, NT_FUNC, 3)
    name, args, body = parse_func(parser.expression_parser)
    nodes.node_setfirst(node, name)
    nodes.node_setsecond(node, args)
    nodes.node_setthird(node, body)
    return node


def prefix_func(parser, node):
    nodes.node_init(node, NT_FUNC, 3)
    name, args, body = parse_func(parser)
    nodes.node_setfirst(node, name)
    nodes.node_setsecond(node, args)
    nodes.node_setthird(node, body)
    return node


def prefix_try(parser, node):
    nodes.node_init(node, NT_TRY, 3)
    trybody = statements(parser, [TT_CATCH])

    advance_expected(parser, TT_CATCH)
    check_token_type(parser, TT_NAME)
    varname = expression(parser, 0)
    catchstmts = statements(parser, [TT_FINALLY, TT_END])
    catchbody = nodes.list_node([varname, catchstmts])
    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = statements(parser, [TT_END])
    else:
        finallybody = nodes.empty_node()

    advance_expected(parser, TT_END)
    nodes.node_setfirst(node, trybody)
    nodes.node_setsecond(node, catchbody)
    nodes.node_setthird(node, finallybody)

    return node


def prefix_match(parser, node):
    nodes.node_init(node, NT_MATCH, 2)
    exp = expression(parser, 0)
    nodes.node_setfirst(node, exp)

    pattern_parser = parser.pattern_parser
    branches = []
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = expression(pattern_parser, 0)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, [TT_END, TT_CASE])
        # advance_expected(parser, TT_END)

        branches.append(nodes.list_node([pattern, body]))

    advance_expected(parser, TT_END)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    nodes.node_setsecond(node, nodes.list_node(branches))
    return node


def stmt_single(parser, node):
    if token_is_one_of(parser, [TT_SEMI, TT_END]) or parser.is_newline_occurred:
        exp = nodes.list_node([])
    else:
        exp = expression(parser, 0)
    endofexpression(parser)
    return node_1(__ntype(node), __ntok(node), exp)


def stmt_loop_flow(parser, node):
    endofexpression(parser)
    if parser.token_type not in [TT_END, TT_ELSE, TT_ELIF, TT_CASE]:
        parse_error(parser, u"Unreachable statement", node)
    return node_0(__ntype(node), __ntok(node))


def stmt_while(parser, node):
    nodes.node_init(node, NT_WHILE, 2)
    nodes.node_setfirst(node, condition(parser))
    # CALL endofexpression for one line while
    endofexpression(parser)
    nodes.node_setsecond(node, statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


def stmt_for(parser, node):
    nodes.node_init(node, NT_FOR, 3)
    variables = []
    # set big lbp to overriding IN binding power
    variables.append(expression(parser, 70))
    while parser.token_type == TT_COMMA:
        advance(parser)
        if parser.token_type != TT_NAME:
            parse_error(parser, u"Wrong variable name in for loop", node)

        variables.append(expression(parser, 0))

    nodes.node_setfirst(node, nodes.list_node(variables))
    advance_expected(parser, TT_IN)
    nodes.node_setsecond(node, expression(parser, 0))

    # CALL endofexpression for one line for i in 1..2; i end
    endofexpression(parser)
    nodes.node_setthird(node, statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


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

    body = statements(_parser, [TT_CASE, TT_END])
    # TODO FIX IT
    if not body:
        body = nodes.empty_node()

    # advance_expected(_parser, TT_END)
    return nodes.list_node([nodes.list_node(signature), body])


def parse_specify_funcs(parser):
    generic_signature_parser = parser.generic_signature_parser
    funcs = []
    if parser.token_type == TT_LPAREN:
        func = parse_specify_fn(parser.expression_parser, generic_signature_parser)
        funcs.append(func)
        advance_expected(parser, TT_END)
    else:
        # advance_expected(parser, TT_COLON)
        while parser.token_type == TT_CASE:
            advance_expected(generic_signature_parser, TT_CASE)
            func = parse_specify_fn(parser.expression_parser, generic_signature_parser)
            funcs.append(func)

        advance_expected(parser, TT_END)

    if len(funcs) == 0:
        parse_error(parser, u"Empty specify statement", parser.node)

    return nodes.list_node(funcs)


def stmt_specify(parser, node):
    nodes.node_init(node, NT_SPECIFY, 2)

    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)

    funcs = parse_specify_funcs(parser)

    nodes.node_setfirst(node, name)
    nodes.node_setsecond(node, funcs)
    return node


def stmt_module(parser, node):
    if parser.token_type != TT_NAME:
        parse_error(parser, u"Invalid module name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)
    stmts = statements(parser, [TT_END])
    advance_expected(parser, TT_END)
    nodes.node_init(node, NT_MODULE, 2)
    nodes.node_setfirst(node, name)
    nodes.node_setsecond(node, stmts)
    return node


def stmt_generic(parser, node):
    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_default_current_0(parser)
    advance(parser)

    if parser.token_type == TT_CASE or parser.token_type == TT_LPAREN:
        nodes.node_init(node, NT_GENERIC, 2)
        funcs = parse_specify_funcs(parser)
        nodes.node_setfirst(node, name)
        nodes.node_setsecond(node, funcs)
    else:
        nodes.node_init(node, NT_GENERIC, 1)
        nodes.node_setfirst(node, name)

    return node


def stmt_trait(parser, node):
    nodes.node_init(node, NT_TRAIT, 1)
    name = expression(parser, 0)
    if nodes.node_type(name) == NT_TUPLE:
        children = nodes.node_first(name)
        for child in children:
            if nodes.node_token_type(child) != TT_NAME:
                parse_error(parser, u"Invalid trait name", child)

        nodes.node_setfirst(node, children)

    elif nodes.node_token_type(name) == TT_NAME:
        nodes.node_setfirst(node, nodes.list_node([name]))
    else:
        parse_error(parser, u"Invalid trait name", parser.node)

    return node


def stmt_load(parser, node):
    imported = expression(parser.load_parser, 0)
    nodes.node_init(node, NT_LOAD, 1)
    nodes.node_setfirst(node, imported)

    return node
