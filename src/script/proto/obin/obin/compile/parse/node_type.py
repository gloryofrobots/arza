# ************************ OBIN NODES*****************************
NT_TRUE = 0
NT_FALSE = 1
NT_NIL = 2
NT_UNDEFINED = 3
NT_INT = 4
NT_FLOAT = 5
NT_STR = 6
NT_CHAR = 7
NT_NAME = 8
NT_FUNC = 9
NT_IF = 10
NT_WHEN = 11
NT_MATCH = 12
NT_ORIGIN = 13
NT_IMPORT = 14
NT_TRAIT = 15
NT_GENERIC = 16
NT_SPECIFY = 17
NT_RETURN = 18
NT_THROW = 19
NT_BREAK = 20
NT_CONTINUE = 21
NT_FOR = 22
NT_WHILE = 23
NT_REST = 24
NT_MAP = 25
NT_COMMA = 26
NT_ASSIGN = 27
NT_CALL = 28
NT_CALL_FROM = 29
NT_LIST = 30
NT_TUPLE = 31
NT_LPAREN = 32
NT_LOOKUP = 33
NT_LOOKUP_SYMBOL = 34
NT_CONS = 35
NT_OF = 36
NT_AS = 37
NT_IN = 38
NT_IS = 39
NT_ISNOT = 40
NT_AND = 41
NT_OR = 42
NT_NOT = 43
NT_EQ = 44
NT_LE = 45
NT_GE = 46
NT_NE = 47
NT_BITAND = 48
NT_BITNOT = 49
NT_BITOR = 50
NT_BITXOR = 51
NT_SUB = 52
NT_ADD = 53
NT_MUL = 54
NT_DIV = 55
NT_BACKTICK = 56
NT_MOD = 57
NT_LT = 58
NT_GT = 59
NT_RSHIFT = 60
NT_URSHIFT = 61
NT_LSHIFT = 62
NT_ADD_ASSIGN = 63
NT_SUB_ASSIGN = 64
NT_MUL_ASSIGN = 65
NT_DIV_ASSIGN = 66
NT_MOD_ASSIGN = 67
NT_BITAND_ASSIGN = 68
NT_BITXOR_ASSIGN = 69
NT_BITOR_ASSIGN = 70
# ************************ OBIN NODES REPR *****************************
__NT_REPR__ = ["NT_TRUE", "NT_FALSE", "NT_NIL", "NT_UNDEFINED", "NT_INT", "NT_FLOAT", "NT_STR", "NT_CHAR", "NT_NAME",
               "NT_FUNC", "NT_IF", "NT_WHEN", "NT_MATCH", "NT_ORIGIN", "NT_IMPORT", "NT_TRAIT", "NT_GENERIC",
               "NT_SPECIFY", "NT_RETURN", "NT_THROW", "NT_BREAK", "NT_CONTINUE", "NT_FOR", "NT_WHILE", "NT_REST",
               "NT_MAP", "NT_COMMA", "NT_ASSIGN", "NT_CALL", "NT_CALL_FROM", "NT_LIST", "NT_TUPLE", "NT_LPAREN",
               "NT_LOOKUP", "NT_LOOKUP_SYMBOL", "NT_CONS", "NT_OF", "NT_AS", "NT_IN", "NT_IS", "NT_ISNOT", "NT_AND",
               "NT_OR", "NT_NOT", "NT_EQ", "NT_LE", "NT_GE", "NT_NE", "NT_BITAND", "NT_BITNOT", "NT_BITOR", "NT_BITXOR",
               "NT_SUB", "NT_ADD", "NT_MUL", "NT_DIV", "NT_BACKTICK", "NT_MOD", "NT_LT", "NT_GT", "NT_RSHIFT",
               "NT_URSHIFT", "NT_LSHIFT", "NT_ADD_ASSIGN", "NT_SUB_ASSIGN", "NT_MUL_ASSIGN", "NT_DIV_ASSIGN",
               "NT_MOD_ASSIGN", "NT_BITAND_ASSIGN", "NT_BITXOR_ASSIGN", "NT_BITOR_ASSIGN", ]


def node_type_to_str(ttype):
    return __NT_REPR__[ttype]