#ifndef OANY_H_
#define OANY_H_
#include "oconf.h"

/*
 *   WARNING DO NOT SWAP TYPE SECTIONS,
 *   SPECIAL FIELDS ARE USED TO DETERMINE TYPE RANGES IN CHECKS
 *   #define obin_is_cell_type(type) (type > EOBIN_TYPE_BEGIN_CELL_TYPES && type < EOBIN_TYPE_END_ENUM)
 */
typedef enum _EOBIN_TYPE {
	/* SINGLETON TYPES */
	EOBIN_TYPE_UNKNOWN = -1,
	EOBIN_TYPE_FALSE = 0,
	EOBIN_TYPE_TRUE,
	EOBIN_TYPE_NIL,
	EOBIN_TYPE_NOTHING,
	/* FIXED TYPES STORED IN ObinAny::data*/
	EOBIN_TYPE_CHAR,
	EOBIN_TYPE_INTEGER,
	EOBIN_TYPE_FLOAT,
	/* TYPES ALLOCATED IN HEAP WE CALL THEM CELLS */
	EOBIN_TYPE_BEGIN_CELL_TYPES,

	EOBIN_BEGIN_COLLECTION_TYPES,
	EOBIN_TYPE_STRING,
	EOBIN_TYPE_VECTOR,
	EOBIN_TYPE_TABLE,
	EOBIN_TYPE_TUPLE,
	EOBIN_TYPE_END_COLLECTION_TYPES,

	EOBIN_TYPE_CELL,

	EOBIN_TYPE_END_CELL_TYPES,
} EOTYPE;

typedef struct _ObinCell OCell;

typedef union {
	oint integer_value;
	ofloat float_value;
	obyte char_value;
	OCell * cell;
} OValue;

typedef struct {
	/*RENAME TO __type__*/
	EOTYPE type;
	OValue data;
} OAny;

OAny OAny_new(EOTYPE type);

/* we mark cells once we initialized them with special type to prevent overwriting types
 *  and values*/
#ifdef ODEBUG
#define OANY_CHECK_TYPE(any, type) oassert(any.type==type)
#else
#define OANY_CHECK_TYPE(any, type)
#endif

#define OAny_type(any) (any.type)

/*TODO MOVE IT TO MODULES*/

#define OAny_cellVal(any) (any.data.cell)
#define OAny_intVal(any) (any.data.integer_value)
#define OAny_charVal(any) (any.data.char_value)
#define OAny_memVal(any) (omem_t)(any.data.integer_value)

#define OAny_floatVal(any) (any.data.float_value)

#define OCHECK_TYPE_RANGE(type, min, max) (type > min && type < max)
#define OType_isCell(type) OCHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_CELL_TYPES, EOBIN_TYPE_END_CELL_TYPES)

#define OAny_isBool(any) ((any.type == EOBIN_TYPE_TRUE) || (any.type == EOBIN_TYPE_FALSE))
#define OAny_isTrue(any) (any.type == EOBIN_TYPE_TRUE)
#define OAny_isFalse(any) (any.type == EOBIN_TYPE_FALSE)
#define OAny_isNil(any) (any.type == EOBIN_TYPE_NIL)
#define OAny_isNothing(any) (any.type == EOBIN_TYPE_NOTHING)

#define OAny_isInt(any) (any.type == EOBIN_TYPE_INTEGER)
#define OAny_isFloat(any) (any.type == EOBIN_TYPE_FLOAT)
#define OAny_isChar(any) (any.type == EOBIN_TYPE_CHAR)

#define OAny_isString(any) (any.type == EOBIN_TYPE_STRING)
#define OAny_isVector(any) (any.type == EOBIN_TYPE_VECTOR)
#define OAny_isTuple(any) (any.type == EOBIN_TYPE_TUPLE)
#define OAny_isTable(any) (any.type == EOBIN_TYPE_TABLE)
#define OAny_isCell(any) OType_isCell(any.type)

#define OBIN_IS_FIT_TO_MEMSIZE(size) (size > 0 && size < OBIN_MAX_CAPACITY)
#define OInt_isFitToMemsize(any) (OBIN_IS_FIT_TO_MEMSIZE(OAny_intVal(any)))

#define OBIN_IS_STOP_ITERATION(any) (OAny_isNothing(any))

#define OBIN_ANY_STATIC_INIT(type) {type, {type}}
#define OBIN_ANY_INTEGER_INIT(value) {EOBIN_TYPE_INTEGER, {value}}

extern OAny ObinFalse;
extern OAny ObinTrue;
extern OAny ObinNil;
extern OAny ObinNothing;


#endif /* OANY_H_ */
