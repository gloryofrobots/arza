import obin.compile.rlexer as lexer
from obin.compile.parse.token_type import *
from obin.compile.parse.node import Node, is_empty_node, empty_node
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.basic import *


def infix_when(parser, node, left):
    node.init(3)
    node.setfirst(condition(parser))
    node.setsecond(left)
    advance_expected(parser, TT_ELSE)
    node.setthird(expression(parser, 0))
    return node


def infix_dot(parser, node, left):
    node.init(2)
    node.setfirst(left)
    check_token_type(parser, TT_NAME)
    node.setsecond(parser.node)
    advance(parser)
    return node


def infix_lsquare(parser, node, left):
    node.init(2)
    node.setfirst(left)
    node.setsecond(expression(parser, 0))
    advance_expected(parser, TT_RSQUARE)
    return node


def infix_lparen(parser, node, left):
    items = []
    if left.type == TT_DOT:
        node.init(3)
        node.setfirst(left.first())
        node.setsecond(left.second())
        node.setthird(items)
    else:
        node.init(2)
        node.setfirst(left)
        node.setsecond(items)
        """
        if ((left.arity !== "unary" || left.id !== "function") &&
            left.arity !== "name" && left.id !== "(" &&
            left.id !== "&&" && left.id !== "||" && left.id !== "?") {
            left.error("Expected a variable name.");
        }
        """
    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.node.type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    return node


def prefix_if(parser, node):
    node.init(1)
    branches = []

    cond = condition(parser)
    advance_expected(parser, TT_LCURLY)
    body = (statements(parser, [TT_RCURLY]))

    branches.append([cond, body])
    advance_expected(parser, TT_RCURLY)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = condition(parser)
        advance_expected(parser, TT_LCURLY)
        body = statements(parser, [TT_RCURLY])

        branches.append([cond, body])
        advance_expected(parser, TT_RCURLY)
    if parser.token_type == TT_ELSE:
        advance_expected(parser, TT_ELSE)
        advance_expected(parser, TT_LCURLY)
        body = statements(parser, [TT_RCURLY])
        advance_expected(parser, TT_RCURLY)
        branches.append([[], body])
    else:
        branches.append([])

    # append else branch anyway
    node.setfirst(branches)
    return node


def prefix_lparen(parser, node):
    e = expression(parser, 0)
    if parser.node.type != TT_COMMA:
        advance_expected(parser, TT_RPAREN)
        return e

    node.init(1)
    items = [e]
    advance_expected(parser, TT_COMMA)

    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.node.type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)
    node.setfirst(items)
    return node


def prefix_lsquare(parser, node):
    items = []
    node.init(1)
    if parser.token_type != TT_RSQUARE:
        while True:
            items.append(expression(parser, 0))
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    node.setfirst(items)
    advance_expected(parser, TT_RSQUARE)
    return node


def prefix_lcurly(parser, node):
    items = []
    key = None
    value = None
    node.init(1)
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            key = parser.node
            advance(parser)
            advance_expected(parser, TT_COLON)
            value = expression(parser, 0)
            items.append([key, value])
            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RCURLY)
    node.setfirst(items)
    return node


def parse_fn(parser):
    args = []
    body = []
    outers = []
    if parser.token_type == TT_NAME:
        name = parser.node
        advance(parser)
    else:
        name = empty_node()

    if parser.token_type == TT_LPAREN:
        advance_expected(parser, TT_LPAREN)
        if parser.token_type != TT_RPAREN:
            while True:
                if parser.token_type == TT_NAME:
                    args.append(parser.node)
                    advance(parser)

                if parser.token_type != TT_COMMA:
                    break

                advance_expected(parser, TT_COMMA)

        if parser.token_type == TT_ELLIPSIS:
            rest = expression(parser.args_parser, 0)
            # advance(parser)
            args.append(rest)
            # advance_expected(parser, TT_NAME)

        advance_expected(parser, TT_RPAREN)

    advance_expected(parser, TT_LCURLY)
    if parser.token_type == TT_OUTER:
        advance_expected(parser, TT_OUTER)
        while True:
            if parser.token_type == TT_NAME:
                outers.append(parser.node)
                advance(parser)

            if parser.token_type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

        if len(outers) == 0:
            parse_error_simple(parser, "Outer variables not declared")

    body = statements(parser)
    if not body:
        body = empty_node()
    advance_expected(parser, TT_RCURLY)
    return name, args, outers, body


def prefix_fn(parser, node):
    node.init(3)
    name, args, outers, body = parse_fn(parser)
    if not is_empty_node(name):
        parse_error_node(parser, "In expressions functions could not have names", node)
    node.setfirst(args)
    node.setsecond(outers)
    node.setthird(body)
    return node


def stmt_fn(parser, node):
    node.init(4)
    name, args, outers, body = parse_fn(parser)
    if is_empty_node(name):
        parse_error_node(parser, "Function statement must be declared with name", node)
    node.setfirst(name)
    node.setsecond(args)
    node.setthird(outers)
    node.setfourth(body)
    return node


