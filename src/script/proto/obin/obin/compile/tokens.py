__author__ = 'gloryofrobots'
from token_type import *

def TT_TO_STR(ttype):
    return TT_REPR[ttype]

## Regexes for use in tokens
##
##

# valid  identifiers (K&R2: A.2.3), plus '$' (supported by some compilers)
identifier = '[a-zA-Z_$][0-9a-zA-Z_$]*'

hex_prefix = '0[xX]'
hex_digits = '[0-9a-fA-F]+'
bin_prefix = '0[bB]'
bin_digits = '[01]+'

integer_suffix_opt = '(([uU]ll)|([uU]LL)|(ll[uU]?)|(LL[uU]?)|([uU][lL])|([lL][uU]?)|[uU])?'
decimal_constant = '(0'+integer_suffix_opt+')|([1-9][0-9]*'+integer_suffix_opt+')'
octal_constant = '0[0-7]*'+integer_suffix_opt
hex_constant = hex_prefix+hex_digits+integer_suffix_opt
bin_constant = bin_prefix+bin_digits+integer_suffix_opt

simple_escape = """([a-zA-Z._~!=&\^\-\\?'"])"""
decimal_escape = """(\d+)"""
hex_escape = """(x[0-9a-fA-F]+)"""

escape_sequence = """(\\("""+simple_escape+'|'+decimal_escape+'|'+hex_escape+'))'
cconst_char = """([^'\\\n]|"""+escape_sequence+')'
char_const = "'"+cconst_char+"'"
char_const = "'[^']+'"

# string literals (K&R2: A.2.6)
string_char = """([^"\\\n]|"""+escape_sequence+')'
string_literal = '"'+string_char+'*"'
wstring_literal = 'L'+string_literal
string_literal = "\"[^\"]*\""

# floating constants (K&R2: A.2.5.3)
exponent_part = """([eE][-+]?[0-9]+)"""
fractional_constant = r"""([0-9]*\.[0-9]+)|([0-9]+\.)"""
floating_constant = '(((('+fractional_constant+')'+exponent_part+'?)|([0-9]+'+exponent_part+'))[FfLl]?)'
binary_exponent_part = '''([pP][+-]?[0-9]+)'''
hex_fractional_constant = '((('+hex_digits+r""")?\."""+hex_digits+')|('+hex_digits+r"""\.))"""
hex_floating_constant = '('+hex_prefix+'('+hex_digits+'|'+hex_fractional_constant+')'+binary_exponent_part+'[FfLl]?)'


RULES = [
    ('\n', TT_NEWLINE),
    (' ', None),
    ('//[^\n]*', None),
    ('/\*[^\*\/]*\*/', None),
    ('break', TT_BREAK),
    # ('case', TT_CASE),
    ('continue', TT_CONTINUE),
    ('do', TT_DO),
    ('else', TT_ELSE),
    ('for', TT_FOR),
    ('while', TT_WHILE),
    ('if', TT_IF),
    ('elif', TT_ELIF),
    ('of', TT_OF),
    ('match', TT_MATCH),
    ('fn', TT_FN),
    ('and', TT_AND),
    ('or', TT_OR),
    ('\\bnot\\b', TT_NOT),
    ('true', TT_TRUE),
    ('false', TT_FALSE),
    ('\\bnil\\b', TT_NIL),
    ('\\bundefined\\b', TT_UNDEFINED),
    # TODO MAYBE DELETE IT
    ('\\braise\\b', TT_RAISE),
    # ('then', TT_THEN),
    # **********
    ('\\bin\\b', TT_IN),
    ('\\bis\\b', TT_IS),
    ('\\bisnot\\b', TT_ISNOT),
    ('\\breturn\\b', TT_RETURN),
    (floating_constant, TT_FLOAT),
    (decimal_constant, TT_INT),
    (string_literal, TT_STR),
    (char_const, TT_CHAR),
    (identifier, TT_NAME),
    ('\.\.\.', TT_ELLIPSIS),
    ('\+=', TT_ADD_ASSIGN),
    ('-=', TT_SUB_ASSIGN),
    ('\*=', TT_MUL_ASSIGN),
    ('/=', TT_DIV_ASSIGN),
    ('\%\=', TT_MOD_ASSIGN),
    ('\&\=', TT_BITAND_ASSIGN),
    ('\^\=', TT_BITXOR_ASSIGN),
    ('\|=', TT_BITOR_ASSIGN),
    ('>>>', TT_URSHIFT),
    ('>>', TT_RSHIFT),
    ('<<', TT_LSHIFT),
    ('->', TT_ARROW),
    ('=>', TT_FAT_ARROW),
    ('==', TT_EQ),
    ('<=', TT_LE),
    ('>=', TT_GE),
    ('!=', TT_NE),
    ('\;', TT_SEMI),
    ('\:', TT_COLON),
    ('\{', TT_LCURLY),
    ('\}', TT_RCURLY),
    ('\,', TT_COMMA),
    ('=', TT_ASSIGN),
    ('\(', TT_LPAREN),
    ('\)', TT_RPAREN),
    ('\[', TT_LSQUARE),
    ('\]', TT_RSQUARE),
    ('\.', TT_DOT),
    ('\&', TT_BITAND),
    ('\~', TT_BITNOT),
    ('\|', TT_BITOR),
    ('\^', TT_BITXOR),
    ('\-', TT_SUB),
    ('\+', TT_ADD),
    ('\*', TT_MUL),
    ('/', TT_DIV),
    ('\%', TT_MOD),
    ('\<', TT_LT),
    ('\>', TT_GT),
    ('\\\\', TT_BACKSLASH),
    ('`', TT_BACKTICK),
]

