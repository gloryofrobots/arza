# ************************ OBIN NODES*****************************
NT_GOTO = 0
NT_TRUE = 1
NT_FALSE = 2
NT_VOID = 3
NT_INT = 4
NT_FLOAT = 5
NT_STR = 6
NT_MULTI_STR = 7
NT_CHAR = 8
NT_WILDCARD = 9
NT_NAME = 10
NT_TEMPORARY = 11
NT_SYMBOL = 12
NT_TYPE = 13
NT_MAP = 15
NT_LIST = 16
NT_TUPLE = 17
NT_UNIT = 18
NT_CONS = 19
NT_COMMA = 20
NT_CASE = 21
NT_FUN = 22
NT_LAMBDA = 23
NT_FARGS = 24
NT_CONDITION = 25
NT_WHEN = 26
NT_MATCH = 27
NT_TRY = 28
NT_MODULE = 29
NT_IMPORT = 30
NT_IMPORT_HIDING = 31
NT_IMPORT_FROM = 32
NT_IMPORT_FROM_HIDING = 33
NT_EXPORT = 34
NT_LOAD = 35
NT_TRAIT = 36
NT_EXTEND = 37
NT_USE = 38
NT_DEF = 39
NT_GENERIC = 40
NT_METHOD = 41
NT_INTERFACE = 42
NT_BIND = 43
NT_THROW = 44
NT_REST = 45
NT_ASSIGN = 46
NT_CALL = 47
NT_JUXTAPOSITION = 48
NT_UNDEFINE = 49
NT_LOOKUP = 50
NT_IMPORTED_NAME = 51
NT_HEAD = 52
NT_TAIL = 53
NT_DROP = 54
NT_RANGE = 55
NT_MODIFY = 56
NT_OF = 57
NT_AS = 58
NT_DELAY = 59
NT_LET = 60
NT_AND = 61
NT_OR = 62
NT_NOT = 63
NT_END_EXPR = 64
NT_END = 65
# ************************ OBIN NODES REPR *****************************
__NT_REPR__ = ["NT_GOTO", "NT_TRUE", "NT_FALSE", "NT_VOID", "NT_INT", "NT_FLOAT", "NT_STR", "NT_MULTI_STR", "NT_CHAR",
               "NT_WILDCARD", "NT_NAME", "NT_TEMPORARY", "NT_SYMBOL", "NT_TYPE", "NT_MAP", "NT_LIST",
               "NT_TUPLE", "NT_UNIT", "NT_CONS", "NT_COMMA", "NT_CASE", "NT_FUN", "NT_LAMBDA", "NT_FARGS",
               "NT_CONDITION", "NT_WHEN", "NT_MATCH", "NT_TRY", "NT_MODULE", "NT_IMPORT", "NT_IMPORT_HIDING",
               "NT_IMPORT_FROM", "NT_IMPORT_FROM_HIDING", "NT_EXPORT", "NT_LOAD", "NT_TRAIT", "NT_EXTEND", "NT_USE",
               "NT_DEF", "NT_GENERIC", "NT_METHOD", "NT_INTERFACE", "NT_BIND", "NT_THROW", "NT_REST", "NT_ASSIGN",
               "NT_CALL", "NT_JUXTAPOSITION", "NT_UNDEFINE", "NT_LOOKUP", "NT_IMPORTED_NAME", "NT_HEAD", "NT_TAIL",
               "NT_DROP", "NT_RANGE", "NT_MODIFY", "NT_OF", "NT_AS", "NT_DELAY", "NT_LET", "NT_AND", "NT_OR", "NT_NOT",
               "NT_END_EXPR", "NT_END", ]


def node_type_to_s(ntype):
    return __NT_REPR__[ntype]
