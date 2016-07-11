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
NT_INTERFACE = 13
NT_METHOD = 14
NT_GENERIC = 15
NT_TYPE = 16
NT_UNION = 17
NT_MAP = 18
NT_LIST = 19
NT_TUPLE = 20
NT_UNIT = 21
NT_CONS = 22
NT_COMMA = 23
NT_CASE = 24
NT_FUN = 25
NT_FENV = 26
NT_CONDITION = 27
NT_WHEN = 28
NT_MATCH = 29
NT_TRY = 30
NT_MODULE = 31
NT_IMPORT = 32
NT_IMPORT_HIDING = 33
NT_IMPORT_FROM = 34
NT_IMPORT_FROM_HIDING = 35
NT_EXPORT = 36
NT_LOAD = 37
NT_TRAIT = 38
NT_IMPLEMENT = 39
NT_EXTEND = 40
NT_BIND = 41
NT_THROW = 42
NT_REST = 43
NT_ASSIGN = 44
NT_CALL = 45
NT_JUXTAPOSITION = 46
NT_UNDEFINE = 47
NT_LOOKUP = 48
NT_IMPORTED_NAME = 49
NT_HEAD = 50
NT_TAIL = 51
NT_DROP = 52
NT_RANGE = 53
NT_MODIFY = 54
NT_OF = 55
NT_AS = 56
NT_DELAY = 57
NT_LET = 58
NT_AND = 59
NT_OR = 60
NT_END_EXPR = 61
NT_END = 62
# ************************ OBIN NODES REPR *****************************
__NT_REPR__ = ["NT_GOTO", "NT_TRUE", "NT_FALSE", "NT_VOID", "NT_INT", "NT_FLOAT", "NT_STR", "NT_MULTI_STR", "NT_CHAR",
               "NT_WILDCARD", "NT_NAME", "NT_TEMPORARY", "NT_SYMBOL", "NT_INTERFACE", "NT_METHOD", "NT_GENERIC",
               "NT_TYPE", "NT_UNION", "NT_MAP", "NT_LIST", "NT_TUPLE", "NT_UNIT", "NT_CONS", "NT_COMMA", "NT_CASE",
               "NT_FUN", "NT_FENV", "NT_CONDITION", "NT_WHEN", "NT_MATCH", "NT_TRY", "NT_MODULE", "NT_IMPORT",
               "NT_IMPORT_HIDING", "NT_IMPORT_FROM", "NT_IMPORT_FROM_HIDING", "NT_EXPORT", "NT_LOAD", "NT_TRAIT",
               "NT_IMPLEMENT", "NT_EXTEND", "NT_BIND", "NT_THROW", "NT_REST", "NT_ASSIGN", "NT_CALL",
               "NT_JUXTAPOSITION", "NT_UNDEFINE", "NT_LOOKUP", "NT_IMPORTED_NAME", "NT_HEAD", "NT_TAIL", "NT_DROP",
               "NT_RANGE", "NT_MODIFY", "NT_OF", "NT_AS", "NT_DELAY", "NT_LET", "NT_AND", "NT_OR", "NT_END_EXPR",
               "NT_END", ]


def node_type_to_s(ntype):
    return __NT_REPR__[ntype]
