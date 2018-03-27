
PREFIX = "arza_"

NOT = PREFIX + "not"
ELEM = PREFIX + "elem"
IS = PREFIX + "is"
IS_EMPTY = PREFIX + "is_empty"
LOAD_MODULE = PREFIX + "load_module"

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
DEFCLASS = PREFIX + "defclass"
LENSE = PREFIX + "lense"

CURRY = PREFIX + "curry"

SPECIFY = PREFIX + "specify"
OVERRIDE = PREFIX + "override"
OVERRIDE_HELPER = PREFIX + "__override__"
RECEIVE_HELPER = PREFIX + "__receive__"

AFFIRM_TYPE_DECORATOR = PREFIX + "__affirm_type_decorator__"

SLICE = "__slice__"
DROP = "__drop__"
TAKE = "__take__"

AT = "__at__"
PUT = "__put__"
PUT_DEFAULT = "__put_default__"

REST = "__rest__"
FIRST = "__first__"
CONS = "__cons__"

EQ = "=="
GE = ">="

HOLE_PREFIX = "@__hole__"
RANDOM_TRAIT_NAME_PREFIX = "@__trait__"
RANDOM_TYPE_DEC_NAME_PREFIX = "@__type_dec__"

TO_SEQ = PREFIX + "to_seq"
CONCAT = "++"
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
Object = PREFIX + "Object"
ENV = PREFIX + "__env__"

SVALUEOF = "VALUEOF"

SKIP_ON_AUTO_EXPORT_START = "_"
SKIP_ON_AUTO_EXPORT_MIDDLE = ":"
