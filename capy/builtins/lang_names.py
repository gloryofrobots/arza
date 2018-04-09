
PREFIX = "arza_"

LEN = "__len__"
NOT = "__not__"
ELEM = "__elem__"
IS = "__is__"
IS_EMPTY = "__is_empty__"
LOAD_MODULE = PREFIX + "load_module"

ISNOT = "__isnot__"
KINDOF = "__kindof__"

# functions used by compiler in code gen
IS_ARRAY = PREFIX + "is_array"
IS_SEQ = PREFIX + "is_seq"
IS_TABLE = PREFIX + "is_table"
DEFCLASS = PREFIX + "defclass"

SLICE = "__slice__"
DROP = "__drop__"
TAKE = "__take__"

AT = "__at__"
PUT = "__put__"
PUT_DEFAULT = "__put_default__"

REST = "__rest__"
FIRST = "__first__"
CONS = "__cons__"

EQ = "__eq__"
GE = "__ge__"

HOLE_PREFIX = "@__hole__"
RANDOM_TRAIT_NAME_PREFIX = "@__trait__"
RANDOM_TYPE_DEC_NAME_PREFIX = "@__type_dec__"

TO_SEQ = PREFIX + "to_seq"
CONCAT = "__concat__"
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
