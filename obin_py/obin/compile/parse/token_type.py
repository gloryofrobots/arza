# ************************ OBIN TOKENS*****************************
TT_ENDSTREAM = 0
TT_INT = 1
TT_FLOAT = 2
TT_STR = 3
TT_MULTI_STR = 4
TT_CHAR = 5
TT_NAME = 6
TT_TYPENAME = 7
TT_OPERATOR = 8
TT_FUN = 9
TT_MATCH = 10
TT_WITH = 11
TT_CASE = 12
TT_BREAK = 13
TT_CONTINUE = 14
TT_FOR = 15
TT_WHILE = 16
TT_IMPLEMENT = 17
TT_EXTEND = 18
TT_DEF = 19
TT_TYPE = 20
TT_IF = 21
TT_IN_CASE = 22
TT_ELIF = 23
TT_ELSE = 24
TT_THEN = 25
TT_WHEN = 26
TT_OF = 27
TT_LET = 28
TT_IN = 29
TT_AS = 30
TT_DELAY = 31
TT_AND = 32
TT_OR = 33
TT_TRUE = 34
TT_FALSE = 35
TT_TRY = 36
TT_ENSURE = 37
TT_THROW = 38
TT_CATCH = 39
TT_FINALLY = 40
TT_MODULE = 41
TT_IMPORT = 42
TT_FROM = 43
TT_HIDING = 44
TT_HIDE = 45
TT_EXPORT = 46
TT_TRAIT = 47
TT_END = 48
TT_END_EXPR = 49
TT_INDENT = 50
TT_NEWLINE = 51
TT_INFIXL = 52
TT_INFIXR = 53
TT_PREFIX = 54
TT_ELLIPSIS = 55
TT_WILDCARD = 56
TT_GOTO = 57
TT_ARROW = 58
TT_BACKARROW = 59
TT_AT_SIGN = 60
TT_SHARP = 61
TT_LAMBDA = 62
TT_JUXTAPOSITION = 63
TT_INFIX_DOT_LCURLY = 64
TT_LCURLY = 65
TT_RCURLY = 66
TT_COMMA = 67
TT_ASSIGN = 68
TT_INFIX_DOT_LPAREN = 69
TT_LPAREN = 70
TT_RPAREN = 71
TT_LSQUARE = 72
TT_RSQUARE = 73
TT_DOT = 74
TT_COLON = 75
TT_DOUBLE_COLON = 76
TT_TRIPLE_COLON = 77
TT_DOUBLE_DOT = 78
TT_BACKTICK_NAME = 79
TT_BACKTICK_OPERATOR = 80
TT_UNKNOWN = 81
# ************************ OBIN TOKENS REPR *****************************
__TT_REPR__ = [u"TT_ENDSTREAM", u"TT_INT", u"TT_FLOAT", u"TT_STR", u"TT_MULTI_STR", u"TT_CHAR", u"TT_NAME",
               u"TT_TYPENAME", u"TT_OPERATOR", u"TT_FUN", u"TT_MATCH", u"TT_WITH", u"TT_CASE", u"TT_BREAK",
               u"TT_CONTINUE", u"TT_FOR", u"TT_WHILE", u"TT_IMPLEMENT", u"TT_EXTEND", u"TT_DEF", u"TT_TYPE", u"TT_IF",
               u"TT_IN_CASE", u"TT_ELIF", u"TT_ELSE", u"TT_THEN", u"TT_WHEN", u"TT_OF", u"TT_LET", u"TT_IN", u"TT_AS",
               u"TT_DELAY", u"TT_AND", u"TT_OR", u"TT_TRUE", u"TT_FALSE", u"TT_TRY", u"TT_ENSURE", u"TT_THROW",
               u"TT_CATCH", u"TT_FINALLY", u"TT_MODULE", u"TT_IMPORT", u"TT_FROM", u"TT_HIDING", u"TT_HIDE",
               u"TT_EXPORT", u"TT_TRAIT", u"TT_END", u"TT_END_EXPR", u"TT_INDENT", u"TT_NEWLINE", u"TT_INFIXL",
               u"TT_INFIXR", u"TT_PREFIX", u"TT_ELLIPSIS", u"TT_WILDCARD", u"TT_GOTO", u"TT_ARROW", u"TT_BACKARROW",
               u"TT_AT_SIGN", u"TT_SHARP", u"TT_LAMBDA", u"TT_JUXTAPOSITION", u"TT_INFIX_DOT_LCURLY", u"TT_LCURLY",
               u"TT_RCURLY", u"TT_COMMA", u"TT_ASSIGN", u"TT_INFIX_DOT_LPAREN", u"TT_LPAREN", u"TT_RPAREN",
               u"TT_LSQUARE", u"TT_RSQUARE", u"TT_DOT", u"TT_COLON", u"TT_DOUBLE_COLON", u"TT_TRIPLE_COLON",
               u"TT_DOUBLE_DOT", u"TT_BACKTICK_NAME", u"TT_BACKTICK_OPERATOR", u"TT_UNKNOWN", ]


def token_type_to_s(ttype):
    return __TT_REPR__[ttype]
