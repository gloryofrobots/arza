__author__ = 'gloryofrobots'
import obin.compile.lexer
from obin.compile.parse.token_type import *
from obin.compile.parse.node import Node, is_empty_node, empty_node
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.basic import *


class BaseParser(object):
    def __init__(self, ts):
        self.handlers = {}
        self.ts = ts

    @property
    def token_type(self):
        return self.ts.token.type

    @property
    def is_newline_occurred(self):
        return self.ts.is_newline_occurred

    @property
    def node(self):
        return self.ts.node

    @property
    def token(self):
        return self.ts.token

    def next(self):
        return self.ts.next()

    def isend(self):
        return self.token_type == TT_ENDSTREAM


class Parser(BaseParser):
    def __init__(self, ts):
        super(Parser, self).__init__(ts)
        self.args_parser = args_parser_init(BaseParser(ts))
        self.module_name_parser = module_name_parser_init(BaseParser(ts))
        self.module_name_alias_parser = module_name_alias_parser_init(BaseParser(ts))
        self.import_alias_parser = import_alias_parser_init(BaseParser(ts))
        self.generic_signature_parser = generic_signature_parser_init(BaseParser(ts))
        # self.expression_parser = expression_parser_init(BaseParser(ts))
        main_parser_init(self)


def args_parser_init(parser):
    prefix(parser, TT_ELLIPSIS)
    symbol(parser, TT_COMMA)
    literal(parser, TT_NAME)
    return parser


def infix_simple_pair(parser, node, left):
    symbol(parser, TT_COMMA)
    node.init(2)
    node.setfirst(left)
    check_token_type(parser, TT_NAME)
    node.setsecond(parser.node)
    advance(parser)
    return node


