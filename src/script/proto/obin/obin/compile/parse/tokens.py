__author__ = 'gloryofrobots'
from obin.compile.parse.token_type import *

# import rpython.rlib.rsre.rsre_re as re


import re


def keyword(literal):
    return re.compile('\\b%s\\b' % literal)


# def token(literal):
#     return literal

token = re.compile

## Regexes for use in tokens
##
##

# valid  identifiers (K&R2: A.2.3), plus '$' (supported by some compilers)
identifier = token('[a-zA-Z_$][0-9a-zA-Z_$]*')

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
    (keyword('else'), TT_ELSE),
    (keyword('for'), TT_FOR),
    (keyword('while'), TT_WHILE),
    (keyword('if'), TT_IF),
    (keyword('elif'), TT_ELIF),
    (keyword('of'), TT_OF),
    (keyword('match'), TT_MATCH),
    (keyword('case'), TT_CASE),
    (keyword('func'), TT_FUNC),
    (keyword('def'), TT_DEF),
    (keyword('end'), TT_END),
    (keyword('and'), TT_AND),
    (keyword('or'), TT_OR),
    (keyword('not'), TT_NOT),
    (keyword('true'), TT_TRUE),
    (keyword('false'), TT_FALSE),
    (keyword('nil'), TT_NIL),
    (keyword('undefined'), TT_UNDEFINED),
    (keyword('throw'), TT_THROW),
    (keyword('try'), TT_TRY),
    (keyword('catch'), TT_CATCH),
    (keyword('finally'), TT_FINALLY),
    (keyword('generic'), TT_GENERIC),
    (keyword('specify'), TT_SPECIFY),
    (keyword('trait'), TT_TRAIT),
    (keyword('module'), TT_MODULE),

    (keyword('import'), TT_IMPORT),
    (keyword('export'), TT_EXPORT),
    (keyword('load'), TT_LOAD),
    (keyword('use'), TT_USE),

    (keyword('from'), TT_FROM),
    (keyword('of'), TT_OF),
    (keyword('as'), TT_AS),
    (keyword('when'), TT_WHEN),

    (keyword('outer'), TT_OUTER),

    (keyword('var'), TT_VAR),
    (keyword('lazy'), TT_LAZY),

    (keyword('in'), TT_IN),
    (keyword('notin'), TT_NOTIN),
    (keyword('is'), TT_IS),
    (keyword('isnot'), TT_ISNOT),

    (keyword('isa'), TT_ISA),
    (keyword('nota'), TT_NOTA),

    (keyword('return'), TT_RETURN),

    (keyword('_'), TT_WILDCARD),

    # **********

    (floating_constant, TT_FLOAT),
    (decimal_constant, TT_INT),
    (string_literal, TT_STR),
    (char_const, TT_CHAR),
    (identifier, TT_NAME),
    (backtick_const, TT_BACKTICK),
    (token('\-\>'), TT_ARROW),
    (token('\.\.\.'), TT_ELLIPSIS),
    (token('\>\>\>'), TT_URSHIFT),
    (token('\>\>'), TT_RSHIFT),
    (token('\<\<'), TT_LSHIFT),
    # ('=>', TT_FAT_ARROW),
    (token('=='), TT_EQ),
    (token('<='), TT_LE),
    (token('>='), TT_GE),
    (token('!='), TT_NE),
    (token('\;'), TT_SEMI),
    (token('\:\:'), TT_DOUBLE_COLON),
    (token('\:'), TT_COLON),
    (token('\{'), TT_LCURLY),
    (token('\}'), TT_RCURLY),
    (token('\,'), TT_COMMA),
    (token('='), TT_ASSIGN),
    (token('\('), TT_LPAREN),
    (token('\)'), TT_RPAREN),
    (token('\['), TT_LSQUARE),
    (token('\]'), TT_RSQUARE),
    (token('\.\.'), TT_DOUBLE_DOT),
    (token('\.'), TT_DOT),
    (token('\&'), TT_BITAND),
    (token('\~'), TT_BITNOT),
    (token('\|'), TT_BITOR),
    (token('\^'), TT_BITXOR),
    (token('\-'), TT_SUB),
    (token('\+'), TT_ADD),
    (token('\*'), TT_MUL),
    (token('/'), TT_DIV),
    (token('\%'), TT_MOD),
    (token('\<'), TT_LT),
    (token('\>'), TT_GT),
]


