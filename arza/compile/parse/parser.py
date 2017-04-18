__author__ = 'gloryofrobots'
from arza.compile.parse.tokenstream import TokenStream

from arza.compile.parse.tokenstream import TokenStream
from arza.compile.parse.indenter import IndentationTokenStream, InvalidIndentationError


from arza.compile.parse.callbacks import *
from arza.compile.parse.lexer import UnknownTokenError
from arza.compile.parse import tokens
from arza.types import api, space, plist, root, environment

if tokens.RPLY:
    import arza.compile.parse.lexer as lexer
else:
    import arza.compile.parse.lexer2 as lexer


# additional helpers


def infix_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infix_function, infix_function)


def infixr_operator(parser, ttype, lbp, infix_function):
    op = get_or_create_operator(parser, ttype)
    operator_infix(op, lbp, led_infixr_function, infix_function)


def prefix_operator(parser, ttype, pbp, prefix_function):
    op = get_or_create_operator(parser, ttype)
    operator_prefix(op, pbp, prefix_nud_function, prefix_function)


def infixr(parser, ttype, ntype, lbp):
    infix(parser, ttype, ntype, lbp, led_infixr)


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
        prefix(self, TT_INDENT, NT_THROW, prefix_indent)
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
        self.map_key_parser = MapKeyParser(self)

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
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)

        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
        prefix(self, TT_LSQUARE, None, prefix_lsquare)
        prefix(self, TT_LCURLY, None, prefix_lcurly)
        prefix(self, TT_SHARP, None, prefix_sharp)
        # TODO DELETE IT
        prefix(self, TT_ELLIPSIS, NT_REST, prefix_nud, 70)
        prefix(self, TT_NOT, NT_NOT, prefix_nud, 35)
        prefix(self, TT_IF, None, prefix_if)

        prefix(self, TT_FUN, None, prefix_nameless_fun)

        prefix(self, TT_MATCH, None, prefix_match)
        prefix(self, TT_TRY, None, prefix_try)
        prefix(self, TT_BACKTICK_OPERATOR, None, prefix_backtick_operator)
        prefix(self, TT_LET, None, prefix_let)
        prefix(self, TT_THROW, None, prefix_throw)

        infix(self, TT_ARROW, None, 10, infix_arrow)
        infix(self, TT_WHEN, None, 10, infix_when)

        infix(self, TT_OF, NT_OF, 15, led_infix)
        infix(self, TT_AS, NT_AS, 20, led_infix)
        infix(self, TT_OR, NT_OR, 25, led_infix)
        infix(self, TT_AND, NT_AND, 30, led_infix)
        infix(self, TT_BACKTICK_NAME, None, 35, infix_backtick_name)
        infix(self, TT_DOUBLE_COLON, NT_CONS, 70, led_infixr)
        infix(self, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
        infix(self, TT_DOT, None, 100, infix_dot)

        infix(self, TT_LPAREN, None, 95, infix_lparen)
        infix(self, TT_INFIX_DOT_LCURLY, None, 95, infix_lcurly)
        infix(self, TT_INFIX_DOT_LSQUARE, None, 95, infix_lsquare)
        # OTHER OPERATORS ARE DECLARED IN prelude.arza


class TypeParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.symbol_list_parser = symbol_list_parser_init(BaseParser())
        self.add_subparsers([
            self.symbol_list_parser
        ])

        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)
        symbol(self, TT_RPAREN)
        infix(self, TT_LPAREN, None, 100, infix_lparen_type)
        prefix(self, TT_NAME, NT_NAME, prefix_typename)
        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)


class PatternParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.map_key_parser = map_key_pattern_parser_init(BaseParser())
        self.add_subparsers([
            self.map_key_parser
        ])

        prefix(self, TT_LPAREN, None, prefix_lparen_tuple, layout=layout_lparen)
        prefix(self, TT_LSQUARE, None, prefix_lsquare, layout=layout_lsquare)
        prefix(self, TT_LCURLY, None, prefix_lcurly_pattern, layout=layout_lcurly)
        prefix(self, TT_SHARP, None, prefix_sharp)
        prefix(self, TT_ELLIPSIS, NT_REST, prefix_nud, 70)

        infix(self, TT_OF, NT_OF, 10, led_infix)
        infix(self, TT_AT_SIGN, None, 15, infix_at)
        infix(self, TT_DOUBLE_COLON, NT_CONS, 60, led_infixr)
        infix(self, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)

        symbol(self, TT_WHEN)
        symbol(self, TT_CASE)
        symbol(self, TT_RPAREN)
        symbol(self, TT_RCURLY)
        symbol(self, TT_RSQUARE)
        symbol(self, TT_ASSIGN)
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)

        init_parser_literals(self)


class LetParser(PatternParser):
    def __init__(self, expression_parser):
        PatternParser.__init__(self)
        self.expression_parser = expression_parser
        symbol(self, TT_IN)
        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
        prefix(self, TT_TRY, None, prefix_try)
        prefix(self, TT_FUN, None, prefix_let_fun)
        infix(self, TT_ASSIGN, None, 10, led_let_assign)


class FunPatternParser(PatternParser):
    def __init__(self):
        PatternParser.__init__(self)
        # prefix(self, TT_LPAREN, prefix_lparen_expression)


class DefPatternParser(PatternParser):
    def __init__(self):
        PatternParser.__init__(self)
        infix(self, TT_OF, None, 5, infix_def_of)
        prefix(self, TT_OF, None, prefix_def_of)

        # prefix(self, TT_LPAREN, prefix_lparen_expression)


class DefParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.expression_parser = ExpressionParser()
        self.fun_pattern_parser = DefPatternParser()
        self.guard_parser = guard_parser_init(BaseParser())
        self.name_parser = name_parser_init(BaseParser())

        self.add_subparsers([
            self.expression_parser,
            self.fun_pattern_parser,
            self.guard_parser,
            self.name_parser
        ])


class UseParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.def_parser = DefParser()
        self.name_parser = name_parser_init(BaseParser())
        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
        prefix(self, TT_DEF, None, prefix_use_def)

        self.add_subparsers([
            self.def_parser,
            self.name_parser
        ])


def use_in_alias_parser_init(parser):
    literal(parser, TT_NAME, NT_NAME)
    literal(parser, TT_INT, NT_INT)
    literal(parser, TT_ELLIPSIS, NT_REST)
    symbol_nud(parser, TT_OPERATOR, NT_NAME, symbol_operator_name)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    return parser


class GenericParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.generic_signature_parser = generic_signature_parser_init(BaseParser())

        prefix(self, TT_NAME, NT_NAME, prefix_generic_name)
        prefix(self, TT_OPERATOR, NT_NAME, prefix_generic_operator)
        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
        symbol(self, TT_RPAREN)

        self.add_subparsers([
            self.generic_signature_parser,
        ])


def generic_signature_parser_init(parser):
    prefix(parser, TT_NAME, NT_NAME, prefix_name_as_symbol)
    literal(parser, TT_WILDCARD, NT_WILDCARD)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    return parser


class InterfaceParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        prefix(self, TT_NAME, None, prefix_interface_name)
        prefix(self, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
        symbol(self, TT_RPAREN)
        self.interface_function_parser = InterfaceFunctionParser()
        self.name_parser = name_parser_init(BaseParser())

        self.add_subparsers([
            self.interface_function_parser,
            self.name_parser
        ])


class InterfaceFunctionParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)
        self.int_parser = int_parser_init(BaseParser())

        infix(self, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
        infix(self, TT_DOT, None, 90, infix_interface_dot)
        literal(self, TT_NAME, NT_NAME)
        prefix(self, TT_LPAREN, None, prefix_lparen_expression_only, layout=layout_lparen)
        symbol_nud(self, TT_OPERATOR, NT_NAME, symbol_operator_name)
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)
        symbol(self, TT_RPAREN)

        self.add_subparsers([
            self.int_parser
        ])