def import_alias_parser_init(parser):
    symbol(parser, TT_COMMA)
    symbol(parser, TT_FROM)
    infix(parser, TT_AS, 20, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def module_name_parser_init(parser):
    symbol(parser, TT_COMMA)
    infix(parser, TT_DOT, 10, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def module_name_alias_parser_init(parser):
    symbol(parser, TT_COMMA)
    infix(parser, TT_DOT, 10, infix_simple_pair)
    infix(parser, TT_AS, 20, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def generic_signature_parser_init(parser):
    symbol(parser, TT_COMMA)
    symbol(parser, TT_LPAREN)
    symbol(parser, TT_RPAREN)
    infix(parser, TT_OF, 10, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


"""
object AliceTraits(Human, Insect, Fucking, Shit) {
    id = 42
    name = "Alice"
    object Bob(Human) {
        fn hello(self) {
            return "I am Bob"
        }
    }
    fn greetings(self) {
        return "Hello from" + self.name
    }
    goNorth = fn(self) {
        "I " + self.name + " go North"
    }
}

"""


def main_parser_init(parser):
    # *********************************************
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_NIL)
    literal(parser, TT_UNDEFINED)

    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ENDSTREAM)
    symbol(parser, TT_COLON)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_LCURLY)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_ELSE)
    symbol(parser, TT_SEMI, nud=empty)

    # precedence 5
    # infix(parser, TT_COMMA, 5)
    # infix(parser, TT_COLON, 5)

    """
    precedence 10
    = += -= *= /= %= &= ^= |=
    """
    assignment(parser, TT_ASSIGN)
    assignment(parser, TT_ADD_ASSIGN)
    assignment(parser, TT_SUB_ASSIGN)
    assignment(parser, TT_MUL_ASSIGN)
    assignment(parser, TT_DIV_ASSIGN)
    assignment(parser, TT_MOD_ASSIGN)
    assignment(parser, TT_BITOR_ASSIGN)
    assignment(parser, TT_BITAND_ASSIGN)
    assignment(parser, TT_BITXOR_ASSIGN)

    """
    precedence 20
    when
    """

    def _infix_when(parser, node, left):
        node.init(3)
        node.setfirst(condition(parser))
        node.setsecond(left)
        advance_expected(parser, TT_ELSE)
        node.setthird(expression(parser, 0))
        return node

    infix(parser, TT_WHEN, 20, _infix_when)

    """
    precedence 25
    or
    """
    infix(parser, TT_OR, 25)

    """
    precedence 30
    AND
    """
    infix(parser, TT_AND, 30)

    """
    precedence 35
    |
    """
    infixr(parser, TT_BITOR, 35)

    """
    precedence 40
    ^
    """
    infixr(parser, TT_BITXOR, 40)

    """
    precedence 45
    &
    """
    infixr(parser, TT_BITAND, 45)

    """
    precedence 50
    in, is, <, <=, >, >=, !=, ==
    """
    # TODO is not and not is

    infix(parser, TT_IN, 50)
    infix(parser, TT_ISNOT, 50)
    infix(parser, TT_IS, 50)
    infix(parser, TT_LT, 50)
    infix(parser, TT_LE, 50)
    infix(parser, TT_GT, 50)
    infix(parser, TT_GE, 50)
    infix(parser, TT_NE, 50)
    infix(parser, TT_EQ, 50)

    """
    precedence 55
    >> << >>>
    """
    infix(parser, TT_LSHIFT, 55)
    infix(parser, TT_RSHIFT, 55)
    infix(parser, TT_URSHIFT, 55)

    """
    precedence 60
    + -
    """
    infix(parser, TT_ADD, 60)
    infix(parser, TT_SUB, 60)

    """
    precedence 65
    * / %
    """
    infix(parser, TT_MUL, 65)
    infix(parser, TT_DIV, 65)
    infix(parser, TT_MOD, 65)

    """
    precedence 70
    .
    """

    def _infix_dot(parser, node, left):
        node.init(2)
        node.setfirst(left)
        check_token_type(parser, TT_NAME)
        node.setsecond(parser.node)
        advance(parser)
        return node

    infix(parser, TT_DOT, 70, _infix_dot)

    """
    precedence 80
    [
    """

    def _infix_lsquare(parser, node, left):
        node.init(2)
        node.setfirst(left)
        node.setsecond(expression(parser, 0))
        advance_expected(parser, TT_RSQUARE)
        return node

    infix(parser, TT_LSQUARE, 80, _infix_lsquare)

    """
    precedence 90
    (
    """

    def _infix_lparen(parser, node, left):
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

    infix(parser, TT_LPAREN, 90, _infix_lparen)

    """
    PREFIXES
    """

    prefix(parser, TT_ELLIPSIS)

    prefix(parser, TT_BITNOT)
    prefix(parser, TT_NOT)
    prefix(parser, TT_SUB)
    prefix(parser, TT_ADD)

    def _parse_if(parser, node):
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

    prefix(parser, TT_IF, _parse_if)

    def _prefix_lparen(parser, node):
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

    prefix(parser, TT_LPAREN, _prefix_lparen)

    def _prefix_lsquare(parser, node):
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

    prefix(parser, TT_LSQUARE, _prefix_lsquare)

    def _prefix_lcurly(parser, node):
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

    prefix(parser, TT_LCURLY, _prefix_lcurly)

    def _parse_fn(parser):
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
                parse_error(parser, "Outer variables not declared")

        body = statements(parser)
        if not body:
            body = empty_node()
        advance_expected(parser, TT_RCURLY)
        return name, args, outers, body

    def _prefix_fn(parser, node):
        node.init(3)
        name, args, outers, body = _parse_fn(parser)
        if not is_empty_node(name):
            parse_error(parser, "In expressions functions could not have names", node=node)
        node.setfirst(args)
        node.setsecond(outers)
        node.setthird(body)
        return node

    prefix(parser, TT_FN, _prefix_fn)

    def _parse_object(parser):
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

    def _prefix_object(parser, node):
        node.init(2)
        name, traits, body = _parse_object(parser)
        if not is_empty_node(name):
            parse_error(parser, "In expressions objects could not have names", node=node)
        node.setfirst(traits)
        node.setsecond(body)
        return node

    prefix(parser, TT_OBJECT, _prefix_object)

    """
    STATEMENTS
    """

    def _stmt_fn(parser, node):
        node.init(4)
        name, args, outers, body = _parse_fn(parser)
        if is_empty_node(name):
            parse_error(parser, "Function statement must be declared with name", node=node)
        node.setfirst(name)
        node.setsecond(args)
        node.setthird(outers)
        node.setfourth(body)
        return node

    stmt(parser, TT_FN, _stmt_fn)

    def _stmt_object(parser, node):
        node.init(3)
        name, traits, items = _parse_object(parser)
        # TODO move this check to parse object or add support for error token in error func
        if is_empty_node(name):
            parse_error(parser, "Object statement must have name", node=node)
        node.setfirst(name)
        node.setsecond(traits)
        node.setthird(items)
        return node

    stmt(parser, TT_OBJECT, _stmt_object)

    def _stmt_single(parser, node):
        node.init(1)
        if token_is_one_of(parser, [TT_SEMI, TT_RCURLY]) or parser.is_newline_occurred:
            node.setfirst([])
        else:
            node.setfirst(expression(parser, 0))
        endofexpression(parser)
        return node

    stmt(parser, TT_RETURN, _stmt_single)
    stmt(parser, TT_THROW, _stmt_single)

    def _stmt_outer(parser, node):
        parse_error(parser, "Outer variables can be declared only in first function statement")

    stmt(parser, TT_OUTER, _stmt_outer)

    def _stmt_loop_flow(parser, node):
        endofexpression(parser)
        if parser.token_type != TT_RCURLY:
            parse_error(parser, "Unreachable statement")
        return node

    stmt(parser, TT_BREAK, _stmt_loop_flow)
    stmt(parser, TT_CONTINUE, _stmt_loop_flow)

    def _stmt_while(parser, node):
        node.init(2)
        node.setfirst(condition(parser))
        advance_expected(parser, TT_LCURLY)
        node.setsecond(statements(parser, [TT_RCURLY]))
        advance_expected(parser, TT_RCURLY)
        return node

    stmt(parser, TT_WHILE, _stmt_while)

    def _stmt_for(parser, node):
        node.init(3)
        vars = []
        # set big lbp to overriding IN binding power
        vars.append(expression(parser, 70))
        while parser.token_type == TT_COMMA:
            advance(parser)
            if parser.token_type != TT_NAME:
                parse_error(parser, "Wrong variable name in for loop")

            vars.append(expression(parser, 0))

        node.setfirst(vars)
        advance_expected(parser, TT_IN)
        node.setsecond(expression(parser, 0))

        advance_expected(parser, TT_LCURLY)
        node.setthird(statements(parser, [TT_RCURLY]))
        advance_expected(parser, TT_RCURLY)
        return node

    stmt(parser, TT_FOR, _stmt_for)

    def _stmt_generic(parser, node):
        if parser.token_type != TT_NAME:
            parse_error(parser, "Wrong generic name")
        name = parser.node
        advance(parser)

        if parser.token_type == TT_LCURLY or parser.token_type == TT_LPAREN:
            node.init(2)
            funcs = _parse_reify_funcs(parser)
            node.setfirst(name)
            node.setsecond(funcs)
        else:
            node.init(1)
            node.setfirst(name)

        return node

    stmt(parser, TT_GENERIC, _stmt_generic)

    def _stmt_trait(parser, node):
        node.init(1)
        name = expression(parser, 0)
        if name.type != TT_NAME:
            parse_error(parser, "Wrong trait name")
        node.setfirst(name)
        return node

    stmt(parser, TT_TRAIT, _stmt_trait)

    def _parse_reify_fn(_parser, _signature_parser):
        signature = []

        advance_expected(parser, TT_LPAREN)
        while _parser.token_type != TT_RPAREN:
            sig = expression(_signature_parser, 0)
            signature.append(sig)

            if _parser.token_type != TT_COMMA:
                break

            advance_expected(_signature_parser, TT_COMMA)

        advance_expected(_parser, TT_RPAREN)
        advance_expected(parser, TT_LCURLY)

        body = statements(parser)
        # TODO FIX IT
        if not body:
            body = empty_node()

        advance_expected(parser, TT_RCURLY)
        return [signature, body]

    def _parse_reify_funcs(parser):
        generic_signature_parser = parser.generic_signature_parser
        funcs = []
        if parser.token_type == TT_LPAREN:
            func = _parse_reify_fn(parser, generic_signature_parser)
            funcs.append(func)
        else:
            advance_expected(parser, TT_LCURLY)
            while parser.token_type == TT_LPAREN:
                func = _parse_reify_fn(parser, generic_signature_parser)
                funcs.append(func)

            advance_expected(parser, TT_RCURLY)

        if len(funcs) == 0:
            parse_error(parser, "Empty reify statement")

        return funcs

    def _stmt_reify(parser, node):
        node.init(2)

        if parser.token_type != TT_NAME:
            parse_error(parser, "Wrong generic name in reify statement")

        name = parser.node
        advance(parser)

        funcs = _parse_reify_funcs(parser)

        node.setfirst(name)
        node.setsecond(funcs)
        return node

    stmt(parser, TT_REIFY, _stmt_reify)

    def _stmt_import(parser, node):
        # import statement needs three different parsers :(

        # all parsers share same token stream and token_type checks can be made for any of them
        module_name_parser = parser.module_name_parser
        module_name_alias_parser = parser.module_name_alias_parser
        import_alias_parser = parser.import_alias_parser

        # first statement can be import x.y.z as c
        imported = expression(module_name_alias_parser, 0)
        # destructuring import x as y from a.b.c
        if parser.token_type == TT_COMMA or parser.token_type == TT_FROM:
            items = [imported]

            # aliases like x as y
            while parser.token_type == TT_COMMA:
                advance(parser)
                items.append(expression(import_alias_parser, 0))

            advance_expected(module_name_parser, TT_FROM)
            # module name x.y.z
            module = expression(module_name_parser, 0)
            node.init(2)
            node.setfirst(items)
            node.setsecond(module)
        # simple import x.y.z as c
        else:
            node.init(1)
            node.setfirst(imported)

        return node

    stmt(parser, TT_IMPORT, _stmt_import)
    return parser


