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
        # TODO REMOVE IT
        self.break_on_juxtaposition = False

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
        self.fun_signature_parser = fun_signature_parser_init(BaseParser())
        self.name_parser = name_parser_init(BaseParser())
        expression_parser_init(proc_data, base_parser_init(self))

    def _on_open(self, state):
        self.pattern_parser.open(state)
        self.fun_signature_parser.open(state)
        self.guard_parser.open(state)
        self.name_parser.open(state)

    def _on_close(self):
        self.pattern_parser.close()
        self.fun_signature_parser.close()
        self.guard_parser.close()
        self.name_parser.close()


class ModuleParser(BaseParser):
    def __init__(self, proc_data):
        BaseParser.__init__(self)

        self.import_parser = import_parser_init(BaseParser())
        self.pattern_parser = pattern_parser_init(BaseParser())
        self.fun_signature_parser = fun_signature_parser_init(BaseParser())
        self.guard_parser = guard_parser_init(proc_data, BaseParser())
        self.expression_parser = ExpressionParser(proc_data)
        self.name_parser = name_parser_init(BaseParser())
        self.import_names_parser = import_names_parser_init(BaseParser())
        self.type_parser = type_parser_init(BaseParser())
        self.method_signature_parser = method_signature_parser_init(BaseParser())

        module_parser_init(base_parser_init(self))

    def _on_open(self, state):
        self.method_signature_parser.open(state)
        self.type_parser.open(state)
        self.pattern_parser.open(state)
        self.fun_signature_parser.open(state)
        self.guard_parser.open(state)
        self.import_parser.open(state)
        self.expression_parser.open(state)
        self.name_parser.open(state)
        self.import_names_parser.open(state)

    def _on_close(self):
        self.method_signature_parser.close()
        self.type_parser.close()
        self.pattern_parser.close()
        self.fun_signature_parser.close()
        self.guard_parser.close()
        self.import_parser.close()
        self.expression_parser.close()
        self.name_parser.close()
        self.import_names_parser.close()


def name_parser_init(parser):
    parser.break_on_juxtaposition = True
    symbol(parser, TT_COMMA, None)
    # symbol(parser, TT_WILDCARD, None)
    symbol(parser, TT_RPAREN, None)
    init_parser_literals(parser)
    symbol(parser, TT_CASE, None)
    symbol(parser, TT_ELLIPSIS, None)

    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    symbol(parser, TT_OPERATOR, symbol_operator_name)
    infix(parser, TT_COLON, 80, infix_name_pair)
    return parser


def type_parser_init(parser):
    parser.break_on_juxtaposition = True
    # literal(parser, TT_TYPENAME)
    prefix(parser, TT_NAME, prefix_name_as_symbol)
    infix(parser, TT_COLON, 80, infix_name_pair)
    symbol(parser, TT_CASE, None)
    symbol(parser, TT_CONSTRUCT, None)
    return parser


def method_signature_parser_init(parser):
    parser.break_on_juxtaposition = True
    prefix(parser, TT_NAME, prefix_name_as_symbol)
    symbol(parser, TT_METHOD, None)
    symbol(parser, TT_ARROW, None)
    symbol(parser, TT_JUXTAPOSITION)
    return parser

def import_names_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_RPAREN, None)
    literal(parser, TT_NAME)
    infix(parser, TT_AS, 20, infix_name_pair)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    return parser


def import_parser_init(parser):
    symbol(parser, TT_COMMA, None)
    symbol(parser, TT_LPAREN, None)
    symbol(parser, TT_HIDING, None)
    infix(parser, TT_COLON, 80, infix_name_pair)
    infix(parser, TT_AS, 20, infix_name_pair)
    literal(parser, TT_NAME)

    return parser


def guard_parser_init(proc_data, parser):
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

    infix(parser, TT_BACKTICK, 50, infix_backtick)
    infix(parser, TT_DOT, 70, infix_dot)
    infix(parser, TT_COLON, 80, infix_name_pair)
    infix(parser, TT_OR, 25, led_infix)
    infix(parser, TT_AND, 30, led_infix)
    infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    return parser


def pattern_parser_init(parser):
    parser.break_on_juxtaposition = True

    # infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly_patterns)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_ELLIPSIS, prefix_nud)

    infix(parser, TT_DOUBLE_COLON, 70, led_infixr)
    infix(parser, TT_OF, 10, led_infix)
    infix(parser, TT_AT_SIGN, 10, infix_at)
    infix(parser, TT_COLON, 80, infix_name_pair)

    symbol(parser, TT_JUXTAPOSITION)
    symbol(parser, TT_WHEN)
    symbol(parser, TT_CASE)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_ASSIGN)

    parser = init_parser_literals(parser)
    return parser

