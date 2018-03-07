PREFIX = "arza:lang:"

NOT = PREFIX + "not"
ELEM = PREFIX + "elem"
IS = PREFIX + "is"
IS_EMPTY = PREFIX + "is_empty"

ISNOT = PREFIX + "isnot"
KINDOF = PREFIX + "kindof"
IS_IMPLEMENTED = PREFIX + "is_implemented"

# functions used by compiler in code gen
DESCRIBE = PREFIX + "describe"
IS_INDEXED = PREFIX + "is_indexed"
IS_TUPLE = PREFIX + "is_tuple"
IS_SEQ = PREFIX + "is_seq"
IS_DICT = PREFIX + "is_dict"
LEN = PREFIX + "len"
TYPE = PREFIX + "deftype"
GENERIC = PREFIX + "defgeneric"
INTERFACE = PREFIX + "definterface"

LENSE = PREFIX + "lense"

CURRY = PREFIX + "curry"

SPECIFY = PREFIX + "specify"
OVERRIDE = PREFIX + "override"
OVERRIDE_HELPER = PREFIX + "__override__"
RECEIVE_HELPER = PREFIX + "__receive__"

SLICE = PREFIX + "slice"
DROP = PREFIX + "drop"
TAKE = PREFIX + "take"

AT = PREFIX + "at"
PUT = PREFIX + "put"
PUT_DEFAULT = PREFIX + "put_default"

REST = PREFIX + "rest"
FIRST = PREFIX + "first"
CONS = PREFIX + "cons"

EQ = PREFIX + "=="
GE = PREFIX + ">="

HOLE_PREFIX = "@__hole__"
RANDOM_TRAIT_NAME_PREFIX = "@__trait__"

TO_SEQ = PREFIX + "to_seq"
CONCAT = PREFIX + "++"
APPLY = PREFIX + "apply"
NEGATE = PREFIX + "negate"
CAST = PREFIX + "cast"


TINT = PREFIX + "Int"
TFLOAT = PREFIX + "Float"
TBOOL = PREFIX + "Bool"
TCHAR = PREFIX + "Char"
TSYMBOL = PREFIX + "Symbol"
TSTRING = PREFIX + "String"
TLIST = PREFIX + "List"
TTUPLE = PREFIX + "Tuple"
TMAP = PREFIX + "Map"
TAny = PREFIX + "Any"
TDatatype = PREFIX + "Datatype"
