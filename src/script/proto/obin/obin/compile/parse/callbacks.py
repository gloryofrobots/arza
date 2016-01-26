from obin.compile.parse.node import is_empty_node, empty_node, list_node
from obin.compile.parse.basic import *
from obin.compile.parse.node_type import *

NODE_TYPE_MAPPING = {
    TT_DOT: NT_LOOKUP_SYMBOL,
    TT_TRUE: NT_TRUE,
    TT_FALSE: NT_FALSE,
    TT_NIL: NT_NIL,
    TT_UNDEFINED: NT_UNDEFINED,
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


def get_node_type(parser, node):
    node_type = NODE_TYPE_MAPPING[node.type]
    return node_type


def _init_node(parser, node, arity):
    node_type = get_node_type(parser, node)
    node.init(node_type, arity)
    return node


def _init_current_node(parser, arity):
    return _init_node(parser, parser.node, arity)


def led_infix(parser, node, left):
    h = node_handler(parser, node)
    _init_node(parser, node, 2)
    node.setfirst(left)
    exp = None
    while exp is None:
        exp = expression(parser, h.lbp)

    node.setsecond(exp)
    return node


def led_infixr(parser, node, left):
    h = node_handler(parser, node)
    _init_node(parser, node, 2)

    node.setfirst(left)
    exp = expression(parser, h.lbp - 1)
    node.setsecond(exp)

    return node


def led_infixr_assign(parser, node, left):
    _init_node(parser, node, 2)
    ltype = left.type
    # NOT TUPLE ASSIGNMENT
    if ltype != TT_DOT and ltype != TT_LSQUARE \
            and ltype != TT_NAME and ltype != TT_COMMA \
            and ltype != TT_LCURLY and ltype != TT_LPAREN:
        parse_error(parser, u"Bad lvalue in assignment", left)

    if ltype == TT_LPAREN and left.arity != 1:
        parse_error(parser, u"Bad lvalue in assignment, wrong tuple destructuring", left)

    if ltype == TT_LCURLY and left.arity == 0:
        parse_error(parser, u"Bad lvalue in assignment, empty map", left)

    node.setfirst(left)
    exp = expression(parser, 9)
    node.setsecond(exp)

    return node


def _prefix_nud(parser, node_type, node):
    node.init(node_type, 1)
    exp = expression(parser, 70)
    node.setfirst(exp)
    return node


def prefix_nud(parser, node):
    node_type = get_node_type(parser, node)
    return _prefix_nud(parser, node_type, node)


def itself(parser, node):
    _init_node(parser, node, 0)
    return node


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
    node.init(NT_WHEN, 3)
    node.setfirst(condition(parser))
    node.setsecond(left)
    advance_expected(parser, TT_ELSE)
    node.setthird(expression(parser, 0))
    return node


def infix_dot(parser, node, left):
    node.init(NT_LOOKUP_SYMBOL, 2)
    node.setfirst(left)
    check_token_type(parser, TT_NAME)
    symbol = _init_current_node(parser, 0)
    node.setsecond(symbol)
    advance(parser)
    return node


def infix_lcurly(parser, node, left):
    items = []
    node.init(NT_MODIFY, 2)
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_COLON, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expression(parser, 10)

            advance_expected(parser, TT_ASSIGN)
            value = expression(parser, 0)

            items.append(list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    node.setfirst(left)
    node.setsecond(list_node(items))
    return node


def infix_lsquare(parser, node, left):
    exp = expression(parser, 0)

    node.init(NT_LOOKUP, 2)
    node.setfirst(left)
    node.setsecond(exp)

    advance_expected(parser, TT_RSQUARE)
    return node


def infix_simple_pair(parser, node, left):
    # TODO REMOVE IT
    symbol(parser, TT_COMMA, None)
    _init_node(parser, node, 2)
    node.setfirst(left)
    check_token_type(parser, TT_NAME)
    name = _init_current_node(parser, 0)
    node.setsecond(name)
    advance(parser)
    return node


def infix_lparen(parser, node, left):
    items = []
    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)

    if left.type == TT_DOT:
        node.init(NT_CALL_MEMBER, 3)
        node.setfirst(left.first())
        node.setsecond(left.second())
        node.setthird(list_node(items))
    else:
        node.init(NT_CALL, 2)
        node.setfirst(left)
        node.setsecond(list_node(items))
    return node


def prefix_if(parser, node):
    IF_TERMINATION_TOKENS = [TT_ELIF, TT_ELSE, TT_END]
    node.init(NT_IF, 1)
    branches = list_node([])

    cond = condition(parser)
    endofexpression(parser)
    body = (statements(parser, IF_TERMINATION_TOKENS))

    branches.append_list([cond, body])
    check_token_types(parser, IF_TERMINATION_TOKENS)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = condition(parser)
        # call endofexpression to allow one line ifs
        endofexpression(parser)
        body = statements(parser, IF_TERMINATION_TOKENS)

        branches.append_list([cond, body])
        check_token_types(parser, IF_TERMINATION_TOKENS)
    if parser.token_type == TT_ELSE:
        advance_expected(parser, TT_ELSE)
        body = statements(parser)
        branches.append_list([empty_node(), body])
        advance_expected(parser, TT_END)
    else:
        advance_expected(parser, TT_END)
        branches.append(empty_node())

    # append else branch anyway
    node.setfirst(branches)
    return node


# TODO MADE it only one lparen handler
def prefix_lparen_tuple(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return empty_node()

    node.init(NT_TUPLE, 1)
    items = []
    while True:
        exp = expression(parser, 0)
        items.append(exp)
        if parser.token_type != TT_COMMA:
            break

        advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    node.setfirst(list_node(items))
    return node


def prefix_lparen(parser, node):
    if parser.token_type == TT_RPAREN:
        advance_expected(parser, TT_RPAREN)
        return empty_node()

    e = expression(parser, 0)
    if parser.token_type != TT_COMMA:
        advance_expected(parser, TT_RPAREN)
        return e

    node.init(NT_TUPLE, 1)
    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    node.setfirst(list_node(items))
    return node


def prefix_lsquare(parser, node):
    items = []
    node.init(NT_LIST, 1)
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    node.setfirst(list_node(items))
    advance_expected(parser, TT_RSQUARE)
    return node


def prefix_lcurly(parser, node):
    items = []
    node.init(NT_MAP, 1)
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_COLON, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            # WE NEED LBP=10 TO OVERRIDE ASSIGNMENT LBP(9)
            key = expression(parser, 10)
            # key = _init_current_node(parser, 0)
            # advance(parser)

            if parser.token_type == TT_COMMA:
                value = empty_node()
            elif parser.token_type == TT_RCURLY:
                value = empty_node()
            else:
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0)

            items.append(list_node([key, value]))

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    node.setfirst(list_node(items))
    return node


def parse_func(parser):
    outers = []
    if parser.token_type == TT_NAME:
        name = _init_current_node(parser, 0)
        advance(parser)
    else:
        name = empty_node()
    args_parser = parser.args_parser
    if args_parser.token_type == TT_ARROW:
        args = empty_node()
    else:
        args = expression(args_parser, 0)

    advance_expected(parser, TT_ARROW)
    if parser.token_type == TT_OUTER:
        advance_expected(parser, TT_OUTER)
        while True:
            if parser.token_type == TT_NAME:
                outer = _init_current_node(parser, 0)
                outers.append(outer)
                advance(parser)

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

        if len(outers) == 0:
            parse_error(parser, u"Wrong outer declaration", parser.node)

    body = statements(parser)
    if not body:
        body = empty_node()
    advance_expected(parser, TT_END)
    return name, args, list_node(outers), body


def prefix_func(parser, node):
    node.init(NT_FUNC, 4)
    name, args, outers, body = parse_func(parser)
    node.setfirst(name)
    node.setsecond(args)
    node.setthird(outers)
    node.setfourth(body)
    return node


def prefix_try(parser, node):
    node.init(NT_TRY, 3)
    trybody = statements(parser, [TT_CATCH])

    advance_expected(parser, TT_CATCH)
    check_token_type(parser, TT_NAME)
    varname = expression(parser, 0)
    catchstmts = statements(parser, [TT_FINALLY, TT_END])
    catchbody = list_node([varname, catchstmts])
    if parser.token_type == TT_FINALLY:
        advance_expected(parser, TT_FINALLY)
        finallybody = statements(parser, [TT_END])
    else:
        finallybody = empty_node()

    advance_expected(parser, TT_END)
    node.setfirst(trybody)
    node.setsecond(catchbody)
    node.setthird(finallybody)

    return node


def prefix_match(parser, node):
    node.init(NT_MATCH, 2)
    exp = expression(parser, 0)
    node.setfirst(exp)

    pattern_parser = parser.pattern_parser
    branches = []
    while pattern_parser.token_type == TT_CASE:
        advance_expected(pattern_parser, TT_CASE)
        pattern = expression(pattern_parser, 0)
        advance_expected(parser, TT_ARROW)

        body = statements(parser, [TT_END, TT_CASE])
        # advance_expected(parser, TT_END)

        branches.append(list_node([pattern, body]))

    advance_expected(parser, TT_END)

    if len(branches) == 0:
        parse_error(parser, u"Empty match expression", node)

    node.setsecond(list_node(branches))
    return node


def stmt_single(parser, node):
    _init_node(parser, node, 1)
    if token_is_one_of(parser, [TT_SEMI, TT_END]) or parser.is_newline_occurred:
        node.setfirst(list_node([]))
    else:
        node.setfirst(expression(parser, 0))
    endofexpression(parser)
    return node


def stmt_outer(parser, node):
    parse_error(parser, u"Outer variables can be declared only in first function statement", node)


def stmt_loop_flow(parser, node):
    endofexpression(parser)
    if parser.token_type not in [TT_END, TT_ELSE, TT_ELIF, TT_CASE]:
        parse_error(parser, u"Unreachable statement", node)
    _init_node(parser, node, 0)
    return node


def stmt_while(parser, node):
    node.init(NT_WHILE, 2)
    node.setfirst(condition(parser))
    # CALL endofexpression for one line while
    endofexpression(parser)
    node.setsecond(statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


def stmt_for(parser, node):
    node.init(NT_FOR, 3)
    variables = []
    # set big lbp to overriding IN binding power
    variables.append(expression(parser, 70))
    while parser.token_type == TT_COMMA:
        advance(parser)
        if parser.token_type != TT_NAME:
            parse_error(parser, u"Wrong variable name in for loop", node)

        variables.append(expression(parser, 0))

    node.setfirst(list_node(variables))
    advance_expected(parser, TT_IN)
    node.setsecond(expression(parser, 0))

    # CALL endofexpression for one line for i in 1..2; i end
    endofexpression(parser)
    node.setthird(statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


def stmt_trait(parser, node):
    node.init(NT_TRAIT, 1)
    name = expression(parser, 0)
    if name.type != TT_NAME:
        parse_error(parser, u"Invalid trait name", parser.node)
    node.setfirst(name)
    return node


def stmt_generic(parser, node):
    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_current_node(parser, 0)
    advance(parser)

    if parser.token_type == TT_CASE or parser.token_type == TT_LPAREN:
        node.init(NT_GENERIC, 2)
        funcs = parse_specify_funcs(parser)
        node.setfirst(name)
        node.setsecond(funcs)
    else:
        node.init(NT_GENERIC, 1)
        node.setfirst(name)

    return node


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
        body = empty_node()

    # advance_expected(_parser, TT_END)
    return list_node([list_node(signature), body])


def parse_specify_funcs(parser):
    generic_signature_parser = parser.generic_signature_parser
    funcs = []
    if parser.token_type == TT_LPAREN:
        func = parse_specify_fn(parser, generic_signature_parser)
        funcs.append(func)
        advance_expected(parser, TT_END)
    else:
        # advance_expected(parser, TT_COLON)
        while parser.token_type == TT_CASE:
            advance_expected(generic_signature_parser, TT_CASE)
            func = parse_specify_fn(parser, generic_signature_parser)
            funcs.append(func)

        advance_expected(parser, TT_END)

    if len(funcs) == 0:
        parse_error(parser, u"Empty specify statement", parser.node)

    return list_node(funcs)


def stmt_specify(parser, node):
    node.init(NT_SPECIFY, 2)

    if parser.token_type != TT_NAME and parser.token_type != TT_BACKTICK:
        parse_error(parser, u"Invalid generic name", parser.node)

    name = _init_current_node(parser, 0)
    advance(parser)

    funcs = parse_specify_funcs(parser)

    node.setfirst(name)
    node.setsecond(funcs)
    return node


def stmt_load(parser, node):
    imported = expression(parser.module_name_alias_parser, 0)
    node.init(NT_LOAD, 1)
    node.setfirst(imported)

    return node


