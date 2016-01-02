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
fractional_constant = """([0-9]*\.[0-9]+)|([0-9]+\.)"""
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
    # ('case', TT_CASE),
    (keyword('continue'), TT_CONTINUE),
    (keyword('else'), TT_ELSE),
    (keyword('for'), TT_FOR),
    (keyword('while'), TT_WHILE),
    (keyword('if'), TT_IF),
    (keyword('elif'), TT_ELIF),
    (keyword('of'), TT_OF),
    (keyword('match'), TT_MATCH),
    (keyword('fn'), TT_FN),
    (keyword('and'), TT_AND),
    (keyword('or'), TT_OR),
    (keyword('not'), TT_NOT),
    (keyword('true'), TT_TRUE),
    (keyword('false'), TT_FALSE),
    (keyword('nil'), TT_NIL),
    (keyword('undefined'), TT_UNDEFINED),
    (keyword('throw'), TT_THROW),
    (keyword('catch'), TT_CATCH),
    (keyword('generic'), TT_GENERIC),
    (keyword('reify'), TT_REIFY),
    (keyword('trait'), TT_TRAIT),
    (keyword('import'), TT_IMPORT),
    (keyword('from'), TT_FROM),
    (keyword('of'), TT_OF),
    (keyword('as'), TT_AS),
    (keyword('when'), TT_WHEN),
    # **********
    (keyword('in'), TT_IN),
    (keyword('is'), TT_IS),
    (keyword('isnot'), TT_ISNOT),
    (keyword('return'), TT_RETURN),
    (keyword('object'), TT_OBJECT),
    (keyword('outer'), TT_OUTER),
    (floating_constant, TT_FLOAT),
    (decimal_constant, TT_INT),
    (string_literal, TT_STR),
    (char_const, TT_CHAR),
    (identifier, TT_NAME),
    (backtick_const, TT_BACKTICK),
    (token('\.\.\.'), TT_ELLIPSIS),
    (token('\+='), TT_ADD_ASSIGN),
    (token('-='), TT_SUB_ASSIGN),
    (token('\*='), TT_MUL_ASSIGN),
    (token('/='), TT_DIV_ASSIGN),
    (token('\%\='), TT_MOD_ASSIGN),
    (token('\&\='), TT_BITAND_ASSIGN),
    (token('\^\='), TT_BITXOR_ASSIGN),
    (token('\|='), TT_BITOR_ASSIGN),
    (token('>>>'), TT_URSHIFT),
    (token('>>'), TT_RSHIFT),
    (token('<<'), TT_LSHIFT),
    # ('->', TT_ARROW),
    # ('=>', TT_FAT_ARROW),
    (token('=='), TT_EQ),
    (token('<='), TT_LE),
    (token('>='), TT_GE),
    (token('!='), TT_NE),
    (token('\;'), TT_SEMI),
    (token('\:'), TT_COLON),
    (token('\{'), TT_LCURLY),
    (token('\}'), TT_RCURLY),
    (token('\,'), TT_COMMA),
    (token('='), TT_ASSIGN),
    (token('\('), TT_LPAREN),
    (token('\)'), TT_RPAREN),
    (token('\['), TT_LSQUARE),
    (token('\]'), TT_RSQUARE),
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



# ************************ OBIN TOKENS REPR *****************************
__TT_REPR__ = ["TT_ENDSTREAM", "TT_INT", "TT_FLOAT", "TT_STR", "TT_CHAR", "TT_NAME", "TT_NEWLINE", "TT_BREAK",
               "TT_CASE", "TT_CONTINUE", "TT_ELSE", "TT_FOR", "TT_WHILE", "TT_IF", "TT_WHEN", "TT_ELIF", "TT_OF",
               "TT_AS", "TT_MATCH", "TT_FN", "TT_AND", "TT_OR", "TT_NOT", "TT_TRUE", "TT_FALSE", "TT_NIL",
               "TT_UNDEFINED", "TT_THROW", "TT_CATCH", "TT_IN", "TT_IS", "TT_OBJECT", "TT_ISNOT", "TT_OUTER", "TT_FROM",
               "TT_IMPORT", "TT_TRAIT", "TT_GENERIC", "TT_REIFY", "TT_RETURN", "TT_ELLIPSIS", "TT_ADD_ASSIGN",
               "TT_SUB_ASSIGN", "TT_MUL_ASSIGN", "TT_DIV_ASSIGN", "TT_MOD_ASSIGN", "TT_BITAND_ASSIGN",
               "TT_BITXOR_ASSIGN", "TT_BITOR_ASSIGN", "TT_RSHIFT", "TT_URSHIFT", "TT_LSHIFT", "TT_ARROW",
               "TT_FAT_ARROW", "TT_EQ", "TT_LE", "TT_GE", "TT_NE", "TT_SEMI", "TT_COLON", "TT_LCURLY", "TT_RCURLY",
               "TT_COMMA", "TT_ASSIGN", "TT_LPAREN", "TT_RPAREN", "TT_LSQUARE", "TT_RSQUARE", "TT_DOT", "TT_BITAND",
               "TT_BITNOT", "TT_BITOR", "TT_BITXOR", "TT_SUB", "TT_ADD", "TT_MUL", "TT_DIV", "TT_BACKTICK", "TT_MOD",
               "TT_LT", "TT_GT", "TT_UNKNOWN", ]


def token_type_to_str(ttype):
    return __TT_REPR__[ttype]
