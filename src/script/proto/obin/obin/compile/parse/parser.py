__author__ = 'gloryofrobots'
import obin.compile.parse.lexer as lexer
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.callbacks import *
from obin.compile.parse.lexer import UnknownTokenError
from obin.compile.parse import tokens
from obin.types import api, space, plist, root, environment


# additional helpers
def infix_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infix_function, infix_function)


def infixr_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infixr_function, infix_function)


def prefix_operator(parser, ttype, prefix_function):
    op = get_or_create_operator(parser, ttype)
    operator_prefix(op, prefix_nud_function, prefix_function)


def infixr(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr)


def assignment(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr_assign)


class BaseParser:
    def __init__(self):
        self.handlers = {}
        self.state = None
        self.allow_overloading = False

    def open(self, state):
        assert self.state is None
        self.state = state
        self._on_open(state)

    def _on_open(self, state):
        pass

    def close(self):
        state = self.state
        self.state = None
        self._on_close()
        return state

    def _on_close(self):
        pass

    @property
    def ts(self):
        return self.state.ts

    @property
    def token_type(self):
        return tokens.token_type(self.ts.token)

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
        try:
            return self.ts.next()
        except UnknownTokenError as e:
            parser_error_unknown(self, e.position)

    def isend(self):
        return self.token_type == TT_ENDSTREAM



class ExpressionParser(BaseParser):
    def __init__(self, proc_data):
        BaseParser.__init__(self)
        self.pattern_parser = pattern_parser_init(BaseParser())
        self.guard_parser = guard_parser_init(proc_data, BaseParser())
        self.name_parser = name_parser_init(BaseParser())
        expression_parser_init(proc_data, base_parser_init(self))

    def _on_open(self, state):
        self.pattern_parser.open(state)
        self.guard_parser.open(state)
        self.name_parser.open(state)

    def _on_close(self):
        self.pattern_parser.close()
        self.guard_parser.close()
        self.name_parser.close()


class ModuleParser(BaseParser):
    def __init__(self, proc_data):
        BaseParser.__init__(self)

        self.load_parser = load_parser_init(BaseParser())
        self.generic_signature_parser = generic_signature_parser_init(BaseParser())
        self.pattern_parser = pattern_parser_init(BaseParser())
        self.guard_parser = guard_parser_init(proc_data, BaseParser())
        self.expression_parser = ExpressionParser(proc_data)
        self.name_parser = name_parser_init(BaseParser())
        self.import_names_parser = import_names_parser_init(BaseParser())

        module_parser_init(base_parser_init(self))

    def _on_open(self, state):
        self.pattern_parser.open(state)
        self.guard_parser.open(state)
        self.generic_signature_parser.open(state)
        self.load_parser.open(state)
        self.expression_parser.open(state)
        self.name_parser.open(state)
        self.import_names_parser.open(state)

    def _on_close(self):
        self.pattern_parser.close()
        self.guard_parser.close()
        self.generic_signature_parser.close()
        self.load_parser.close()
        self.expression_parser.close()
        self.name_parser.close()
        self.import_names_parser.close()


def name_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    literal(parser, TT_NAME)
    literal(parser, TT_INT)

    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_BACKTICK, prefix_backtick)
    infix(parser, TT_COLON, 10, infix_name_pair)
    return parser


def import_names_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    literal(parser, TT_NAME)
    infix(parser, TT_AS, 20, infix_name_pair)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    return parser


def load_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    infix(parser, TT_COLON, 10, infix_name_pair)
    infix(parser, TT_AS, 20, infix_name_pair)
    literal(parser, TT_NAME)

    return parser


def generic_signature_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_LPAREN, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_CASE, None)
    infix(parser, TT_OF, 10, infix_name_pair)
    literal(parser, TT_NAME)
    return parser


