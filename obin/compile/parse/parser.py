__author__ = 'gloryofrobots'
from obin.compile.parse.tokenstream import TokenStream
from obin.compile.parse.callbacks import *
from obin.compile.parse.lexer import UnknownTokenError
from obin.compile.parse import tokens
from obin.types import api, space, plist, root, environment

if tokens.RPLY:
    import obin.compile.parse.lexer as lexer
else:
    import obin.compile.parse.lexer2 as lexer

""" GOLANG PRECEDENCES. SOURCE OF INSPIRATION
Precedence    Operator
    5             *  /  %  <<  >>  &  &^
    4             +  -  |  ^
    3             ==  !=  <  <=  >  >=
    2             &&
    1             ||
"""
"""
OBIN PRECEDENCES
Precedence    Operator
    100           : . .{ .(
    95           JUXTAPOSITION
    60           :: :::
    50           *  /
    40           +  - ++
    35           ==  !=  <  <=  >  >=
    30           and
    25           or << >>
    20           |>
    15           " ."  as of <|
    10           = := @
"""


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


# def assignment(parser, ttype, lbp):
#     infix(parser, ttype, lbp, led_infixr_assign)


class BaseParser:
    def __init__(self):
        self.handlers = {}
        self.state = None
        self.allow_overloading = False
        self.break_on_juxtaposition = True
        self.allow_unknown = True
        self.juxtaposition_as_list = False
        symbol(self, TT_UNKNOWN)
        symbol(self, TT_ENDSTREAM)
        self.subparsers = []

    def add_subparsers(self, parsers):
        for parser in parsers:
            self.subparsers.append(parser)

    def open(self, state):
        assert self.state is None
        self.state = state
        self._on_open(state)

    def _on_open(self, state):
        for parser in self.subparsers:
            parser.open(state)

    def close(self):
        state = self.state
        self.state = None
        self._on_close()
        return state

    def _on_close(self):
        for parser in self.subparsers:
            parser.close()

    @property
    def ts(self):
        return self.state.ts

    @property
    def token_type(self):
        return tokens.token_type(self.ts.token)

    # @property
    # def is_newline_occurred(self):
    #     return self.ts.is_newline_occurred

    @property
    def node(self):
        return self.ts.node

    @property
    def token(self):
        return self.ts.token

    @property
    def previous_token(self):
        return self.ts.previous

    def next_token(self):
        try:
            return self.ts.next_token()
        except UnknownTokenError as e:
            parser_error_unknown(self, e.position)

    def isend(self):
        return self.token_type == TT_ENDSTREAM


class ExpressionParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.pattern_parser = PatternParser()
        self.fun_pattern_parser = FunPatternParser()
        self.guard_parser = guard_parser_init(BaseParser())
        self.name_parser = name_parser_init(BaseParser())
        self.let_parser = LetParser(self)
        self.map_key_parser = map_key_parser_init(BaseParser())

        self.add_subparsers(
            [
                self.pattern_parser,
                self.fun_pattern_parser,
                self.guard_parser,
                self.name_parser,
                self.let_parser,
                self.map_key_parser,
            ])

        self.allow_overloading = True

        init_parser_literals(self)

        symbol(self, TT_RSQUARE)
        symbol(self, TT_THEN)
        symbol(self, TT_RPAREN)
        symbol(self, TT_RCURLY)
        symbol(self, TT_END_EXPR)
        symbol(self, TT_ENDSTREAM)
        symbol(self, TT_AT_SIGN)
        symbol(self, TT_ELSE)
        symbol(self, TT_ELIF)
        symbol(self, TT_CASE)
        symbol(self, TT_THEN)
        symbol(self, TT_CATCH)
        symbol(self, TT_FINALLY)
        symbol(self, TT_WITH)
        symbol(self, TT_IN)
        symbol(self, TT_ASSIGN)
        symbol(self, TT_COMMA, symbol_comma_nud)

        prefix(self, TT_LPAREN, prefix_lparen)
        prefix(self, TT_LSQUARE, prefix_lsquare)
        prefix(self, TT_LCURLY, prefix_lcurly)
        prefix(self, TT_SHARP, prefix_sharp)
        prefix(self, TT_ELLIPSIS, prefix_nud)
        prefix(self, TT_NOT, prefix_not)
        prefix(self, TT_IF, prefix_if)

        prefix(self, TT_FUN, prefix_nameless_fun)

        prefix(self, TT_MATCH, prefix_match)
        prefix(self, TT_TRY, prefix_try)
        prefix(self, TT_BACKTICK_OPERATOR, prefix_backtick_operator)
        prefix(self, TT_LET, prefix_let)
        prefix(self, TT_THROW, prefix_throw)

        infix(self, TT_ARROW, 10, infix_arrow)
        infix(self, TT_WHEN, 10, infix_when)

        infix(self, TT_OF, 15, led_infix)
        infix(self, TT_OR, 25, led_infix)
        infix(self, TT_AND, 30, led_infix)
        infix(self, TT_BACKTICK_NAME, 35, infix_backtick_name)
        infix(self, TT_DOUBLE_COLON, 70, led_infixr)
        infix(self, TT_COLON, 100, infix_name_pair)
        infix(self, TT_DOT, 100, infix_dot)

        infix(self, TT_LPAREN, 100, infix_lparen)
        infix(self, TT_INFIX_DOT_LCURLY, 100, infix_lcurly)
        infix(self, TT_INFIX_DOT_LSQUARE, 100, infix_lsquare)
        # OTHER OPERATORS ARE DECLARED IN prelude.obn


class TraitParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.expression_parser = ExpressionParser()
        # TODO CHECK IT
        self.name_parser = name_parser_init(BaseParser())

        self.add_subparsers([
            self.expression_parser,
            self.name_parser,
        ])

        prefix(self, TT_DEF, prefix_trait_def)
        prefix(self, TT_LET, prefix_trait_let)
        prefix(self, TT_LPAREN, prefix_lparen)


class TypeParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.symbol_list_parser = symbol_list_parser_init(BaseParser())
        self.add_subparsers([
            self.symbol_list_parser
        ])

        symbol(self, TT_COMMA, symbol_comma_nud)
        symbol(self, TT_RPAREN, None)
        infix(self, TT_LPAREN, 100, infix_lparen_type)
        prefix(self, TT_NAME, prefix_typename)
        prefix(self, TT_LPAREN, prefix_lparen)


class ExtendParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.expression_parser = ExpressionParser()
        self.name_parser = name_parser_init(BaseParser())
        self.name_list_parser = name_list_parser_init(BaseParser())
        self.add_subparsers([
            self.expression_parser,
            self.name_parser,
            self.name_list_parser
        ])

        prefix(self, TT_LET, prefix_extend_let)
        prefix(self, TT_DEF, prefix_extend_def)
        prefix(self, TT_USE, prefix_extend_use)
        prefix(self, TT_LPAREN, prefix_lparen)


class PatternParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.map_key_parser = map_key_pattern_parser_init(BaseParser())
        self.add_subparsers([
            self.map_key_parser
        ])

        prefix(self, TT_LPAREN, prefix_lparen_expression)
        prefix(self, TT_LSQUARE, prefix_lsquare)
        prefix(self, TT_LCURLY, prefix_lcurly_pattern)
        prefix(self, TT_SHARP, prefix_sharp)
        prefix(self, TT_ELLIPSIS, prefix_nud)

        infix(self, TT_OF, 10, led_infix)
        infix(self, TT_AT_SIGN, 15, infix_at)
        infix(self, TT_DOUBLE_COLON, 60, led_infixr)
        infix(self, TT_COLON, 100, infix_name_pair)

        symbol(self, TT_WHEN)
        symbol(self, TT_CASE)
        symbol(self, TT_RPAREN)
        symbol(self, TT_RCURLY)
        symbol(self, TT_RSQUARE)
        symbol(self, TT_ASSIGN)
        symbol(self, TT_COMMA, symbol_comma_nud)

        init_parser_literals(self)


