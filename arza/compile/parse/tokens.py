__author__ = 'gloryofrobots'
from arza.compile.parse.token_type import *
from arza.types import space, api, root
from arza.misc.platform import re

RPLY = True

if RPLY:
    def keyword(literal):
        return re.compile('\\b%s\\b' % literal)


    def token(literal):
        return re.compile(literal)
else:
    def keyword(literal):
        return '\\b%s\\b' % literal


    def token(literal):
        return literal


# OLD STUFF
# simple_escape = """([a-zA-Z._~!=&\^\-\\?'"])"""
# decimal_escape = """(\d+)"""
# hex_escape = """(x[0-9a-fA-F]+)"""

# escape_sequence = """(\\(""" + simple_escape + '|' + decimal_escape + '|' + hex_escape + '))'
# cconst_char = """([^'\\\n]|""" + escape_sequence + ')'
# char_const = "'" + cconst_char + "'"

# string literals (K&R2: A.2.6)
# string_char = """([^"\\\n]|""" + escape_sequence + ')'
# string_literal = '"' + string_char + '*"'
# wstring_literal = 'L' + string_literal
# string_literal = "\"[^\"]*\""


# valid  identifiers (K&R2: A.2.3), plus '$' (supported by some compilers)
name_const = '[a-zA-Z_][0-9a-zA-Z_]*'
typename = '[A-Z][0-9a-zA-Z_]*'
operator_char = '^\s\,\.\@\#\)\(\]\[\}\{\;\w"`\''
operator_const = '[%s]+' % operator_char

hex_prefix = '0[xX]'
hex_digits = '[0-9a-fA-F]+'
bin_prefix = '0[bB]'
bin_digits = '[01]+'

integer_suffix_opt = '(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
# decimal_constant = '(0' + integer_suffix_opt + ')|([1-9][0-9]*' + integer_suffix_opt + ')'
decimal_constant = "[0-9]+"

octal_constant = '0[0-7]*' + integer_suffix_opt
hex_constant = hex_prefix + hex_digits + integer_suffix_opt
bin_constant = bin_prefix + bin_digits + integer_suffix_opt

# floating constants (K&R2: A.2.5.3)
exponent_part = """([eE][-+]?[0-9]+)"""
fractional_constant = """([0-9]+\.[0-9]+)"""
# floating_constant = '((((' + fractional_constant + ')' + exponent_part + '?)|([0-9]+' + exponent_part + '))[FfLl]?)'
floating_constant = fractional_constant

binary_exponent_part = '''([pP][+-]?[0-9]+)'''
hex_fractional_constant = '(((' + hex_digits + r""")?\.""" + hex_digits + ')|(' + hex_digits + r"""\.))"""
hex_floating_constant = '(' + hex_prefix + '(' + hex_digits + '|' + hex_fractional_constant + ')' + binary_exponent_part + '[FfLl]?)'

char_const = "'[^']+'"
# backtick_const = "`[^`]+`"

singletick_name_const = "`%s" % name_const
backtick_name_const = "`%s`" % name_const
backtick_op_const = "`%s`" % operator_const
# string_literal = '(""".*?""")|(".*?")'
# string_literal = '"(\\.|[^"])*"'
# string_literal = '"(\\.|[^"])*"'
# string_literal = '"([^"]|[a-zA-Z._~!=&\^\-\?\'"])*"'
string_literal = '"([^\\\"]+|\\.)*"'
multi_string_literal = '"{3}([\s\S]*?"{3})'

