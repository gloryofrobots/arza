import obin.compile.rlexer as lexer
from obin.compile.parse.token_type import *
from obin.compile.parse.node import Node, is_empty_node, empty_node, list_node
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
    if parser.token_type != TT_RPAREN:
        while True:
            items.append(expression(parser, 0))
            if parser.node.type != TT_COMMA:
                break

            advance_expected(parser, TT_COMMA)

    advance_expected(parser, TT_RPAREN)

    if left.type == TT_DOT:
        node.init(3)
        node.setfirst(left.first())
        node.setsecond(left.second())
        node.setthird(list_node(items))
    else:
        node.init(2)
        node.setfirst(left)
        node.setsecond(list_node(items))
        """
        if ((left.arity !== "unary" || left.id !== "function") &&
            left.arity !== "name" && left.id !== "(" &&
            left.id !== "&&" && left.id !== "||" && left.id !== "?") {
            left.error("Expected a variable name.");
        }
        """
    return node


def prefix_if(parser, node):
    IF_TERMINATION_TOKENS = [TT_ELIF, TT_ELSE, TT_END]
    node.init(1)
    branches = list_node([])

    cond = condition(parser)
    advance_expected(parser, TT_COLON)
    body = (statements(parser, IF_TERMINATION_TOKENS))

    branches.append_list([cond, body])
    check_token_types(parser, IF_TERMINATION_TOKENS)

    while parser.token_type == TT_ELIF:
        advance_expected(parser, TT_ELIF)

        cond = condition(parser)
        advance_expected(parser, TT_COLON)
        body = statements(parser, IF_TERMINATION_TOKENS)

        branches.append_list([cond, body])
        check_token_types(parser, IF_TERMINATION_TOKENS)
    if parser.token_type == TT_ELSE:
        advance_expected(parser, TT_ELSE)
        advance_expected(parser, TT_COLON)
        body = statements(parser)
        branches.append_list([empty_node(), body])
        advance_expected(parser, TT_END)
    else:
        advance_expected(parser, TT_END)
        branches.append(empty_node())

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
    node.setfirst(list_node(items))
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

    node.setfirst(list_node(items))
    advance_expected(parser, TT_RSQUARE)
    return node


def prefix_lcurly(parser, node):
    items = []
    node.init(1)
    if parser.token_type != TT_RCURLY:
        while True:
            # TODO check it
            check_token_types(parser, [TT_NAME, TT_INT, TT_STR, TT_CHAR, TT_FLOAT])
            key = parser.node
            advance(parser)

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
    args = []
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

    advance_expected(parser, TT_COLON)
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
    advance_expected(parser, TT_END)
    return name, list_node(args), list_node(outers), body


def prefix_func(parser, node):
    node.init(3)
    name, args, outers, body = parse_func(parser)
    if not is_empty_node(name):
        parse_error_node(parser, "func expression could not have name", node)
    node.setfirst(args)
    node.setsecond(outers)
    node.setthird(body)
    return node


def stmt_def(parser, node):
    node.init(4)
    name, args, outers, body = parse_func(parser)
    if is_empty_node(name):
        parse_error_node(parser, "def statement must be declared with name", node)
    node.setfirst(name)
    node.setsecond(args)
    node.setthird(outers)
    node.setfourth(body)
    return node

def stmt_single(parser, node):
    node.init(1)
    if token_is_one_of(parser, [TT_SEMI, TT_END]) or parser.is_newline_occurred:
        node.setfirst(list_node([]))
    else:
        node.setfirst(expression(parser, 0))
    endofexpression(parser)
    return node


def stmt_outer(parser, node):
    parse_error_simple(parser, "Outer variables can be declared only in first function statement")


def stmt_loop_flow(parser, node):
    endofexpression(parser)
    if parser.token_type != TT_END:
        parse_error_simple(parser, "Unreachable statement")
    return node


def stmt_while(parser, node):
    node.init(2)
    node.setfirst(condition(parser))
    advance_expected(parser, TT_COLON)
    node.setsecond(statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


def stmt_for(parser, node):
    node.init(3)
    variables = []
    # set big lbp to overriding IN binding power
    variables.append(expression(parser, 70))
    while parser.token_type == TT_COMMA:
        advance(parser)
        if parser.token_type != TT_NAME:
            parse_error_simple(parser, "Wrong variable name in for loop")

        variables.append(expression(parser, 0))

    node.setfirst(list_node(variables))
    advance_expected(parser, TT_IN)
    node.setsecond(expression(parser, 0))

    advance_expected(parser, TT_COLON)
    node.setthird(statements(parser, [TT_END]))
    advance_expected(parser, TT_END)
    return node


def stmt_origin(parser, node):
    node.init(4)
    name, args, outers, body = parse_func(parser)
    if is_empty_node(name):
        parse_error_node(parser, "origin statement must have name", node)
    node.setfirst(name)
    node.setsecond(args)
    node.setthird(outers)
    node.setfourth(body)
    return node


def stmt_generic(parser, node):
    if parser.token_type != TT_NAME:
        parse_error_simple(parser, "Wrong generic name")
    name = parser.node
    advance(parser)

    if parser.token_type == TT_COLON or parser.token_type == TT_LPAREN:
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
    advance_expected(_parser, TT_COLON)

    body = statements(_parser)
    # TODO FIX IT
    if not body:
        body = empty_node()

    advance_expected(_parser, TT_END)
    return list_node([list_node(signature), body])


def parse_reify_funcs(parser):
    generic_signature_parser = parser.generic_signature_parser
    funcs = []
    if parser.token_type == TT_LPAREN:
        func = parse_reify_fn(parser, generic_signature_parser)
        funcs.append(func)
    else:
        advance_expected(parser, TT_COLON)
        while parser.token_type == TT_LPAREN:
            func = parse_reify_fn(parser, generic_signature_parser)
            funcs.append(func)

        advance_expected(parser, TT_END)

    if len(funcs) == 0:
        parse_error_simple(parser, "Empty reify statement")

    return list_node(funcs)


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


def stmt_import(parser, node):
    # statement can be import x.y.z as c
    imported = expression(parser.module_name_alias_parser, 0)
    node.init(2)
    node.setfirst(imported)
    # SET HERE empty node to show compiler it is a statement
    # BAD DESIGN. NEED NODE TYPE
    node.setsecond(empty_node())

    return node


def prefix_import(parser, node):
    imported = expression(parser.module_name_parser, 0)
    node.init(1)
    node.setfirst(imported)

    return node
