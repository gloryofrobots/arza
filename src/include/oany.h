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
	EOBIN_TYPE_INTEGER,
	EOBIN_TYPE_CHAR,
	EOBIN_TYPE_FLOAT,
	/* TYPES ALLOCATED IN HEAP WE CALL THEM CELLS */
	EOBIN_TYPE_BEGIN_CELL_TYPES,

	EOBIN_BEGIN_COLLECTION_TYPES,
	EOBIN_TYPE_STRING,
	EOBIN_TYPE_ARRAY,
	EOBIN_TYPE_TABLE,
	EOBIN_TYPE_TUPLE,
	EOBIN_TYPE_END_COLLECTION_TYPES,

	EOBIN_TYPE_CELL,

	EOBIN_TYPE_END_CELL_TYPES,
} EOBIN_TYPE;

typedef struct _ObinCell ObinCell;

typedef union {
	obin_integer integer_value;
	obin_float float_value;
	struct {
		obin_byte size;
		obin_byte char_data;
	} char_value;

	ObinCell * cell;
} ObinValue;

typedef struct {
	EOBIN_TYPE type;
	ObinValue data;
} ObinAny;
/* we mark cells once we initialized them with special type to prevent overwriting types
 *  and values*/
#ifdef ODEBUG
#define OBIN_ANY_CHECK_TYPE(any, type) obin_assert(any.type==type)
#define OBIN_ANY_BEFORE_SET(any) obin_assert(any.type == EOBIN_TYPE_UNKNOWN)
#else
#define OBIN_ANY_CHECK_TYPE(any, type)
#define OBIN_ANY_BEFORE_SET(any)
#endif

#define obin_any_type(any) (any.type)

#define obin_any_init_cell(any, type, cell) \
		OBIN_ANY_BEFORE_SET(any); \
		any.type=type; \
		any.data.cell=cell

#define obin_any_init_integer(any, num) \
		OBIN_ANY_BEFORE_SET(any); \
		any.type=EOBIN_TYPE_INTEGER; \
		any.data.integer_value=num

#define obin_any_init_float(any, num) \
		OBIN_ANY_BEFORE_SET(any); \
		any.type=EOBIN_TYPE_FLOAT; \
		any.data.float_value=num

#define obin_any_cell(any) (any.data.cell)
#define obin_any_integer(any) (any.data.integer_value)
#define obin_any_char(any) (any.data.char_value.char_data)
#define obin_any_mem_t(any) (obin_mem_t)(any.data.integer_value)

#define obin_any_float(any) (any.data.float_value)

#define OBIN_CHECK_TYPE_RANGE(type, min, max) (type > min && type < max)
#define obin_type_is_cell(type) OBIN_CHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_CELL_TYPES, EOBIN_TYPE_END_CELL_TYPES)

#define obin_any_is_bool(any) ((any.type == EOBIN_TYPE_TRUE) || (any.type == EOBIN_TYPE_FALSE))
#define obin_any_is_true(any) (any.type == EOBIN_TYPE_TRUE)
#define obin_any_is_false(any) (any.type == EOBIN_TYPE_FALSE)
#define obin_any_is_nil(any) (any.type == EOBIN_TYPE_NIL)
#define obin_any_is_nothing(any) (any.type == EOBIN_TYPE_NOTHING)

#define obin_any_is_integer(any) (any.type == EOBIN_TYPE_INTEGER)
#define obin_any_is_float(any) (any.type == EOBIN_TYPE_FLOAT)
#define obin_any_is_char(any) (any.type == EOBIN_TYPE_CHAR)

#define obin_any_is_string(any) (any.type == EOBIN_TYPE_STRING || any.type == EOBIN_TYPE_CHAR)
#define obin_any_is_array(any) (any.type == EOBIN_TYPE_ARRAY)
#define obin_any_is_tuple(any) (any.type == EOBIN_TYPE_TUPLE)
#define obin_any_is_table(any) (any.type == EOBIN_TYPE_TABLE)
#define obin_any_is_cell(any) obin_type_is_cell(any.type)

#define obin_is_fit_to_memsize(size) (size > 0 && size < OBIN_MAX_CAPACITY)
#define obin_integer_is_fit_to_memsize(any) (obin_is_fit_to_memsize(obin_any_integer(any)))

#define obin_is_stop_iteration(any) (obin_any_is_nothing(any))

#define OBIN_ANY_STATIC_INIT(type) {type, {type}}
#define OBIN_ANY_INTEGER_INIT(value) {EOBIN_TYPE_INTEGER, {value}}

extern ObinAny ObinFalse;
extern ObinAny ObinTrue;
extern ObinAny ObinNil;
extern ObinAny ObinNothing;


#endif /* OANY_H_ */