def parse_object(parser):
    def _object_statement_to_expr(stmt):
        expr = Node(stmt.type, stmt.value, stmt.position, stmt.line)
        expr.init(2)
        expr.setfirst(stmt.second())
        expr.setsecond(stmt.third())
        return expr

    def _fn_statement_to_expr(stmt):
        expr = Node(stmt.type, stmt.value, stmt.position, stmt.line)
        expr.init(3)
        expr.setfirst(stmt.second())
        expr.setsecond(stmt.third())
        expr.setthird(stmt.fourth())
        return expr

    name = empty_node()
    traits = []
    items = []

    if parser.token_type == TT_NAME:
        name = parser.node
        advance(parser)

    if parser.token_type == TT_LPAREN:
        advance_expected(parser, TT_LPAREN)
        if parser.token_type != TT_RPAREN:
            while True:
                if parser.token_type == TT_NAME:
                    traits.append(parser.node)
                    advance(parser)

                if parser.token_type != TT_COMMA:
                    break

                advance_expected(parser, TT_COMMA)

        advance_expected(parser, TT_RPAREN)

    advance_expected(parser, TT_LCURLY)
    if parser.token_type != TT_RCURLY:
        while True:
            if parser.token_type == TT_FN:
                fn = statement(parser)
                key = fn.first()
                # dirty hack to convert statements to expression for compiler
                value = _fn_statement_to_expr(fn)
            elif parser.token_type == TT_OBJECT:
                obj = statement(parser)
                key = obj.first()
                # dirty hack to convert statements to expression for compiler
                value = _object_statement_to_expr(obj)
            else:
                # TODO check it
                check_token_types(parser, [TT_NAME, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
                key = parser.node
                advance(parser)
                advance_expected(parser, TT_ASSIGN)
                value = expression(parser, 0)

            items.append([key, value])
            if parser.token_type == TT_RCURLY:
                break

    advance_expected(parser, TT_RCURLY)
    return name, traits, items


def prefix_object(parser, node):
    node.init(2)
    name, traits, body = parse_object(parser)
    if not is_empty_node(name):
        parse_error_node(parser, "In expressions objects could not have names", node)
    node.setfirst(traits)
    node.setsecond(body)
    return node


def stmt_object(parser, node):
    node.init(3)
    name, traits, items = parse_object(parser)
    # TODO move this check to parse object or add support for error token in error func
    if is_empty_node(name):
        parse_error_node(parser, "Object statement must have name", node)
    node.setfirst(name)
    node.setsecond(traits)
    node.setthird(items)
    return node


def stmt_single(parser, node):
    node.init(1)
    if token_is_one_of(parser, [TT_SEMI, TT_RCURLY]) or parser.is_newline_occurred:
        node.setfirst([])
    else:
        node.setfirst(expression(parser, 0))
    endofexpression(parser)
    return node


def stmt_outer(parser, node):
    parse_error_simple(parser, "Outer variables can be declared only in first function statement")


def stmt_loop_flow(parser, node):
    endofexpression(parser)
    if parser.token_type != TT_RCURLY:
        parse_error_simple(parser, "Unreachable statement")
    return node


def stmt_while(parser, node):
    node.init(2)
    node.setfirst(condition(parser))
    advance_expected(parser, TT_LCURLY)
    node.setsecond(statements(parser, [TT_RCURLY]))
    advance_expected(parser, TT_RCURLY)
    return node


def stmt_for(parser, node):
    node.init(3)
    vars = []
    # set big lbp to overriding IN binding power
    vars.append(expression(parser, 70))
    while parser.token_type == TT_COMMA:
        advance(parser)
        if parser.token_type != TT_NAME:
            parse_error_simple(parser, "Wrong variable name in for loop")

        vars.append(expression(parser, 0))

    node.setfirst(vars)
    advance_expected(parser, TT_IN)
    node.setsecond(expression(parser, 0))

    advance_expected(parser, TT_LCURLY)
    node.setthird(statements(parser, [TT_RCURLY]))
    advance_expected(parser, TT_RCURLY)
    return node


def stmt_generic(parser, node):
    if parser.token_type != TT_NAME:
        parse_error_simple(parser, "Wrong generic name")
    name = parser.node
    advance(parser)

    if parser.token_type == TT_LCURLY or parser.token_type == TT_LPAREN:
        node.init(2)
        funcs = parse_reify_funcs(parser)
        node.setfirst(name)
        node.setsecond(funcs)
    else:
        node.init(1)
        node.setfirst(name)

    return node


def stmt_trait(parser, node):
    node.init(1)
    name = expression(parser, 0)
    if name.type != TT_NAME:
        parse_error_simple(parser, "Wrong trait name")
    node.setfirst(name)
    return node


def parse_reify_fn(_parser, _signature_parser):
    signature = []

    advance_expected(_parser, TT_LPAREN)
    while _parser.token_type != TT_RPAREN:
        sig = expression(_signature_parser, 0)
        signature.append(sig)

        if _parser.token_type != TT_COMMA:
            break

        advance_expected(_signature_parser, TT_COMMA)

    advance_expected(_parser, TT_RPAREN)
    advance_expected(_parser, TT_LCURLY)

    body = statements(_parser)
    # TODO FIX IT
    if not body:
        body = empty_node()

    advance_expected(_parser, TT_RCURLY)
    return [signature, body]


def parse_reify_funcs(parser):
    generic_signature_parser = parser.generic_signature_parser
    funcs = []
    if parser.token_type == TT_LPAREN:
        func = parse_reify_fn(parser, generic_signature_parser)
        funcs.append(func)
    else:
        advance_expected(parser, TT_LCURLY)
        while parser.token_type == TT_LPAREN:
            func = parse_reify_fn(parser, generic_signature_parser)
            funcs.append(func)

        advance_expected(parser, TT_RCURLY)

    if len(funcs) == 0:
        parse_error_simple(parser, "Empty reify statement")

    return funcs


def stmt_reify(parser, node):
    node.init(2)

    if parser.token_type != TT_NAME:
        parse_error_simple(parser, "Wrong generic name in reify statement")

    name = parser.node
    advance(parser)

    funcs = parse_reify_funcs(parser)

    node.setfirst(name)
    node.setsecond(funcs)
    return node