"""
import fire as army_fire, Weapon as weapon, private as army_private from state.military

import military.army.behavior as bh
print(bh)
import military.army.behavior
print(behavior)
print(fire, army_unit_destroy, army_unit_attack)


"""


def parse(parser):
    parser.next()
    stmts = statements(parser)
    check_token_type(parser, TT_ENDSTREAM)
    return stmts


def parser_from_str(txt):
    lx = obin.compile.lexer.lexer(txt)
    tokens = lx.tokens()
    ts = TokenStream(tokens)
    parser = Parser(ts)
    return parser


def parse_string(txt):
    parser = parser_from_str(txt)
    stmts = parse(parser)
    # print stmts
    return stmts


def write_ast(ast):
    import json
    if not isinstance(ast, list):
        ast = [ast.to_dict()]
    else:
        ast = [node.to_dict() for node in ast]
    with open("output.json", "w") as f:
        repr = json.dumps(ast, sort_keys=True,
                          indent=2, separators=(',', ': '))
        f.write(repr)

# ast = parse_string(
#     """
#     reify fire {
#         (self of Soldier, other of Civilian) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#         (self of Soldier, other1, other2) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#         (self, other1, other2, other3 of Enemy) {
#             attack(self, other)
#             name = self.name
#             surname = "Surname" + name + other.name
#         }
#     }
#     """
# )
# print ast
# write_ast(ast)