RULES = [
    (token('\n'), -1),
    (token('[ ]*\.\.\.'), TT_ELLIPSIS),
    (token('\.\{'), TT_INFIX_DOT_LCURLY),
    (token('\.\['), TT_INFIX_DOT_LSQUARE),
    (token(' '), -1),
    (token('--[^\n]*'), -1),
    (token('//[^\n]*'), -1),
    (token('/\*[^\*\/]*\*/'), -1),

    (keyword('if'), TT_IF),
    (keyword('elif'), TT_ELIF),
    (keyword('else'), TT_ELSE),

    (keyword('then'), TT_THEN),
    (keyword('of'), TT_OF),
    (keyword('match'), TT_MATCH),
    (keyword('with'), TT_WITH),
    (keyword('fun'), TT_FUN),
    (keyword('and'), TT_AND),
    (keyword('or'), TT_OR),
    (keyword('not'), TT_NOT),
    (keyword('True'), TT_TRUE),
    (keyword('False'), TT_FALSE),
    # (keyword('nil'), TT_NIL),
    (keyword('throw'), TT_THROW),
    (keyword('try'), TT_TRY),
    (keyword('catch'), TT_CATCH),
    (keyword('finally'), TT_FINALLY),
    # (keyword('module'), TT_MODULE),

    (keyword('use'), TT_USE),
    (keyword('extend'), TT_EXTEND),
    (keyword('for'), TT_FOR),

    (keyword('trait'), TT_TRAIT),
    (keyword('generic'), TT_GENERIC),
    (keyword('interface'), TT_INTERFACE),
    (keyword('derive'), TT_DERIVE),
    (keyword('type'), TT_TYPE),

    (keyword('export'), TT_EXPORT),
    (keyword('import'), TT_IMPORT),
    (keyword('from'), TT_FROM),
    (keyword('hiding'), TT_HIDING),
    (keyword('hide'), TT_HIDE),

    (keyword('of'), TT_OF),
    (keyword('as'), TT_AS),
    (keyword('let'), TT_LET),
    (keyword('def'), TT_DEF),
    (keyword('when'), TT_WHEN),
    (keyword('in'), TT_IN),

    (keyword('infixl'), TT_INFIXL),
    (keyword('infixr'), TT_INFIXR),
    (keyword('prefix'), TT_PREFIX),

    (keyword('_'), TT_WILDCARD),

    # **********

    (token(floating_constant), TT_FLOAT),
    (token(decimal_constant), TT_INT),
    (token(multi_string_literal), TT_MULTI_STR),
    (token(string_literal), TT_STR),
    (token(char_const), TT_CHAR),
    (token(backtick_name_const), TT_BACKTICK_NAME),
    (token(backtick_op_const), TT_BACKTICK_OPERATOR),
    # (typename, TT_TYPENAME),
    (token(name_const), TT_NAME),

    (token('=>'), TT_FAT_ARROW),
    (token('\-\>'), TT_ARROW),
    # (token('\<\-'), TT_BACKARROW),
    (token('\-\:'), TT_DISPATCH),
    (token('\;'), TT_END_EXPR),
    (token('#'), TT_SHARP),
    (token('\{'), TT_LCURLY),
    (token('\}'), TT_RCURLY),
    (token('\,'), TT_COMMA),
    (token('\('), TT_LPAREN),
    (token('\)'), TT_RPAREN),
    (token('\['), TT_LSQUARE),
    (token('\]'), TT_RSQUARE),
    (token('\.[\.]+'), TT_OPERATOR),
    (token('\.'), TT_DOT),
    (token('@'), TT_AT_SIGN),
    (token('::'), TT_DOUBLE_COLON),
    (token('[:^:][%s]+' % operator_char), TT_OPERATOR),
    (token(':'), TT_COLON),
    (token('[%s][=]+' % operator_char), TT_OPERATOR),
    (token('[=][%s]+' % operator_char), TT_OPERATOR),
    (token('[%s][|]+' % operator_char), TT_OPERATOR),
    (token('[|][%s]+' % operator_char), TT_OPERATOR),
    # (token('[%s][:]+' % operator_char), TT_OPERATOR),
    # (token('[:][%s]+' % operator_char), TT_OPERATOR),

    (token('\|'), TT_CASE),
    (token('='), TT_ASSIGN),

    # that can catch op
    (token(operator_const), TT_OPERATOR),
]


class Token(root.W_Hashable):
    def __init__(self, type, val, pos, line, column):
        root.W_Hashable.__init__(self)
        assert isinstance(type, int)
        assert isinstance(val, str), val
        assert space.isint(pos)
        assert space.isint(line)
        assert space.isint(column)
        self.type = type
        self.length = len(val)
        self.val_s = val
        self.val = space.newstring_s(val)
        self.pos = pos
        self.line = line
        self.column = column

    def _compute_hash_(self):
        from arza.misc.platform import rarithmetic
        x = 0x345678
        for item in [self.val, self.pos, self.line, self.column]:
            y = api.hash_i(item)
            x = rarithmetic.intmask((1000003 * x) ^ y)
        return x

    def _type_(self, process):
        return process.std.types.Tuple

    def _equal_(self, other):
        if not isinstance(other, Token):
            return False

        if self.type != other.type:
            return False
        if self.val_s != other.val_s:
            return False

        if token_position_i(self) != token_position_i(other):
            return False

        return True

    def _to_string_(self):
        return token_to_s(self)


def newtoken(type, val, pos, line, column):
    return Token(type, val, pos, line, column)


def newtoken_without_meta(type, val):
    return newtoken(type, val, space.newint(-1), space.newint(-1), space.newint(-1), )


def token_type(token):
    return token.type


def token_value_s(token):
    return token.val_s


def token_value(token):
    return token.val


def token_position(token):
    return token.pos


def token_line(token):
    return token.line


def token_column(token):
    return token.column


def token_length(token):
    return token.length


INFIX_TOKENS = [TT_DOUBLE_COLON, TT_COLON,
                TT_OPERATOR, TT_DOT, TT_ASSIGN, TT_OR, TT_AND]


def is_infix_token_type(ttype):
    return ttype in INFIX_TOKENS


# indentation level
def token_level(token):
    return api.to_i(token_column(token)) - 1


def token_position_i(token):
    return api.to_i(token_position(token))


def token_line_i(token):
    return api.to_i(token_line(token))


def token_column_i(token):
    return api.to_i(token_column(token))


def create_end_expression_token(token):
    return newtoken(TT_END_EXPR, ";",
                    token_position(token),
                    token_line(token),
                    token_column(token))


def token_to_s(token):
    return "(%s, %s, %d, %d)" % (token_type_to_s(token_type(token)),
                                 str(token_value_s(token)), api.to_i(token_line(token)),
                                 api.to_i(token_column(token)))
