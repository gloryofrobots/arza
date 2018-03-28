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
        return self.ts.next_token()

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
        self.modify_key_parser = ModifyKeyParser(self)

        self.add_subparsers(
            [
                self.pattern_parser,
                self.fun_pattern_parser,
                self.guard_parser,
                self.name_parser,
                self.let_parser,
                self.map_key_parser,
                self.modify_key_parser
            ])

        self.allow_overloading = True

        init_parser_literals(self)

        symbol(self, TT_RSQUARE)
        symbol(self, TT_THEN)
        symbol(self, TT_RPAREN)
        symbol(self, TT_RCURLY)
        symbol(self, TT_END_EXPR)
        symbol(self, TT_ENDSTREAM)
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
        prefix(self, TT_LSQUARE, None, prefix_lsquare, layout=layout_lsquare)
        prefix(self, TT_LCURLY, None, prefix_lcurly, layout=layout_lcurly)
        prefix(self, TT_SHARP, None, prefix_sharp)

        # TODO DELETE IT, BAD PARSER COMPOSITION. EXPRESSIONS DOES NOT NEED THEM
        prefix(self, TT_ELLIPSIS, NT_REST, prefix_nud, 70)
        prefix(self, TT_AT_SIGN, None, prefix_decorator, layout=layout_decorator)

        prefix(self, TT_NOT, NT_NOT, prefix_nud, 35)
        prefix(self, TT_IF, None, prefix_if, layout=layout_if)

        prefix(self, TT_FUN, None, prefix_fun, layout=layout_fun)

        prefix(self, TT_MATCH, None, prefix_match, layout=layout_match)
        prefix(self, TT_RECEIVE, None, prefix_receive, layout=layout_receive)
        prefix(self, TT_TRY, None, prefix_try, layout=layout_try)
        prefix(self, TT_BACKTICK_OPERATOR, None, prefix_backtick_operator)
        prefix(self, TT_THROW, None, prefix_throw)
        prefix(self, TT_CLASS, None, prefix_class, layout=layout_fun)

        prefix(self, TT_LET, None, prefix_let, layout=layout_let)

        infix(self, TT_ARROW, None, 10, infix_arrow)
        infix(self, TT_WHEN, None, 10, infix_when)

        infix(self, TT_OF, NT_OF, 15, led_infix)
        infix(self, TT_AS, NT_AS, 20, led_infix)
        infix(self, TT_OR, NT_OR, 25, led_infix)
        infix(self, TT_AND, NT_AND, 30, led_infix)
        infix(self, TT_BACKTICK_NAME, None, 35, infix_backtick_name)
        infix(self, TT_DOUBLE_COLON, NT_CONS, 70, led_infixr)
        infix(self, TT_DOT, None, 100, infix_dot)

        infix(self, TT_LPAREN, None, 95, infix_lparen, layout=layout_lparen)
        infix(self, TT_INFIX_DOT_LCURLY, None, 95, infix_lcurly, layout=layout_lcurly)
        infix(self, TT_INFIX_DOT_LSQUARE, None, 95, infix_lsquare, layout=layout_lsquare)
        # OTHER OPERATORS ARE DECLARED IN prelude.arza


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

        infix(self, TT_LPAREN, None, 95, infix_lparen_pattern, layout=layout_lparen)
        infix(self, TT_AS, None, 15, infix_bind)
        infix(self, TT_DOUBLE_COLON, NT_CONS, 60, led_infixr)

        symbol(self, TT_WHEN)
        symbol(self, TT_CASE)
        symbol(self, TT_RPAREN)
        symbol(self, TT_RCURLY)
        symbol(self, TT_RSQUARE)
        symbol(self, TT_ASSIGN)
        symbol(self, TT_COLON)
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)

        init_parser_literals(self)


class LetParser(PatternParser):
    def __init__(self, expression_parser):
        PatternParser.__init__(self)
        self.expression_parser = expression_parser
        self.name_parser = name_parser_init(BaseParser())
        self.add_subparsers([
            self.name_parser,
        ])
        infix(self, TT_ASSIGN, None, 10, led_let_assign)


class FunPatternParser(PatternParser):
    def __init__(self):
        PatternParser.__init__(self)


class ModifyKeyParser(BaseParser):
    def __init__(self, expression_parser):
        BaseParser.__init__(self)
        self.expression_parser = expression_parser
        literal(self, TT_INT, NT_INT)
        literal(self, TT_FLOAT, NT_FLOAT)
        literal(self, TT_CHAR, NT_CHAR)
        literal(self, TT_STR, NT_STR)
        literal(self, TT_TRUE, NT_TRUE)
        literal(self, TT_FALSE, NT_FALSE)
        literal(self, TT_MULTI_STR, NT_MULTI_STR)
        prefix(self, TT_LPAREN, None, prefix_lparen_map_key)
        # literal(self, TT_NAME, NT_NAME)
        prefix(self, TT_NAME, NT_NAME, prefix_name_as_symbol)
        # symbol_nud(self, TT_OPERATOR, NT_NAME, operator_as_symbol)
        symbol(self, TT_COMMA)
        symbol(self, TT_ASSIGN)
        symbol(self, TT_OR)
        # infix(self, TT_DOT, None, 100, infix_lcurly_dot)
        infix(self, TT_DOT, NT_LOOKUP, 70, led_infixr)


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
        prefix(self, TT_LPAREN, None, prefix_lparen_map_key)
        symbol_nud(self, TT_OPERATOR, NT_NAME, operator_as_symbol)
        symbol(self, TT_COMMA)
        symbol(self, TT_ASSIGN)


