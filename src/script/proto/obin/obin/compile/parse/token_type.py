# ************************ OBIN TOKENS*****************************
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
TT_ELSE = 10
TT_FOR = 11
TT_WHILE = 12
TT_IF = 13
TT_WHEN = 14
TT_ELIF = 15
TT_OF = 16
TT_AS = 17
TT_MATCH = 18
TT_FUNC = 19
TT_DEF = 20
TT_VAR = 21
TT_LAZY = 22
TT_AND = 23
TT_OR = 24
TT_NOT = 25
TT_TRUE = 26
TT_FALSE = 27
TT_NIL = 28
TT_UNDEFINED = 29
TT_TRY = 30
TT_THROW = 31
TT_CATCH = 32
TT_FINALLY = 33
TT_IN = 34
TT_IS = 35
TT_NOTIN = 36
TT_ISNOT = 37
TT_ISA = 38
TT_NOTA = 39
TT_OUTER = 40
TT_FROM = 41
TT_MODULE = 42
TT_IMPORT = 43
TT_EXPORT = 44
TT_LOAD = 45
TT_USE = 46
TT_TRAIT = 47
TT_GENERIC = 48
TT_SPECIFY = 49
TT_END = 50
TT_RETURN = 51
TT_ELLIPSIS = 52
TT_WILDCARD = 53
TT_GOTO = 54
TT_RSHIFT = 55
TT_URSHIFT = 56
TT_LSHIFT = 57
TT_ARROW = 58
TT_FAT_ARROW = 59
TT_EQ = 60
TT_LE = 61
TT_GE = 62
TT_NE = 63
TT_SEMI = 64
TT_COLON = 65
TT_DOUBLE_COLON = 66
TT_LCURLY = 67
TT_RCURLY = 68
TT_COMMA = 69
TT_ASSIGN = 70
TT_LPAREN = 71
TT_RPAREN = 72
TT_LSQUARE = 73
TT_RSQUARE = 74
TT_DOT = 75
TT_DOUBLE_DOT = 76
TT_BITAND = 77
TT_BITNOT = 78
TT_BITOR = 79
TT_BITXOR = 80
TT_SUB = 81
TT_ADD = 82
TT_MUL = 83
TT_DIV = 84
TT_BACKTICK = 85
TT_MOD = 86
TT_LT = 87
TT_GT = 88
TT_UNKNOWN = 89
# ************************ OBIN TOKENS REPR *****************************
__TT_REPR__ = [u"TT_ENDSTREAM", u"TT_INT", u"TT_FLOAT", u"TT_STR", u"TT_CHAR", u"TT_NAME", u"TT_NEWLINE", u"TT_BREAK",
               u"TT_CASE", u"TT_CONTINUE", u"TT_ELSE", u"TT_FOR", u"TT_WHILE", u"TT_IF", u"TT_WHEN", u"TT_ELIF",
               u"TT_OF", u"TT_AS", u"TT_MATCH", u"TT_FUNC", u"TT_DEF", u"TT_VAR", u"TT_LAZY", u"TT_AND", u"TT_OR",
               u"TT_NOT", u"TT_TRUE", u"TT_FALSE", u"TT_NIL", u"TT_UNDEFINED", u"TT_TRY", u"TT_THROW", u"TT_CATCH",
               u"TT_FINALLY", u"TT_IN", u"TT_IS", u"TT_NOTIN", u"TT_ISNOT", u"TT_ISA", u"TT_NOTA", u"TT_OUTER",
               u"TT_FROM", u"TT_MODULE", u"TT_IMPORT", u"TT_EXPORT", u"TT_LOAD", u"TT_USE", u"TT_TRAIT", u"TT_GENERIC",
               u"TT_SPECIFY", u"TT_END", u"TT_RETURN", u"TT_ELLIPSIS", u"TT_WILDCARD", u"TT_GOTO", u"TT_RSHIFT",
               u"TT_URSHIFT", u"TT_LSHIFT", u"TT_ARROW", u"TT_FAT_ARROW", u"TT_EQ", u"TT_LE", u"TT_GE", u"TT_NE",
               u"TT_SEMI", u"TT_COLON", u"TT_DOUBLE_COLON", u"TT_LCURLY", u"TT_RCURLY", u"TT_COMMA", u"TT_ASSIGN",
               u"TT_LPAREN", u"TT_RPAREN", u"TT_LSQUARE", u"TT_RSQUARE", u"TT_DOT", u"TT_DOUBLE_DOT", u"TT_BITAND",
               u"TT_BITNOT", u"TT_BITOR", u"TT_BITXOR", u"TT_SUB", u"TT_ADD", u"TT_MUL", u"TT_DIV", u"TT_BACKTICK",
               u"TT_MOD", u"TT_LT", u"TT_GT", u"TT_UNKNOWN", ]


def token_type_to_str(ttype):
    return __TT_REPR__[ttype]