class MapKeyParser(BaseParser):
    def __init__(self, expression_parser):
        BaseParser.__init__(self)
        self.int_parser = int_parser_init(BaseParser())
        self.expression_parser = expression_parser
        literal(self, TT_INT, NT_INT)
        literal(self, TT_FLOAT, NT_FLOAT)
        literal(self, TT_CHAR, NT_CHAR)
        literal(self, TT_STR, NT_STR)
        literal(self, TT_TRUE, NT_TRUE)
        literal(self, TT_FALSE, NT_FALSE)
        literal(self, TT_MULTI_STR, NT_MULTI_STR)
        prefix(self, TT_NAME, NT_NAME, prefix_name_as_symbol)
        symbol_nud(self, TT_OPERATOR, NT_NAME, operator_as_symbol)
        prefix(self, TT_LPAREN, None, prefix_lparen_map_key)
        # literal(self, TT_NAME)
        symbol(self, TT_COMMA)
        symbol(self, TT_ASSIGN)


class ModuleParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.import_parser = import_parser_init(BaseParser())
        self.expression_parser = ExpressionParser()
        self.name_parser = name_parser_init(BaseParser())
        self.name_tuple_parser = name_tuple_parser_init(BaseParser())

        self.import_names_parser = import_names_parser_init(BaseParser())
        self.generic_parser = GenericParser()
        self.interface_parser = InterfaceParser()
        self.type_parser = TypeParser()
        self.name_list_parser = name_list_parser_init(BaseParser())
        self.def_parser = DefParser()
        self.use_parser = UseParser()
        self.use_in_alias_parser = use_in_alias_parser_init(BaseParser())

        self.add_subparsers([
            self.import_parser,
            self.expression_parser,
            self.name_parser,
            self.name_tuple_parser,
            self.name_list_parser,
            self.import_names_parser,
            self.generic_parser,
            self.interface_parser,
            self.type_parser,
            self.def_parser,
            self.use_in_alias_parser,
            self.use_parser
        ])

        init_parser_literals(self)
        self.allow_overloading = True
        self.break_on_juxtaposition = True

        symbol(self, TT_ENDSTREAM)
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)

        stmt(self, TT_FUN, None, prefix_module_fun)
        stmt(self, TT_LET, None, prefix_module_let)
        stmt(self, TT_TYPE, None, stmt_type)
        stmt(self, TT_IMPORT, None, stmt_import)
        stmt(self, TT_FROM, None, stmt_from)
        stmt(self, TT_EXPORT, None, stmt_export)
        stmt(self, TT_INFIXL, None, stmt_infixl)
        stmt(self, TT_INFIXR, None, stmt_infixr)
        stmt(self, TT_PREFIX, None, stmt_prefix)
        stmt(self, TT_GENERIC, None, stmt_generic)
        stmt(self, TT_DEF, None, stmt_def)
        stmt(self, TT_USE, None, stmt_use)
        stmt(self, TT_INTERFACE, None, stmt_interface, layout=layout_node)
        stmt(self, TT_DERIVE, None, stmt_derive)

        prefix(self, TT_LPAREN, None, prefix_lparen_module, layout=layout_lparen)
        symbol(self, TT_RPAREN)


