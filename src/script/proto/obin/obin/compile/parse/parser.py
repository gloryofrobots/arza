__author__ = 'gloryofrobots'
import obin.compile.rlexer as lexer
from obin.compile.parse.token_type import *
from obin.compile.parse.node import Node, is_empty_node, empty_node
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.basic import *
from obin.compile.parse.expression_handlers import *


class BaseParser:
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
        BaseParser.__init__(self, ts)
        self.args_parser = args_parser_init(BaseParser(ts))
        self.module_name_parser = module_name_parser_init(BaseParser(ts))
        self.module_name_alias_parser = module_name_alias_parser_init(BaseParser(ts))
        self.generic_signature_parser = generic_signature_parser_init(BaseParser(ts))
        # self.expression_parser = expression_parser_init(BaseParser(ts))
        main_parser_init(self)


def args_parser_init(parser):
    prefix(parser, TT_ELLIPSIS)
    prefix(parser, TT_LPAREN, prefix_lparen_arguments)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)

    symbol(parser, TT_COMMA)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_COLON)
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
    symbol(parser, TT_CASE)
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
    literal(parser, TT_BACKTICK)
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
    symbol(parser, TT_END)
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

    infix(parser, TT_WHEN, 20, infix_when)

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

    infix(parser, TT_DOT, 70, infix_dot)
    # infixr(parser, TT_COLON, 70)

    """
    precedence 80
    [
    """

    infix(parser, TT_LSQUARE, 80, infix_lsquare)

    """
    precedence 90
    (
    """
    infix(parser, TT_LPAREN, 90, infix_lparen)

    """
    PREFIXES
    """

    prefix(parser, TT_BITNOT)
    prefix(parser, TT_NOT)
    prefix(parser, TT_SUB)
    prefix(parser, TT_ADD)

    prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_LPAREN, prefix_lparen)

    prefix(parser, TT_LSQUARE, prefix_lsquare)

    prefix(parser, TT_LCURLY, prefix_lcurly)

    prefix(parser, TT_FUNC, prefix_func)

    prefix(parser, TT_IMPORT, prefix_import)

    """
    STATEMENTS
    """

    stmt(parser, TT_ORIGIN, stmt_origin)

    stmt(parser, TT_RETURN, stmt_single)
    stmt(parser, TT_THROW, stmt_single)

    stmt(parser, TT_OUTER, stmt_outer)

    stmt(parser, TT_BREAK, stmt_loop_flow)
    stmt(parser, TT_CONTINUE, stmt_loop_flow)

    stmt(parser, TT_WHILE, stmt_while)

    stmt(parser, TT_FOR, stmt_for)

    stmt(parser, TT_GENERIC, stmt_generic)

    stmt(parser, TT_TRAIT, stmt_trait)

    stmt(parser, TT_REIFY, stmt_reify)

    stmt(parser, TT_IMPORT, stmt_import)
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
    lx = lexer.lexer(txt)
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
#     func: end
#     """
# )
"""
    func(x, (y,z), a, b,
        {name=name, age=(years, month)},
         ...rest):
        return age
    end
"""
# print ast
# write_ast(ast)