class LetParser(PatternParser):
    def __init__(self, expression_parser):
        PatternParser.__init__(self)
        self.expression_parser = expression_parser
        symbol(self, TT_IN)
        prefix(self, TT_LPAREN, prefix_lparen)
        prefix(self, TT_FUN, prefix_let_fun)
        infix(self, TT_ASSIGN, 10, led_let_assign)


class FunPatternParser(PatternParser):
    def __init__(self):
        PatternParser.__init__(self)
        prefix(self, TT_LPAREN, prefix_lparen_expression)


class ModuleParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.import_parser = import_parser_init(BaseParser())
        self.expression_parser = ExpressionParser()
        self.name_parser = name_parser_init(BaseParser())
        self.name_list_parser = name_list_parser_init(BaseParser())

        self.import_names_parser = import_names_parser_init(BaseParser())
        self.generic_parser = generic_parser_init(BaseParser())
        self.interface_parser = interface_parser_init(BaseParser())
        self.trait_parser = TraitParser()
        self.type_parser = TypeParser()
        self.extend_parser = ExtendParser()

        self.add_subparsers([
            self.import_parser,
            self.expression_parser,
            self.name_parser,
            self.import_names_parser,
            self.name_list_parser,
            self.generic_parser,
            self.interface_parser,
            self.trait_parser,
            self.extend_parser,
            self.type_parser,
        ])

        init_parser_literals(self)
        self.allow_overloading = True
        self.break_on_juxtaposition = True

        symbol(self, TT_ENDSTREAM)
        symbol(self, TT_COMMA, symbol_comma_nud)

        stmt(self, TT_FUN, prefix_module_fun)
        stmt(self, TT_LET, prefix_module_let)
        stmt(self, TT_TRAIT, stmt_trait)
        stmt(self, TT_TYPE, stmt_type)
        stmt(self, TT_EXTEND, stmt_extend)
        stmt(self, TT_IMPORT, stmt_import)
        stmt(self, TT_FROM, stmt_from)
        stmt(self, TT_EXPORT, stmt_export)
        stmt(self, TT_INFIXL, stmt_infixl)
        stmt(self, TT_INFIXR, stmt_infixr)
        stmt(self, TT_PREFIX, stmt_prefix)
        stmt(self, TT_GENERIC, stmt_generic)
        stmt(self, TT_INTERFACE, stmt_interface)


def guard_parser_init(parser):
    parser.allow_overloading = True
    parser = init_parser_literals(parser)

    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_RCURLY, None)
    symbol(parser, TT_RSQUARE, None)
    symbol(parser, TT_ASSIGN, None)

    prefix(parser, TT_LPAREN, prefix_lparen)
    prefix(parser, TT_LSQUARE, prefix_lsquare)
    prefix(parser, TT_LCURLY, prefix_lcurly)
    prefix(parser, TT_SHARP, prefix_sharp)
    prefix(parser, TT_BACKTICK_OPERATOR, prefix_backtick_operator)

    infix(parser, TT_OR, 25, led_infix)
    infix(parser, TT_AND, 30, led_infix)
    infix(parser, TT_BACKTICK_NAME, 35, infix_backtick_name)
    infix(parser, TT_DOT, 100, infix_dot)
    infix(parser, TT_COLON, 100, infix_name_pair)
    return parser


def map_key_pattern_parser_init(parser):
    parser = init_parser_literals(parser)
    symbol(parser, TT_COMMA, symbol_comma_nud)
    symbol(parser, TT_ASSIGN)

    infix(parser, TT_OF, 5, infix_map_pattern_of)
    infix(parser, TT_AT_SIGN, 15, infix_map_pattern_at)
    return parser


