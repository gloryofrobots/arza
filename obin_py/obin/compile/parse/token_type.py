# ************************ OBIN TOKENS*****************************
TT_ENDSTREAM = 0
TT_INT = 1
TT_FLOAT = 2
TT_STR = 3
TT_CHAR = 4
TT_NAME = 5
TT_TYPENAME = 6
TT_OPERATOR = 7
TT_FUN = 8
TT_MATCH = 9
TT_WITH = 10
TT_CASE = 11
TT_BREAK = 12
TT_CONTINUE = 13
TT_FOR = 14
TT_WHILE = 15
TT_IMPLEMENT = 16
TT_EXTEND = 17
TT_DEF = 18
TT_TYPE = 19
TT_IF = 20
TT_IN_CASE = 21
TT_ELIF = 22
TT_ELSE = 23
TT_THEN = 24
TT_WHEN = 25
TT_OF = 26
TT_LET = 27
TT_IN = 28
TT_AS = 29
TT_LAZY = 30
TT_AND = 31
TT_OR = 32
TT_TRUE = 33
TT_FALSE = 34
TT_TRY = 35
TT_ENSURE = 36
TT_THROW = 37
TT_CATCH = 38
TT_FINALLY = 39
TT_MODULE = 40
TT_IMPORT = 41
TT_FROM = 42
TT_HIDING = 43
TT_HIDE = 44
TT_EXPORT = 45
TT_TRAIT = 46
TT_END = 47
TT_END_EXPR = 48
TT_INDENT = 49
TT_NEWLINE = 50
TT_INFIXL = 51
TT_INFIXR = 52
TT_PREFIX = 53
TT_ELLIPSIS = 54
TT_WILDCARD = 55
TT_GOTO = 56
TT_ARROW = 57
TT_BACKARROW = 58
TT_AT_SIGN = 59
TT_SHARP = 60
TT_LAMBDA = 61
TT_JUXTAPOSITION = 62
TT_INFIX_DOT_LCURLY = 63
TT_LCURLY = 64
TT_RCURLY = 65
TT_COMMA = 66
TT_ASSIGN = 67
TT_INFIX_DOT_LPAREN = 68
TT_LPAREN = 69
TT_RPAREN = 70
TT_LSQUARE = 71
TT_RSQUARE = 72
TT_DOT = 73
TT_COLON = 74
TT_DOUBLE_COLON = 75
TT_TRIPLE_COLON = 76
TT_DOUBLE_DOT = 77
TT_BACKTICK_NAME = 78
TT_BACKTICK_OPERATOR = 79
TT_UNKNOWN = 80
# ************************ OBIN TOKENS REPR *****************************
__TT_REPR__ = [u"TT_ENDSTREAM", u"TT_INT", u"TT_FLOAT", u"TT_STR", u"TT_CHAR", u"TT_NAME", u"TT_TYPENAME",
               u"TT_OPERATOR", u"TT_FUN", u"TT_MATCH", u"TT_WITH", u"TT_CASE", u"TT_BREAK", u"TT_CONTINUE", u"TT_FOR",
               u"TT_WHILE", u"TT_IMPLEMENT", u"TT_EXTEND", u"TT_DEF", u"TT_TYPE", u"TT_IF", u"TT_IN_CASE", u"TT_ELIF",
               u"TT_ELSE", u"TT_THEN", u"TT_WHEN", u"TT_OF", u"TT_LET", u"TT_IN", u"TT_AS", u"TT_LAZY", u"TT_AND",
               u"TT_OR", u"TT_TRUE", u"TT_FALSE", u"TT_TRY", u"TT_ENSURE", u"TT_THROW", u"TT_CATCH", u"TT_FINALLY",
               u"TT_MODULE", u"TT_IMPORT", u"TT_FROM", u"TT_HIDING", u"TT_HIDE", u"TT_EXPORT", u"TT_TRAIT", u"TT_END",
               u"TT_END_EXPR", u"TT_INDENT", u"TT_NEWLINE", u"TT_INFIXL", u"TT_INFIXR", u"TT_PREFIX", u"TT_ELLIPSIS",
               u"TT_WILDCARD", u"TT_GOTO", u"TT_ARROW", u"TT_BACKARROW", u"TT_AT_SIGN", u"TT_SHARP", u"TT_LAMBDA",
               u"TT_JUXTAPOSITION", u"TT_INFIX_DOT_LCURLY", u"TT_LCURLY", u"TT_RCURLY", u"TT_COMMA", u"TT_ASSIGN",
               u"TT_INFIX_DOT_LPAREN", u"TT_LPAREN", u"TT_RPAREN", u"TT_LSQUARE", u"TT_RSQUARE", u"TT_DOT", u"TT_COLON",
               u"TT_DOUBLE_COLON", u"TT_TRIPLE_COLON", u"TT_DOUBLE_DOT", u"TT_BACKTICK_NAME", u"TT_BACKTICK_OPERATOR",
               u"TT_UNKNOWN", ]


def token_type_to_s(ttype):
    return __TT_REPR__[ttype]
