__author__ = 'gloryofrobots'
from obin.compile.parse.token_type import *
from obin.types import space, api
from obin.misc.platform import re


def keyword(literal):
    return re.compile('\\b%s\\b' % literal)


token = re.compile

## Regexes for use in tokens
##
##
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
name_const = '[a-zA-Z_$][0-9a-zA-Z_$]*'
typename = '[A-Z][0-9a-zA-Z_$]*'
operator_char = '^\s\,\.\@\#\)\(\]\[\}\{\;\w"`\''
operator_const = '[%s]+' % operator_char

hex_prefix = '0[xX]'
hex_digits = '[0-9a-fA-F]+'
bin_prefix = '0[bB]'
bin_digits = '[01]+'

integer_suffix_opt = '(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
decimal_constant = '(0' + integer_suffix_opt + ')|([1-9][0-9]*' + integer_suffix_opt + ')'
octal_constant = '0[0-7]*' + integer_suffix_opt
hex_constant = hex_prefix + hex_digits + integer_suffix_opt
bin_constant = bin_prefix + bin_digits + integer_suffix_opt

# floating constants (K&R2: A.2.5.3)
exponent_part = """([eE][-+]?[0-9]+)"""
fractional_constant = """([0-9]+\.[0-9]+)"""
floating_constant = '((((' + fractional_constant + ')' + exponent_part + '?)|([0-9]+' + exponent_part + '))[FfLl]?)'
binary_exponent_part = '''([pP][+-]?[0-9]+)'''
hex_fractional_constant = '(((' + hex_digits + r""")?\.""" + hex_digits + ')|(' + hex_digits + r"""\.))"""
hex_floating_constant = '(' + hex_prefix + '(' + hex_digits + '|' + hex_fractional_constant + ')' + binary_exponent_part + '[FfLl]?)'

char_const = "'[^']+'"
backtick_const = "`[^`]+`"
string_literal = '(""".*?""")|(".*?")|(\'.*?\')'

RULES = [
    # (token('\n[ ]*'), TT_INDENTATION),
    (token('\n'), TT_NEWLINE),
    (token('[ ]*\.\.\.'), TT_ELLIPSIS),
    (token(' \.'), TT_JUXTAPOSITION),
    (token('\.\{'), TT_INFIX_DOT_LCURLY),
    (token('\.\('), TT_INFIX_DOT_LPAREN),
    (token(' '), -1),
    (token('-----[-]*'), -1),
    (token('//[^\n]*'), -1),
    (token('/\*[^\*\/]*\*/'), -1),

    (keyword('if'), TT_IF),
    (keyword('elif'), TT_ELIF),
    (keyword('else'), TT_ELSE),

    (keyword('in_case'), TT_IN_CASE),

    (keyword('then'), TT_THEN),
    (keyword('of'), TT_OF),
    (keyword('match'), TT_MATCH),
    (keyword('with'), TT_WITH),
    (keyword('fun'), TT_FUN),
    (keyword('end'), TT_END),
    (keyword('and'), TT_AND),
    (keyword('or'), TT_OR),
    (keyword('True'), TT_TRUE),
    (keyword('False'), TT_FALSE),
    # (keyword('nil'), TT_NIL),
    (keyword('throw'), TT_THROW),
    (keyword('ensure'), TT_ENSURE),
    (keyword('try'), TT_TRY),
    (keyword('catch'), TT_CATCH),
    (keyword('finally'), TT_FINALLY),
    (keyword('lam'), TT_LAMBDA),
    # (keyword('module'), TT_MODULE),

    (keyword('trait'), TT_TRAIT),
    (keyword('implement'), TT_IMPLEMENT),
    (keyword('def'), TT_DEF),
    (keyword('type'), TT_TYPE),
    (keyword('derive'), TT_DERIVE),
    (keyword('for'), TT_FOR),

    (keyword('export'), TT_EXPORT),
    (keyword('import'), TT_IMPORT),
    (keyword('from'), TT_FROM),
    (keyword('hiding'), TT_HIDING),

    (keyword('of'), TT_OF),
    (keyword('as'), TT_AS),
    (keyword('when'), TT_WHEN),

    (keyword('var'), TT_VAR),
    (keyword('lazy'), TT_LAZY),

    (keyword('infixl'), TT_INFIXL),
    (keyword('infixr'), TT_INFIXR),
    (keyword('prefix'), TT_PREFIX),

    (keyword('_'), TT_WILDCARD),

    # **********

    (token(floating_constant), TT_FLOAT),
    (token(decimal_constant), TT_INT),
    (token(string_literal), TT_STR),
    (token(char_const), TT_CHAR),
    (token(backtick_const), TT_BACKTICK),
    # (typename, TT_TYPENAME),
    (token(name_const), TT_NAME),

    (token('\&'), TT_AMP),

    (token('\-\>'), TT_ARROW),
    (token('\<\-'), TT_BACKARROW),
    (token('\;'), TT_END_EXPR),
    (token('#'), TT_SHARP),
    (token('\{'), TT_LCURLY),
    (token('\}'), TT_RCURLY),
    (token('\,'), TT_COMMA),
    (token('\('), TT_LPAREN),
    (token('\)'), TT_RPAREN),
    (token('\['), TT_LSQUARE),
    (token('\]'), TT_RSQUARE),
    (token('\.'), TT_DOT),
    (token('\.\.'), TT_DOUBLE_DOT),
    (token('@'), TT_AT_SIGN),
    (token('::'), TT_DOUBLE_COLON),
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


def newtoken(type, val, pos, line, column):
    assert isinstance(type, int)
    assert isinstance(val, str)
    assert space.isint(pos)
    assert space.isint(line)
    assert space.isint(column)
    return space.newtuple([space.newint(type), space.newstring_s(val), pos, line, column])


def newtoken_without_meta(type, val):
    return newtoken(type, val, space.newint(-1), space.newint(-1), space.newint(-1), )


def token_type(token):
    return api.to_i(api.at_index(token, 0))


def token_value_s(token):
    return api.to_s(api.at_index(token, 1))


def token_value(token):
    return api.at_index(token, 1)


def token_position(token):
    return api.at_index(token, 2)


def token_line(token):
    return api.at_index(token, 3)


def token_column(token):
    return api.at_index(token, 4)


# indentation level
def token_level(token):
    return api.to_i(token_column(token)) - 1


def token_position_i(token):
    return api.to_i(token_position(token))


def token_line_i(token):
    return api.to_i(token_line(token))


def token_column_i(token):
    return api.to_i(token_column(token))


def create_end_token(token):
    return newtoken(TT_END, "end",
                    token_position(token),
                    token_line(token),
                    token_column(token))


def create_end_expression_token(token):
    return newtoken(TT_END_EXPR, ";",
                    token_position(token),
                    token_line(token),
                    token_column(token))


def create_indent_token(token):
    return newtoken(TT_INDENT, "(indent)",
                    token_position(token),
                    token_line(token),
                    token_column(token))


def token_to_s(token):
    return "(%s, %s, %d, %d)" % (token_type_to_s(token_type(token)),
                                 repr(token_value_s(token)), api.to_i(token_line(token)),
                                 api.to_i(token_column(token)))
