__author__ = 'gloryofrobots'
import obin.compile.rlexer as lexer
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.callbacks import *


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
        self.pattern_parser = pattern_parser_init(BaseParser(ts))
        # self.expression_parser = expression_parser_init(BaseParser(ts))
        main_parser_init(self)


def args_parser_init(parser):
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)

    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_COLON, None)
    literal(parser, TT_NAME)
    return parser


def infix_simple_pair(parser, node, left):
    symbol(parser, TT_COMMA, None)
    node.init(2)
    node.setfirst(left)
    check_token_type(parser, TT_NAME)
    node.setsecond(parser.node)
    advance(parser)
    return node


def module_name_parser_init(parser):
    symbol(parser, TT_COMMA,  None)
    infix(parser, TT_DOT,  10, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def module_name_alias_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    infix(parser, TT_DOT, 10, infix_simple_pair)
    infix(parser, TT_AS, 20, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def generic_signature_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_LPAREN, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_CASE, None)
    infix(parser, TT_OF,  10, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def pattern_parser_init(parser):
    prefix(parser, TT_ELLIPSIS,  prefix_nud)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE,   prefix_lsquare)
    prefix(parser, TT_LCURLY,  prefix_lcurly)

    infix(parser, TT_OF, 10, infix_simple_pair)

    symbol(parser, TT_CASE, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_COLON, None)

    literal(parser, TT_NAME)
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_NIL)
    literal(parser, TT_UNDEFINED)
    literal(parser, TT_WILDCARD)
    return parser


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


    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ENDSTREAM, None)
    symbol(parser, TT_COLON, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_LCURLY, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_END, None)
    symbol(parser, TT_ELSE, None)
    symbol(parser, TT_SEMI, empty)
    symbol(parser, TT_WILDCARD, nud_wildcard)

    # precedence 5
    # infix(parser, TT_COMMA, 5)

    """
    precedence 10
    = += -= *= /= %= &= ^= |=
    """
    infixr(parser, TT_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_ADD_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_SUB_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_MUL_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_DIV_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_MOD_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_BITOR_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_BITAND_ASSIGN, 10, led_infixr_assign)
    infixr(parser, TT_BITXOR_ASSIGN, 10, led_infixr_assign)

    """
    precedence 20
    when
    """

    infix(parser, TT_WHEN, 20, infix_when)

    """
    precedence 25
    or
    """
    infix(parser, TT_OR, 25, led_infix)

    """
    precedence 30
    AND
    """
    infix(parser, TT_AND, 30, led_infix)
    """
    precedence 35
    |
    """
    infixr(parser, TT_BITOR,  35, led_infixr)

    """
    precedence 40
    ^
    """
    infixr(parser, TT_BITXOR,  40, led_infixr)

    """
    precedence 45
    &
    """
    infixr(parser, TT_BITAND, 45, led_infixr)

    """
    precedence 50
    in, is, <, <=, >, >=, !=, ==
    """
    # TODO is not and not in

    infix(parser, TT_ISNOT, 50, led_infix)
    infix(parser, TT_IN, 50, led_infix)
    infix(parser, TT_IS, 50, led_infix)
    infix(parser, TT_LT, 50, led_infix)
    infix(parser, TT_LE, 50, led_infix)
    infix(parser, TT_GT, 50, led_infix)
    infix(parser, TT_GE, 50, led_infix)
    infix(parser, TT_NE, 50, led_infix)
    infix(parser, TT_EQ, 50, led_infix)

    """
    precedence 55
    >> << >>>
    """
    infix(parser, TT_LSHIFT, 55, led_infix)
    infix(parser, TT_RSHIFT, 55, led_infix)
    infix(parser, TT_URSHIFT, 55, led_infix)

    """
    precedence 60
    + -
    """
    infix(parser, TT_ADD, 60, led_infix)
    infix(parser, TT_SUB, 60, led_infix)

    """
    precedence 65
    * / %
    """
    infix(parser, TT_MUL, 65, led_infix)
    infix(parser, TT_DIV, 65, led_infix)
    infix(parser, TT_MOD, 65, led_infix)

    """
    precedence 70
    .
    """

    infix(parser, TT_DOT, 70, infix_dot)
    infixr(parser, TT_DOUBLE_COLON, 70, led_infixr)

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

    prefix(parser, TT_BITNOT, prefix_nud)
    prefix(parser, TT_NOT, prefix_nud)
    prefix(parser, TT_SUB, prefix_unary_minus)
    prefix(parser, TT_ADD, prefix_unary_plus)

    prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_LPAREN, prefix_lparen)

    prefix(parser, TT_LSQUARE, prefix_lsquare)

    prefix(parser, TT_LCURLY, prefix_lcurly)

    prefix(parser, TT_FUNC, prefix_func)

    prefix(parser, TT_IMPORT, prefix_import)
    prefix(parser, TT_MATCH, prefix_match)

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

    stmt(parser, TT_SPECIFY, stmt_specify)

    stmt(parser, TT_IMPORT, stmt_import)
    return parser


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


ast = parse_string(
"""
$[0][1]['name'][2]

//2 name 1 0 $

"""

)
"""
match (a,b):
    case (true, b):
        1 + 1
    end
    case ({name="Bob", surname="Alice"}, (1,2)): 2 + 2 end
    case 42: 3 + 3 end
    case _: nil end
end
"""
# print ast
# write_ast(ast)
