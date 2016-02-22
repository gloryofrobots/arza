__author__ = 'gloryofrobots'
from obin.compile.parse.token_type import *
from obin.types import space, api
from obin.misc.platform import re


def keyword(literal):
    return re.compile('\\b%s\\b' % literal)


# def token(literal):
#     return literal

token = re.compile

## Regexes for use in tokens
##
##

# valid  identifiers (K&R2: A.2.3), plus '$' (supported by some compilers)
name = token('[a-zA-Z_$][0-9a-zA-Z_$]*')
operator_char = '^\s\,\.\@\#\)\(\]\[\}\{\;\w"`\''
operator = token('[%s]+' % operator_char)

hex_prefix = '0[xX]'
hex_digits = '[0-9a-fA-F]+'
bin_prefix = '0[bB]'
bin_digits = '[01]+'

integer_suffix_opt = '(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
decimal_constant = token('(0' + integer_suffix_opt + ')|([1-9][0-9]*' + integer_suffix_opt + ')')
octal_constant = '0[0-7]*' + integer_suffix_opt
hex_constant = hex_prefix + hex_digits + integer_suffix_opt
bin_constant = bin_prefix + bin_digits + integer_suffix_opt

simple_escape = """([a-zA-Z._~!=&\^\-\\?'"])"""
decimal_escape = """(\d+)"""
hex_escape = """(x[0-9a-fA-F]+)"""

escape_sequence = """(\\(""" + simple_escape + '|' + decimal_escape + '|' + hex_escape + '))'
cconst_char = """([^'\\\n]|""" + escape_sequence + ')'
char_const = "'" + cconst_char + "'"
char_const = token("'[^']+'")
backtick_const = token("`[^`]+`")

# string literals (K&R2: A.2.6)
# string_char = """([^"\\\n]|""" + escape_sequence + ')'
# string_literal = token('"' + string_char + '*"')
string_literal = token('(""".*?""")|(".*?")|(\'.*?\')')
# wstring_literal = 'L' + string_literal
# string_literal = "\"[^\"]*\""

# floating constants (K&R2: A.2.5.3)
exponent_part = """([eE][-+]?[0-9]+)"""
fractional_constant = """([0-9]*\.[0-9]+)"""
floating_constant = token(
    '((((' + fractional_constant + ')' + exponent_part + '?)|([0-9]+' + exponent_part + '))[FfLl]?)')
binary_exponent_part = '''([pP][+-]?[0-9]+)'''
hex_fractional_constant = '(((' + hex_digits + r""")?\.""" + hex_digits + ')|(' + hex_digits + r"""\.))"""
hex_floating_constant = '(' + hex_prefix + '(' + hex_digits + '|' + hex_fractional_constant + ')' + binary_exponent_part + '[FfLl]?)'

RULES = [
    (token('\n'), TT_NEWLINE),
    (token(' '), -1),
    (token('//[^\n]*'), -1),
    (token('/\*[^\*\/]*\*/'), -1),
    (keyword('break'), TT_BREAK),
    (keyword('continue'), TT_CONTINUE),
    (keyword('for'), TT_FOR),
    (keyword('while'), TT_WHILE),
    (keyword('condition'), TT_CONDITION),
    (keyword('otherwise'), TT_OTHERWISE),
    (keyword('if'), TT_IF),
    (keyword('else'), TT_ELSE),
    (keyword('then'), TT_THEN),
    (keyword('of'), TT_OF),
    (keyword('match'), TT_MATCH),
    (keyword('fun'), TT_FUN),
    (keyword('end'), TT_END),
    (keyword('and'), TT_AND),
    (keyword('or'), TT_OR),
    (keyword('true'), TT_TRUE),
    (keyword('false'), TT_FALSE),
    (keyword('nil'), TT_NIL),
    (keyword('throw'), TT_THROW),
    (keyword('try'), TT_TRY),
    (keyword('catch'), TT_CATCH),
    (keyword('finally'), TT_FINALLY),
    (keyword('generic'), TT_GENERIC),
    (keyword('specify'), TT_SPECIFY),
    (keyword('trait'), TT_TRAIT),
    # (keyword('module'), TT_MODULE),

    (keyword('export'), TT_EXPORT),
    (keyword('import'), TT_IMPORT),
    (keyword('from'), TT_FROM),
    (keyword('hiding'), TT_HIDING),

    (keyword('isa'), TT_ISA),
    (keyword('nota'), TT_NOTA),
    (keyword('kindof'), TT_KINDOF),
    (keyword('of'), TT_OF),
    (keyword('as'), TT_AS),
    (keyword('when'), TT_WHEN),
    (keyword('not'), TT_NOT),

    (keyword('in'), TT_IN),
    (keyword('notin'), TT_NOTIN),
    (keyword('is'), TT_IS),
    (keyword('isnot'), TT_ISNOT),

    (keyword('var'), TT_VAR),
    (keyword('lazy'), TT_LAZY),

    # (keyword('return'), TT_RETURN),

    (keyword('_'), TT_WILDCARD),

    # **********

    (floating_constant, TT_FLOAT),
    (decimal_constant, TT_INT),
    (string_literal, TT_STR),
    (char_const, TT_CHAR),
    (backtick_const, TT_BACKTICK),
    (name, TT_NAME),

    (token('\|'), TT_CASE),
    (token('---[-]*'), TT_END),

    (token('\-\>'), TT_ARROW),
    (token('\.\.\.'), TT_ELLIPSIS),
    (token('\;'), TT_SEMI),
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
    (token('[%s][=]+' % operator_char), TT_OPERATOR),
    (token('[=][%s]+' % operator_char), TT_OPERATOR),
    (token('[%s][:]+' % operator_char), TT_OPERATOR),
    (token('[:][%s]+' % operator_char), TT_OPERATOR),

    (token(':'), TT_COLON),
    (token('='), TT_ASSIGN),

    # that can catch op
    (operator, TT_OPERATOR),
]


def newtoken(type, val, pos, line, column):
    assert isinstance(type, int)
    assert isinstance(val, str)
    assert space.isint(pos)
    assert space.isint(line)
    assert space.isint(column)
    return space.newtuple([space.newint(type), space.newstring_s(val), pos, line, column])

def newtoken_without_meta(type, val):
    return newtoken(type, val, space.newint(-1), space.newint(-1),space.newint(-1),)


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
