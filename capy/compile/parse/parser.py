__author__ = 'gloryofrobots'

from capy.compile.parse.tokenstream import TokenStream
from capy.compile.parse.indenter import IndentationTokenStream, InvalidIndentationError

from capy.compile.parse.callbacks import *
from capy.compile.parse.lexer import UnknownTokenError
from capy.compile.parse import tokens
from capy.types import api, space, plist, root, environment

if tokens.RPLY:
    import capy.compile.parse.lexer as lexer
else:
    import capy.compile.parse.lexer2 as lexer


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
        self.name_parser = name_parser_init(BaseParser())
        self.fun_name_parser = fun_name_parser_init(BaseParser())
        self.map_key_parser = MapKeyParser(self)
        self.modify_key_parser = ModifyKeyParser(self)

        self.add_subparsers(
            [
                self.pattern_parser,
                self.name_parser,
                self.fun_name_parser,
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

        prefix(self, TT_TRY, None, prefix_try, layout=layout_try)
        prefix(self, TT_THROW, None, prefix_throw)
        prefix(self, TT_CLASS, None, prefix_class, layout=layout_class)

        infix(self, TT_ARROW, None, 10, infix_arrow)
        infix(self, TT_WHEN, None, 10, infix_when)

        infix(self, TT_ASSIGN, None, 10, led_assign)
        infix(self, TT_OF, NT_OF, 15, led_infix)
        infix(self, TT_AS, NT_AS, 20, led_infix)
        infix(self, TT_OR, NT_OR, 25, led_infix)
        infix(self, TT_AND, NT_AND, 30, led_infix)
        infix(self, TT_DOT, None, 100, infix_dot)

        infix(self, TT_LPAREN, None, 95, infix_lparen, layout=layout_lparen)
        infix(self, TT_INFIX_DOT_LCURLY, None, 95, infix_lcurly, layout=layout_lcurly)
        infix(self, TT_LSQUARE, None, 95, infix_lsquare, layout=layout_lsquare)
        # OTHER OPERATORS ARE DECLARED IN prelude.arza


class PatternParser(BaseParser):
    def __init__(self):
        BaseParser.__init__(self)

        self.map_key_parser = map_key_pattern_parser_init(BaseParser())
        self.add_subparsers([
            self.map_key_parser
        ])

        prefix(self, TT_LSQUARE, None, prefix_lsquare, layout=layout_lsquare)
        prefix(self, TT_LCURLY, None, prefix_lcurly_pattern, layout=layout_lcurly)
        prefix(self, TT_ELLIPSIS, NT_REST, prefix_nud, 70)
        symbol_nud(self, TT_COMMA, None, symbol_comma_nud)

        init_parser_literals(self)


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

        self.add_subparsers([
            self.import_parser,
            self.name_parser,
            self.name_tuple_parser,
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
        symbol(self, TT_ENDSTREAM)


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

def fun_name_parser_init(parser):
    infix(parser, TT_DOT, NT_LOOKUP, 100, led_infix)
    prefix(parser, TT_NAME, NT_NAME, prefix_name_as_symbol)
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
    symbol(parser, TT_IMPORT)
    symbol(parser, TT_WILDCARD)
    infix(parser, TT_AS, NT_AS, 15, infix_name_pair)
    infix(parser, TT_DOT, NT_LOOKUP, 100, led_infix)
    literal(parser, TT_NAME, NT_NAME)

    return parser


def init_parser_literals(parser):
    literal(parser, TT_INT, NT_INT)
    literal(parser, TT_FLOAT, NT_FLOAT)
    literal(parser, TT_CHAR, NT_CHAR)
    literal(parser, TT_STR, NT_STR)
    literal(parser, TT_TRUE, NT_TRUE)
    literal(parser, TT_NIL, NT_NIL)
    literal(parser, TT_FALSE, NT_FALSE)
    literal(parser, TT_MULTI_STR, NT_MULTI_STR)
    literal(parser, TT_NAME, NT_NAME)
    literal(parser, TT_SELF, NT_NAME)
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