class ModuleParser(ExpressionParser):
    def __init__(self):
        ExpressionParser.__init__(self)

        self.import_parser = import_parser_init(BaseParser())
        self.name_parser = name_parser_init(BaseParser())
        self.name_tuple_parser = name_tuple_parser_init(BaseParser())

        self.import_names_parser = import_names_parser_init(BaseParser())
        self.name_list_parser = name_list_parser_init(BaseParser())

        self.add_subparsers([
            self.import_parser,
            self.name_parser,
            self.name_tuple_parser,
            self.name_list_parser,
            self.import_names_parser,
        ])

        init_parser_literals(self)
        self.allow_overloading = True
        self.break_on_juxtaposition = True

        stmt(self, TT_INFIXL, None, stmt_infixl)
        stmt(self, TT_INFIXR, None, stmt_infixr)
        stmt(self, TT_PREFIX, None, stmt_prefix)
        stmt(self, TT_IMPORT, None, stmt_import)
        stmt(self, TT_INCLUDE, None, stmt_include)
        stmt(self, TT_EXPORT, None, stmt_export)
        symbol(self, TT_ENDSTREAM)


def guard_parser_init(parser):
    parser.allow_overloading = True
    parser = init_parser_literals(parser)

    symbol(parser, TT_RPAREN)
    symbol(parser, TT_RCURLY)
    symbol(parser, TT_RSQUARE)
    symbol(parser, TT_ASSIGN)

    prefix(parser, TT_LPAREN, None, prefix_lparen, layout=layout_lparen)
    prefix(parser, TT_LSQUARE, None, prefix_lsquare, layout=layout_lsquare)
    prefix(parser, TT_LCURLY, None, prefix_lcurly, layout=layout_lcurly)
    prefix(parser, TT_SHARP, None, prefix_sharp)
    prefix(parser, TT_BACKTICK_OPERATOR, None, prefix_backtick_operator)
    prefix(parser, TT_NOT, NT_NOT, prefix_nud, 35)

    infix(parser, TT_OR, NT_OR, 25, led_infix)
    infix(parser, TT_AND, NT_AND, 30, led_infix)
    infix(parser, TT_BACKTICK_NAME, None, 35, infix_backtick_name)
    infix(parser, TT_DOT, None, 100, infix_dot)
    infix(parser, TT_LPAREN, None, 95, infix_lparen, layout=layout_lparen)
    infix(parser, TT_INFIX_DOT_LCURLY, None, 95, infix_lcurly, layout=layout_lcurly)
    infix(parser, TT_INFIX_DOT_LSQUARE, None, 95, infix_lsquare, layout=layout_lsquare)
    return parser


def map_key_pattern_parser_init(parser):
    parser = init_parser_literals(parser)
    # prefix(parser, TT_NAME, prefix_name_as_symbol)
    prefix(parser, TT_SHARP, None, prefix_sharp)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    symbol(parser, TT_ASSIGN)

    infix(parser, TT_OF, None, 5, infix_map_pattern_of)
    infix(parser, TT_AS, None, 15, infix_map_pattern_as)
    return parser


def int_parser_init(parser):
    literal(parser, TT_INT, NT_INT)
    return parser


def name_parser_init(parser):
    literal(parser, TT_NAME, NT_NAME)
    symbol_nud(parser, TT_OPERATOR, NT_NAME, symbol_operator_name)
    return parser


def name_tuple_parser_init(parser):
    symbol(parser, TT_RPAREN)
    symbol_nud(parser, TT_OPERATOR, NT_NAME, symbol_operator_name)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)

    literal(parser, TT_NAME, NT_NAME)
    # FIXME THIS IS FOR PREFIX INFIXL
    literal(parser, TT_INT, NT_INT)

    prefix(parser, TT_LPAREN, None, prefix_lparen_tuple, layout=layout_lparen)

    return parser


def name_list_parser_init(parser):
    symbol(parser, TT_RPAREN)
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    literal(parser, TT_NAME, NT_NAME)
    prefix(parser, TT_LSQUARE, None, prefix_lsquare_name_list, layout=layout_lsquare)
    return parser


def import_names_parser_init(parser):
    symbol_nud(parser, TT_COMMA, None, symbol_comma_nud)
    symbol(parser, TT_RPAREN)
    literal(parser, TT_NAME, NT_NAME)
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
    return IndentationTokenStream(lx, source)


def parse(process, env, src):
    parser = process.parser
    try:
        ts = newtokenstream(src)

        parser.open(ParseState(process, env, ts))

        parser.next_token()
        stmts, scope = parse_module(parser)
        assert plist.is_empty(parser.state.scopes)
        check_token_type(parser, TT_ENDSTREAM)

        parser.close()
        # print stmts
        if api.DEBUG_MODE:
            print "************************** OPERATORS ****************************************"
            print scope.operators
            print "************************** AST ****************************************"
            ast = str(nodes.node_to_string(stmts))
            f = open('debinfo/ast.json', 'w')
            f.write(ast)
            f.close()
            raise SystemExit()

        return stmts, scope
    except UnknownTokenError as e:
        parser_error_unknown(parser, e.position)
    except InvalidIndentationError as e:
        parser_error_indentation(parser, e.msg, e.position, e.line, e.column)


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