def guard_parser_init(parser):
    parser.allow_overloading = True
    parser = init_parser_literals(parser)

    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ASSIGN)

    prefix(parser, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
    prefix(parser, TT_LSQUARE, None, prefix_lsquare)
    prefix(parser, TT_LCURLY, None, prefix_lcurly)
    prefix(parser, TT_SHARP, None, prefix_sharp)
    prefix(parser, TT_BACKTICK_OPERATOR, None, prefix_backtick_operator)
    prefix(parser, TT_NOT, NT_NOT, prefix_nud, 35)

    infix(parser, TT_OR, NT_OR, 25, led_infix)
    infix(parser, TT_AND, NT_AND, 30, led_infix)
    infix(parser, TT_BACKTICK_NAME, None, 35, infix_backtick_name)
    infix(parser, TT_DOT, None, 100, infix_dot)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 110, infix_name_pair)
    infix(parser, TT_LPAREN, None, 95, infix_lparen)
    infix(parser, TT_INFIX_DOT_LCURLY, None, 95, infix_lcurly)
    infix(parser, TT_INFIX_DOT_LSQUARE, None, 95, infix_lsquare)
    return parser


def map_key_pattern_parser_init(parser):
    parser = init_parser_literals(parser)
    # prefix(parser, TT_NAME, prefix_name_as_symbol)
    prefix(parser, TT_SHARP, None, prefix_sharp)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    symbol(parser, TT_ASSIGN)

    infix(parser, TT_OF, None, 5, infix_map_pattern_of)
    infix(parser, TT_AT_SIGN, None, 15, infix_map_pattern_at)
    return parser


def int_parser_init(parser):
    literal(parser, TT_INT, NT_INT)
    return parser


def name_parser_init(parser):
    literal(parser, TT_NAME, NT_NAME)
    symbol_nud(parser, TT_OPERATOR, NT_NAME, symbol_operator_name)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    return parser


def name_tuple_parser_init(parser):
    symbol(parser, TT_RPAREN)
    symbol_nud(parser, TT_OPERATOR, NT_NAME, symbol_operator_name)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)

    literal(parser, TT_NAME, NT_NAME)
    # FIXME THIS IS FOR PREFIX INFIXL
    literal(parser, TT_INT, NT_INT)

    prefix(parser, TT_LPAREN, None, prefix_lparen_tuple, layout=layout_lparen)

    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    return parser


def name_list_parser_init(parser):
    symbol(parser, TT_RPAREN)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    literal(parser, TT_NAME, NT_NAME)
    prefix(parser, TT_LSQUARE, None, prefix_lsquare_name_list)
    return parser


def symbol_list_parser_init(parser):
    prefix(parser, TT_NAME, NT_NAME, prefix_name_as_symbol)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    return parser


def import_names_parser_init(parser):
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    symbol(parser, TT_RPAREN)
    literal(parser, TT_NAME, NT_NAME)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    infix(parser, TT_AS, NT_AS, 15, infix_name_pair)
    prefix(parser, TT_LPAREN, None, prefix_lparen_tuple, layout=layout_lparen)
    return parser


def import_parser_init(parser):
    parser.allow_unknown = True
    symbol(parser, TT_UNKNOWN)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    symbol(parser, TT_LPAREN)
    symbol(parser, TT_HIDING)
    symbol(parser, TT_HIDE)
    symbol(parser, TT_IMPORT)
    symbol(parser, TT_WILDCARD)
    infix(parser, TT_COLON, NT_IMPORTED_NAME, 100, infix_name_pair)
    infix(parser, TT_AS, NT_AS, 15, infix_name_pair)
    literal(parser, TT_NAME, NT_NAME)

    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT, NT_INT)
    literal(parser, TT_FLOAT, NT_FLOAT)
    literal(parser, TT_CHAR, NT_CHAR)
    literal(parser, TT_STR, NT_STR)
    literal(parser, TT_TRUE, NT_TRUE)
    literal(parser, TT_FALSE, NT_FALSE)
    literal(parser, TT_MULTI_STR, NT_MULTI_STR)
    literal(parser, TT_NAME, NT_NAME)
    literal(parser, TT_WILDCARD, NT_WILDCARD)
    return parser


def newparser():
    parser = ModuleParser()
    return parser


def newtokenstream(source):
    lx = lexer.lexer(source)
    tokens_iter = lx.tokens()
    return IndentationTokenStream(tokens_iter, source)


PARSE_DEBUG = True


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
