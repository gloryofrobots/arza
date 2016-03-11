# ************************ OBIN TOKENS*****************************
TT_ENDSTREAM = 0
TT_INT = 1
TT_FLOAT = 2
TT_STR = 3
TT_CHAR = 4
TT_NAME = 5
TT_TYPENAME = 6
TT_OPERATOR = 7
TT_NEWLINE = 8
TT_FUN = 9
TT_MATCH = 10
TT_CASE = 11
TT_BREAK = 12
TT_CONTINUE = 13
TT_FOR = 14
TT_WHILE = 15
TT_CONSTRUCT = 16
TT_IMPLEMENT = 17
TT_DERIVE = 18
TT_METHOD = 19
TT_UNION = 20
TT_TYPE = 21
TT_CONDITION = 22
TT_IF = 23
TT_THEN = 24
TT_ELSE = 25
TT_WHEN = 26
TT_OF = 27
TT_AS = 28
TT_VAR = 29
TT_LAZY = 30
TT_AND = 31
TT_OR = 32
TT_TRUE = 33
TT_FALSE = 34
TT_TRY = 35
TT_THROW = 36
TT_CATCH = 37
TT_FINALLY = 38
TT_MODULE = 39
TT_IMPORT = 40
TT_FROM = 41
TT_HIDING = 42
TT_EXPORT = 43
TT_TRAIT = 44
TT_END = 45
TT_INFIXL = 46
TT_INFIXR = 47
TT_PREFIX = 48
TT_AMP = 49
TT_ELLIPSIS = 50
TT_WILDCARD = 51
TT_GOTO = 52
TT_ARROW = 53
TT_BACKARROW = 54
TT_AT_SIGN = 55
TT_SEMI = 56
TT_SHARP = 57
TT_LAMBDA = 58
TT_JUXTAPOSITION = 59
TT_INFIX_DOT_LCURLY = 60
TT_LCURLY = 61
TT_RCURLY = 62
TT_COMMA = 63
TT_ASSIGN = 64
TT_INFIX_DOT_LPAREN = 65
TT_LPAREN = 66
TT_RPAREN = 67
TT_LSQUARE = 68
TT_RSQUARE = 69
TT_DOT = 70
TT_COLON = 71
TT_DOUBLE_DOT = 72
TT_BACKTICK = 73
TT_UNKNOWN = 74
# ************************ OBIN TOKENS REPR *****************************
__TT_REPR__ = [u"TT_ENDSTREAM", u"TT_INT", u"TT_FLOAT", u"TT_STR", u"TT_CHAR", u"TT_NAME", u"TT_TYPENAME",
               u"TT_OPERATOR", u"TT_NEWLINE", u"TT_FUN", u"TT_MATCH", u"TT_CASE", u"TT_BREAK", u"TT_CONTINUE",
               u"TT_FOR", u"TT_WHILE", u"TT_CONSTRUCT", u"TT_IMPLEMENT", u"TT_DERIVE", u"TT_METHOD", u"TT_UNION",
               u"TT_TYPE", u"TT_CONDITION", u"TT_IF", u"TT_THEN", u"TT_ELSE", u"TT_WHEN", u"TT_OF", u"TT_AS", u"TT_VAR",
               u"TT_LAZY", u"TT_AND", u"TT_OR", u"TT_TRUE", u"TT_FALSE", u"TT_TRY", u"TT_THROW", u"TT_CATCH",
               u"TT_FINALLY", u"TT_MODULE", u"TT_IMPORT", u"TT_FROM", u"TT_HIDING", u"TT_EXPORT", u"TT_TRAIT",
               u"TT_END", u"TT_INFIXL", u"TT_INFIXR", u"TT_PREFIX", u"TT_AMP", u"TT_ELLIPSIS", u"TT_WILDCARD",
               u"TT_GOTO", u"TT_ARROW", u"TT_BACKARROW", u"TT_AT_SIGN", u"TT_SEMI", u"TT_SHARP", u"TT_LAMBDA",
               u"TT_JUXTAPOSITION", u"TT_INFIX_DOT_LCURLY", u"TT_LCURLY", u"TT_RCURLY", u"TT_COMMA", u"TT_ASSIGN",
               u"TT_INFIX_DOT_LPAREN", u"TT_LPAREN", u"TT_RPAREN", u"TT_LSQUARE", u"TT_RSQUARE", u"TT_DOT", u"TT_COLON",
               u"TT_DOUBLE_DOT", u"TT_BACKTICK", u"TT_UNKNOWN", ]


def token_type_to_str(ttype):
    return __TT_REPR__[ttype]
