__author__ = 'gloryofrobots'
import obin.compile.parse.lexer as lexer
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.callbacks import *
from obin.compile.parse.lexer import UnknownTokenError
from obin.compile.parse import tokens


# additional helpers
def infixr(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr)


def assignment(parser, ttype, lbp):
    infix(parser, ttype, lbp, led_infixr_assign)


class BaseParser:
    def __init__(self):
        self.handlers = {}
        self.ts = None
        self.process = None
        self.env = None

    def open(self, process, env, ts):
        assert self.ts is None
        assert self.process is None
        assert self.env is None
        self.ts = ts
        self.process = process
        self.env = env
        self._on_open(process, env, ts)

    def _on_open(self, process, env, ts):
        pass

    def close(self):
        self.ts = None
        self.process = None
        self.env = None
        self._on_close()

    def _on_close(self):
        pass

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
    def __init__(self):
        BaseParser.__init__(self)
        self.args_parser = args_parser_init(BaseParser())
        self.pattern_parser = pattern_parser_init(BaseParser())
        # self.expression_parser = expression_parser_init(BaseParser(ts))
        expression_parser_init(base_parser_init(self))

    def _on_open(self, process, env, ts):
        self.args_parser.open(process, env, ts)
        self.pattern_parser.open(process, env, ts)

    def _on_close(self):
        self.args_parser.close()
        self.pattern_parser.close()

class ModuleParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.args_parser = args_parser_init(BaseParser())
        self.load_parser = load_parser_init(BaseParser())
        self.generic_signature_parser = generic_signature_parser_init(BaseParser())
        self.pattern_parser = pattern_parser_init(BaseParser())
        self.expression_parser = ExpressionParser()

        module_parser_init(base_parser_init(self))

    def _on_open(self, process, env, ts):
        self.args_parser.open(process, env, ts)
        self.pattern_parser.open(process, env, ts)
        self.generic_signature_parser.open(process, env, ts)
        self.expression_parser.open(process, env, ts)
        self.load_parser.open(process, env, ts)

    def _on_close(self):
        self.args_parser.close()
        self.pattern_parser.close()
        self.generic_signature_parser.close()
        self.expression_parser.close()
        self.load_parser.close()

def args_parser_init(parser):
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)

    symbol(parser, TT_ASSIGN, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_ARROW, None)
    literal(parser, TT_NAME)
    return parser


def load_parser_init(parser):
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
    infix(parser, TT_OF, 10, infix_simple_pair)
    literal(parser, TT_NAME)
    return parser


def pattern_parser_init(parser):
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly_patterns)
    prefix(parser, TT_COLON, prefix_colon)

    infix(parser, TT_OF, 10, led_infix)
    infix(parser, TT_AT_SIGN, 10, infix_at)

    symbol(parser, TT_CASE, None)
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ARROW, None)
    symbol(parser, TT_ASSIGN, None)

    literal(parser, TT_NAME)
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_NIL)
    literal(parser, TT_WILDCARD)
    return parser


def base_parser_init(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_BACKTICK)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_NIL)
    literal(parser, TT_WILDCARD)

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

    assignment(parser, TT_ASSIGN, 10)
    infix(parser, TT_DOT, 70, infix_dot)

    prefix(parser, TT_LPAREN, prefix_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)
    prefix(parser, TT_COLON, prefix_colon)

    return parser


def expression_parser_init(parser):
    # OTHER OPERATORS ARE DECLARED IN PRELUDE

    # 20
    infix(parser, TT_WHEN, 20, infix_when)

    # 25
    infix(parser, TT_OR, 25, led_infix)

    # 30
    infix(parser, TT_AND, 30, led_infix)

    # 50
    infix(parser, TT_ISA, 50, led_infix)
    infix(parser, TT_NOTA, 50, led_infix)
    infix(parser, TT_KINDOF, 50, led_infix)

    # 70
    infix(parser, TT_DOT, 70, infix_dot)

    # 75
    infix(parser, TT_DOUBLE_DOT, 75, led_infix)

    # 80
    infix(parser, TT_LCURLY, 80, infix_lcurly)
    infix(parser, TT_LSQUARE, 80, infix_lsquare)

    # 90
    infix(parser, TT_LPAREN, 90, infix_lparen)

    """
    PREFIXES
    """

    prefix(parser, TT_NOT, prefix_nud)

    prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_FUN, prefix_fun)

    prefix(parser, TT_MATCH, prefix_match)
    prefix(parser, TT_TRY, prefix_try)

    """
    STATEMENTS
    """

    stmt(parser, TT_OPERATOR, stmt_operator)

    stmt(parser, TT_RETURN, stmt_single)
    stmt(parser, TT_THROW, stmt_single)
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
    stmt(parser, TT_LOAD, stmt_load)
    stmt(parser, TT_MODULE, stmt_module)

    prefix(parser, TT_DEF, prefix_def)
    return parser


def newparser():
    parser = ModuleParser()
    return parser


def newstream(source):
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return TokenStream(tokens_iter, source)


def _parse(parser):
    parser.next()
    stmts = statements(parser, TERM_FILE)
    check_token_type(parser, TT_ENDSTREAM)
    return stmts


def parse(process, env, src):
    parser = process.parser
    ts = newstream(src)
    parser.open(process, env, ts)
    stmts = _parse(parser)
    parser.close()
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
match (a,b):
    case (true, b):
        1 + 1
    end
    case ({name="Bob", surname="Alice"}, (1,2)): 2 + 2 end
    case 42: 3 + 3 end
    case _: nil end
end
"""
"""
    A[1..];
    A[2..3];
    A[..];
    A[..4];
    A[5];
"""
