__author__ = 'gloryofrobots'


TT_ENDSTREAM = 0
TT_INT = 1
TT_FLOAT = 2
TT_STR = 3
TT_CHAR = 4
TT_NAME = 5
TT_NEWLINE = 6
TT_BREAK = 7
TT_CASE = 8
TT_CONTINUE = 9
TT_DO = 10
TT_ELSE = 11
TT_FOR = 12
TT_WHILE = 13
TT_IF = 14
TT_OF = 15
TT_MATCH = 16
TT_FN = 17
TT_AND = 18
TT_OR = 19
TT_NOT = 20
TT_ELLIPSIS = 21
TT_ADD_ASSIGN = 22
TT_SUB_ASSIGN = 23
TT_MUL_ASSIGN = 24
TT_DIV_ASSIGN = 25
TT_MOD_ASSIGN = 26
TT_AND_ASSIGN = 27
TT_XOR_ASSIGN = 28
TT_OR_ASSIGN = 29
TT_RSHIFT = 30
TT_LSHIFT = 31
TT_ARROW = 32
TT_FAT_ARROW = 33
TT_EQ = 34
TT_LE = 35
TT_GE = 36
TT_NE = 37
TT_SEMI = 38
TT_COLON = 39
TT_LCURLY = 40
TT_RCURLY = 41
TT_COMMA = 42
TT_ASSIGN = 43
TT_LPAREN = 44
TT_RPAREN = 45
TT_LSQUARE = 46
TT_RSQUARE = 47
TT_DOT = 48
TT_BITAND = 49
TT_BITNOT = 50
TT_BITOR = 51
TT_BITXOR = 52
TT_SUB = 53
TT_ADD = 54
TT_MUL = 55
TT_DIVIDE = 56
TT_MOD = 57
TT_LESS = 58
TT_GREATER = 59
TT_QUESTION = 60
TT_UNKNOWN = 61