def fun_signature_parser_init(parser):
    parser.break_on_juxtaposition = True
    literal(parser, TT_NAME)
    infix(parser, TT_OF, 10, led_infix)

    prefix(parser, TT_LPAREN, prefix_lparen_unit)
    prefix(parser, TT_ELLIPSIS, prefix_nud)
    infix(parser, TT_COLON, 80, infix_name_pair)

    literal(parser, TT_WILDCARD)
    symbol(parser, TT_METHOD, None)
    symbol(parser, TT_ARROW, None)
    symbol(parser, TT_CASE, None)
    symbol(parser, TT_JUXTAPOSITION)
    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_TYPENAME)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_WILDCARD)
    return parser


def base_parser_init(parser):
    parser = init_parser_literals(parser)

    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ENDSTREAM)
    symbol(parser, TT_ARROW)
    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_COMMA)
    symbol(parser, TT_END)
    symbol(parser, TT_SEMI)

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
    # OTHER OPERATORS ARE DECLARED IN prelude.obn

    # support for destructive assignments, would work only in assignment expressions
    infix(parser, TT_OF, 10, led_infix)
    symbol(parser, TT_AT_SIGN, None)
    prefix(parser, TT_ELLIPSIS, prefix_nud)

    symbol(parser, TT_ELSE)
    symbol(parser, TT_CASE)
    symbol(parser, TT_THEN)

    symbol(parser, TT_COMMA)

    infix(parser, TT_IF, 20, infix_if)

    infix(parser, TT_OR, 25, led_infix)

    infix(parser, TT_AND, 30, led_infix)

    infix(parser, TT_BACKTICK, 50, infix_backtick)

    infix(parser, TT_DOUBLE_COLON, 70, infix_double_colon)
    infix(parser, TT_JUXTAPOSITION, 90, infix_juxtaposition)
    infix(parser, TT_DOT, 95, infix_dot)

    infix(parser, TT_INFIX_DOT_LCURLY, 95, infix_lcurly)
    infix(parser, TT_INFIX_DOT_LPAREN, 95, infix_lparen)


    """
    PREFIXES
    """
    prefix(parser, TT_AMP, prefix_amp)
    prefix(parser, TT_THROW, stmt_single)
    prefix(parser, TT_CONDITION, prefix_condition)
    # PREFIX IF IS NOT SUPPORTED BECAUSE OF PROBLEM WITH END BLOCK
    # CONSIDER if False then 1 else 0 42
    # HERE RESULT WILL BE 42 not 0
    # prefix(parser, TT_IF, prefix_if)

    prefix(parser, TT_FUN, prefix_fun)
    prefix(parser, TT_LAMBDA, prefix_lambda)

    prefix(parser, TT_MATCH, prefix_match)
    prefix(parser, TT_TRY, prefix_try)

    """
    STATEMENTS
    """

    stmt(parser, TT_BREAK, stmt_loop_flow)
    stmt(parser, TT_CONTINUE, stmt_loop_flow)
    stmt(parser, TT_WHEN, stmt_when)
    return parser


def module_parser_init(parser):
    stmt(parser, TT_FUN, prefix_module_fun)

    stmt(parser, TT_TRAIT, stmt_trait)
    stmt(parser, TT_TYPE, stmt_type)
    stmt(parser, TT_IMPLEMENT, stmt_implement)
    stmt(parser, TT_DERIVE, stmt_derive)

    stmt(parser, TT_IMPORT, stmt_import)
    stmt(parser, TT_EXPORT, stmt_export)
    # stmt(parser, TT_MODULE, stmt_module)

    stmt(parser, TT_INFIXL, stmt_infixl)
    stmt(parser, TT_INFIXR, stmt_infixr)
    stmt(parser, TT_PREFIX, stmt_prefix)
    return parser


def newparser(proc_data):
    parser = ModuleParser(proc_data)
    return parser


def newtokenstream(source):
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return TokenStream(tokens_iter, source)


PARSE_DEBUG = False


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
    if PARSE_DEBUG:
        print "************************** OPERATORS ****************************************"
        print scope.operators
        print "************************** AST ****************************************"
        ast = str(nodes.node_to_string(stmts))
        f = open('ast.json', 'w')
        f.write(ast)
        f.close()
        raise SystemExit()

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