def guard_parser_init(proc_data, parser):
    from obin.builtins import prelude
    parser.allow_overloading = True
    parser = init_parser_literals(parser)

    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ARROW, None)

    prefix(parser, TT_LPAREN, prefix_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)

    prefix_operator(parser, TT_NOT, proc_data.std.generics.not_.name)

    infix(parser, TT_DOT, 70, infix_dot)
    infix(parser, TT_COLON, 80, infix_name_pair)
    infix(parser, TT_LPAREN, 90, infix_lparen)
    infix(parser, TT_OR, 25, led_infix)
    infix(parser, TT_AND, 30, led_infix)

    infix_operator(parser, TT_KINDOF, 50, proc_data.symbols.symbol_s(prelude.PRIM_KINDOF))
    infix_operator(parser, TT_IS, 50, proc_data.symbols.symbol_s(prelude.PRIM_IS))
    infix_operator(parser, TT_ISNOT, 50, proc_data.symbols.symbol_s(prelude.PRIM_ISNOT))
    infix_operator(parser, TT_IN, 50, proc_data.std.generics.in_.name)
    infix_operator(parser, TT_NOTIN, 50, proc_data.std.generics.notin.name)
    return parser


def pattern_parser_init(parser):
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly_patterns)
    prefix(parser, TT_SHARP, prefix_sharp)

    infix(parser, TT_OF, 10, led_infix)
    infix(parser, TT_AT_SIGN, 10, infix_at)

    symbol(parser, TT_CASE, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ARROW, None)
    symbol(parser, TT_ASSIGN, None)

    parser = init_parser_literals(parser)
    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_NIL)
    literal(parser, TT_WILDCARD)
    return parser


def base_parser_init(parser):
    parser = init_parser_literals(parser)

    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ENDSTREAM, None)
    symbol(parser, TT_ARROW, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_LCURLY, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_END, None)
    symbol(parser, TT_ELSE, None)
    symbol(parser, TT_SEMI, None)

    # 10
    assignment(parser, TT_ASSIGN, 10)
    # 70
    infix(parser, TT_DOT, 70, infix_dot)

    infix(parser, TT_COLON, 80, infix_name_pair)

    prefix(parser, TT_LPAREN, prefix_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)

    return parser


def expression_parser_init(proc_data, parser):
    parser.allow_overloading = True
    # OTHER OPERATORS ARE DECLARED IN PRELUDE
    from obin.builtins import prelude

    # 20
    infix(parser, TT_WHEN, 20, infix_when)

    # 25
    infix(parser, TT_OR, 25, led_infix)

    # 30
    infix(parser, TT_AND, 30, led_infix)

    # 50
    infix_operator(parser, TT_ISA, 50, proc_data.symbols.symbol_s(prelude.PRIM_ISA))
    infix_operator(parser, TT_NOTA, 50, proc_data.symbols.symbol_s(prelude.PRIM_NOTA))
    infix_operator(parser, TT_KINDOF, 50, proc_data.symbols.symbol_s(prelude.PRIM_KINDOF))

    infix_operator(parser, TT_IS, 50, proc_data.symbols.symbol_s(prelude.PRIM_IS))
    infix_operator(parser, TT_ISNOT, 50, proc_data.symbols.symbol_s(prelude.PRIM_ISNOT))

    infix_operator(parser, TT_IN, 50, proc_data.std.generics.in_.name)
    infix_operator(parser, TT_NOTIN, 50, proc_data.std.generics.notin.name)

    infix(parser, TT_DOT, 70, infix_dot)

    # 80
    infix(parser, TT_LCURLY, 80, infix_lcurly)
    infix(parser, TT_LSQUARE, 80, infix_lsquare)

    # 90
    infix(parser, TT_LPAREN, 90, infix_lparen)

    """
    PREFIXES
    """
    prefix(parser, TT_BACKTICK, prefix_backtick)
    prefix_operator(parser, TT_NOT, proc_data.std.generics.not_.name)

    prefix(parser, TT_THROW, stmt_single)
    prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_FUN, prefix_fun)

    prefix(parser, TT_MATCH, prefix_match)
    prefix(parser, TT_TRY, prefix_try)

    """
    STATEMENTS
    """

    stmt(parser, TT_RETURN, stmt_single)
    stmt(parser, TT_BREAK, stmt_loop_flow)
    stmt(parser, TT_CONTINUE, stmt_loop_flow)
    stmt(parser, TT_WHILE, stmt_while)
    stmt(parser, TT_FOR, stmt_for)
    stmt(parser, TT_WHEN, stmt_when)

    return parser