TT_REPR = {}
TT_REPR[TT_ENDSTREAM] = 'TT_ENDSTREAM'
TT_REPR[TT_INT] = 'TT_INT'
TT_REPR[TT_FLOAT] = 'TT_FLOAT'
TT_REPR[TT_STR] = 'TT_STR'
TT_REPR[TT_CHAR] = 'TT_CHAR'
TT_REPR[TT_NAME] = 'TT_NAME'
TT_REPR[TT_NEWLINE] = 'TT_NEWLINE'
TT_REPR[TT_BREAK] = 'TT_BREAK'
TT_REPR[TT_CASE] = 'TT_CASE'
TT_REPR[TT_CONTINUE] = 'TT_CONTINUE'
TT_REPR[TT_DO] = 'TT_DO'
TT_REPR[TT_ELSE] = 'TT_ELSE'
TT_REPR[TT_FOR] = 'TT_FOR'
TT_REPR[TT_WHILE] = 'TT_WHILE'
TT_REPR[TT_IF] = 'TT_IF'
TT_REPR[TT_OF] = 'TT_OF'
TT_REPR[TT_MATCH] = 'TT_MATCH'
TT_REPR[TT_FN] = 'TT_FN'
TT_REPR[TT_AND] = 'TT_AND'
TT_REPR[TT_OR] = 'TT_OR'
TT_REPR[TT_NOT] = 'TT_NOT'
TT_REPR[TT_ELLIPSIS] = 'TT_ELLIPSIS'
TT_REPR[TT_ADD_ASSIGN] = 'TT_ADD_ASSIGN'
TT_REPR[TT_SUB_ASSIGN] = 'TT_SUB_ASSIGN'
TT_REPR[TT_MUL_ASSIGN] = 'TT_MUL_ASSIGN'
TT_REPR[TT_DIV_ASSIGN] = 'TT_DIV_ASSIGN'
TT_REPR[TT_MOD_ASSIGN] = 'TT_MOD_ASSIGN'
TT_REPR[TT_AND_ASSIGN] = 'TT_AND_ASSIGN'
TT_REPR[TT_XOR_ASSIGN] = 'TT_XOR_ASSIGN'
TT_REPR[TT_OR_ASSIGN] = 'TT_OR_ASSIGN'
TT_REPR[TT_RSHIFT] = 'TT_RSHIFT'
TT_REPR[TT_LSHIFT] = 'TT_LSHIFT'
TT_REPR[TT_ARROW] = 'TT_ARROW'
TT_REPR[TT_FAT_ARROW] = 'TT_FAT_ARROW'
TT_REPR[TT_EQ] = 'TT_EQ'
TT_REPR[TT_LE] = 'TT_LE'
TT_REPR[TT_GE] = 'TT_GE'
TT_REPR[TT_NE] = 'TT_NE'
TT_REPR[TT_SEMI] = 'TT_SEMI'
TT_REPR[TT_COLON] = 'TT_COLON'
TT_REPR[TT_LCURLY] = 'TT_LCURLY'
TT_REPR[TT_RCURLY] = 'TT_RCURLY'
TT_REPR[TT_COMMA] = 'TT_COMMA'
TT_REPR[TT_ASSIGN] = 'TT_ASSIGN'
TT_REPR[TT_LPAREN] = 'TT_LPAREN'
TT_REPR[TT_RPAREN] = 'TT_RPAREN'
TT_REPR[TT_LSQUARE] = 'TT_LSQUARE'
TT_REPR[TT_RSQUARE] = 'TT_RSQUARE'
TT_REPR[TT_DOT] = 'TT_DOT'
TT_REPR[TT_BITAND] = 'TT_BITAND'
TT_REPR[TT_BITNOT] = 'TT_BITNOT'
TT_REPR[TT_BITOR] = 'TT_BITOR'
TT_REPR[TT_BITXOR] = 'TT_BITXOR'
TT_REPR[TT_SUB] = 'TT_SUB'
TT_REPR[TT_ADD] = 'TT_ADD'
TT_REPR[TT_MUL] = 'TT_MUL'
TT_REPR[TT_DIVIDE] = 'TT_DIVIDE'
TT_REPR[TT_MOD] = 'TT_MOD'
TT_REPR[TT_LESS] = 'TT_LESS'
TT_REPR[TT_GREATER] = 'TT_GREATER'
TT_REPR[TT_QUESTION] = 'TT_QUESTION'
TT_REPR[TT_UNKNOWN] = 'TT_UNKNOWN'

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
    ('//[^\n]*', None),
    ('/\*[^\*\/]*\*/', None),
    ('\n', TT_NEWLINE),
    (floating_constant, TT_FLOAT),
    (decimal_constant, TT_INT),
    (string_literal, TT_STR),
    (char_const, TT_CHAR),
    (identifier, TT_NAME),
    ('break', TT_BREAK),
    ('case', TT_CASE),
    ('continue', TT_CONTINUE),
    ('do', TT_DO),
    ('else', TT_ELSE),
    ('for', TT_FOR),
    ('while', TT_WHILE),
    ('if', TT_IF),
    ('of', TT_OF),
    ('match', TT_MATCH),
    ('fn', TT_FN),
    ('and', TT_AND),
    ('or', TT_OR),
    ('not', TT_NOT),
    ('\.\.\.', TT_ELLIPSIS),
    ('\+=', TT_ADD_ASSIGN),
    ('-=', TT_SUB_ASSIGN),
    ('\*=', TT_MUL_ASSIGN),
    ('/=', TT_DIV_ASSIGN),
    ('\%\=', TT_MOD_ASSIGN),
    ('\&\=', TT_AND_ASSIGN),
    ('\^\=', TT_XOR_ASSIGN),
    ('\|=', TT_OR_ASSIGN),
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
    ('\=', TT_ASSIGN),
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
    ('/', TT_DIVIDE),
    ('\%', TT_MOD),
    ('\<', TT_LESS),
    ('\>', TT_GREATER),
    ('\?', TT_QUESTION),
]

RULES2 = [
    ('\d+',             'NUMBER'),
    ('fn',     'fn'),
    ('if',       'if'),
    ('elif',       'elif'),
    ('else',     'else'),
    ('while',    'while'),
    ('for',      'for'),
    ('[a-zA-Z_]\w*',    'symbol'),
    ('\+',              'PLUS'),
    ('\-',              'MINUS'),
    ('\*',              'MULTIPLY'),
    ('\/',              'DIVIDE'),
    ('\]',              'LEFT_SQUARE'),
    ('\[',              'RIGHT_SQUARE'),
    ('\{',              'LEFT_CURLY'),
    ('\}',              'RIGHT_CURLY'),
    ('\(',              'LEFT_PAREN'),
    ('\)',              'RIGHT_PAREN'),
    ('=',               'EQUALS'),
    (',',               'COMA'),
    (':',               'COLON'),
    ('::',              'CONCAT'),
    (';',               'SEMI'),
]