def map_key_parser_init(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_MULTI_STR)
    literal(parser, TT_NAME)

    symbol(parser, TT_COMMA)
    symbol(parser, TT_ASSIGN)

    return parser


def generic_parser_init(parser):
    prefix(parser, TT_LPAREN, prefix_lparen)
    infix(parser, TT_LPAREN, 100, infix_lparen_generic)

    prefix(parser, TT_NAME, prefix_name_as_symbol)
    prefix(parser, TT_TICKNAME, prefix_name_as_symbol)
    prefix(parser, TT_OPERATOR, operator_as_symbol)

    symbol(parser, TT_COMMA, symbol_comma_nud)
    symbol(parser, TT_RPAREN)
    return parser


def interface_parser_init(parser):
    prefix(parser, TT_LPAREN, prefix_lparen)
    infix(parser, TT_LPAREN, 90, infix_lparen_interface)
    infix(parser, TT_COLON, 100, infix_name_pair)
    literal(parser, TT_NAME)
    symbol(parser, TT_OPERATOR, symbol_operator_name)
    symbol(parser, TT_COMMA, symbol_comma_nud)
    symbol(parser, TT_RPAREN)
    return parser


def name_parser_init(parser):
    literal(parser, TT_NAME)
    symbol(parser, TT_OPERATOR, symbol_operator_name)
    infix(parser, TT_COLON, 100, infix_name_pair)
    return parser


def name_list_parser_init(parser):
    symbol(parser, TT_RPAREN, None)
    symbol(parser, TT_OPERATOR, symbol_operator_name)
    symbol(parser, TT_COMMA, symbol_comma_nud)

    literal(parser, TT_NAME)
    # FIXME THIS IS FOR PREFIX INFIXL
    literal(parser, TT_INT)

    prefix(parser, TT_LPAREN, prefix_lparen_tuple)

    infix(parser, TT_COLON, 100, infix_name_pair)
    return parser


def symbol_list_parser_init(parser):
    prefix(parser, TT_NAME, prefix_name_as_symbol)
    symbol(parser, TT_COMMA, symbol_comma_nud)
    return parser


def import_names_parser_init(parser):
    symbol(parser, TT_COMMA, symbol_comma_nud)
    symbol(parser, TT_RPAREN, None)
    literal(parser, TT_NAME)
    infix(parser, TT_AS, 15, infix_name_pair)
    prefix(parser, TT_LPAREN, prefix_lparen_tuple)
    return parser


def import_parser_init(parser):
    parser.allow_unknown = True
    symbol(parser, TT_UNKNOWN)
    symbol(parser, TT_COMMA, symbol_comma_nud)
    symbol(parser, TT_LPAREN, None)
    symbol(parser, TT_HIDING, None)
    symbol(parser, TT_HIDE, None)
    symbol(parser, TT_IMPORT, None)
    symbol(parser, TT_WILDCARD, None)
    infix(parser, TT_COLON, 100, infix_name_pair)
    infix(parser, TT_AS, 15, infix_name_pair)
    literal(parser, TT_NAME)

    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT)
    literal(parser, TT_FLOAT)
    literal(parser, TT_CHAR)
    literal(parser, TT_STR)
    literal(parser, TT_TRUE)
    literal(parser, TT_FALSE)
    literal(parser, TT_MULTI_STR)
    literal(parser, TT_NAME)
    literal(parser, TT_WILDCARD)
    return parser


def newparser():
    parser = ModuleParser()
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

    parser.next_token()
    stmts, scope = parse_module(parser, TERM_FILE)
    assert plist.is_empty(parser.state.scopes)
    check_token_type(parser, TT_ENDSTREAM)

    parser.close()
    # print stmts
    if PARSE_DEBUG:
        print "************************** OPERATORS ****************************************"
        print scope.operators
        print "************************** AST ****************************************"
        ast = str(nodes.node_to_string(stmts))
        f = open('debinfo/ast.json', 'w')
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