def module_parser_init(parser):
    stmt(parser, TT_GENERIC, stmt_generic)
    stmt(parser, TT_TRAIT, stmt_trait)
    stmt(parser, TT_SPECIFY, stmt_specify)
    stmt(parser, TT_IMPORT, stmt_import)
    stmt(parser, TT_EXPORT, stmt_export)
    stmt(parser, TT_MODULE, stmt_module)

    stmt(parser, TT_AT_SIGN, stmt_module_at)
    prefix(parser, TT_DEF, prefix_def)
    return parser


def newparser(proc_data):
    parser = ModuleParser(proc_data)
    return parser


def newtokenstream(source):
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return TokenStream(tokens_iter, source)


def parse(process, env, src):
    parser = process.parser
    ts = newtokenstream(src)
    parser.open(ParseState(process, env, ts))

    parser.next()
    stmts, scope = parse_env_statements(parser, TERM_FILE)
    assert plist.is_empty(parser.state.scopes)
    check_token_type(parser, TT_ENDSTREAM)

    parser.close()
    # print stmts
    return stmts, scope


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


def __parse__():
    from obin.runtime.engine import newprocess
    source = """
        @infixl(`-`, `-`, 60)
        @infixl(`>=`, `>=`, 50)
        @infixl(`==`, `==`, 50)
        @infixl(`+`, `+`, 60)
        @infixl(`-`, `-`, 60)
        @infixl(`%`, `%`, 65)
        @infixl(`*`, `*`, 65)
        @infixl(`/`, `/`, 65)
        @infixr(`::`, `::`, 70)
        @infixl(`!=`, `!=`, 70)


        def main ->
        A = false
        match (1,2,3)
            case (x, y, z) when z == 2 -> #first
            case (x, y, z) when z == 3 and y == 3 -> #second
            case (x, y, z) when z == 3 and y == 2 and x == 3 -> #third
            case (x, y, z) when z == 3 and y == 2 and x == 1 and A == 2 -> #fourth
            case (x, y, z) when z == 3 and y == 2 and x == 1 and not A is true -> #fifth
            case _ -> 12
        end
        end
    """
    import os
    script_dir = os.path.dirname(os.path.realpath(__file__))
    lib_path = os.path.realpath(os.path.join(script_dir, '../../../test/obin/__lib__'))
    process = newprocess([lib_path])

    ast, scope = parse(process, None, source)
    print "************************** OPERATORS ****************************************"
    print scope.operators
    print "************************** AST ****************************************"
    print nodes.node_to_string(ast)


# TODO DOUBLE DOT AS RANGE

if __name__ == "__main__":
    __parse__()

# ast = parse_string(
#     """
#     module M
#         def main() ->
#             when 2 == 2
#                  false end
#         end
#     ;
#     """
# )
# print nodes.node_to_string(ast)
"""
    A[1..];
    A[2..3];
    A[..];
    A[..4];
    A[5];
"""
"""
import lib_az:abc:module_ab as ab (cons, length)
import lib_az:abc:module_ab as ab2
import lib_az:abc:module_ab
import from lib_az:abc:module_ab
import from lib_az:abc:module_ab as ab (cons, length)
import from lib_az:abc:module_ab as ab hiding (cons, length)
import lib_az:abc:module_ab as ab hiding (cons, length)
"""
