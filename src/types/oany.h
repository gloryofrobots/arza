#ifndef OBIN_OTYPES_H_
#define OBIN_OTYPES_H_
/*
Obin q reg
obin_ w reg
OBIN_ e reg

ObinFalse f reg
ObinTrue t reg
ObinNil n reg
ObinNothing g reg
ObinAny a reg
 */
#include "oconf.h"

#define OFALSE 0
#define OTRUE 1
/*
 *   WARNING DO NOT SWAP TYPE SECTIONS,
 *   SPECIAL FIELDS ARE USED TO DETERMINE TYPE RANGES IN CHECKS
 *   #define obin_is_cell_type(type) (type > EOBIN_TYPE_BEGIN_CELL_TYPES && type < EOBIN_TYPE_END_ENUM)
 */
typedef enum _EOBIN_TYPE {
	/* INTERNAL TYPES */
	EOBIN_TYPE_FAILURE = -3,
	EOBIN_TYPE_SUCCESS = -2,

	/* SINGLETON TYPES */
	EOBIN_TYPE_UNKNOWN = -1,
	EOBIN_TYPE_FALSE = 0,
	EOBIN_TYPE_TRUE,
	EOBIN_TYPE_NIL,
	EOBIN_TYPE_NOTHING,
	/** compare types **/
	EOBIN_TYPE_EQUAL,
	EOBIN_TYPE_LESSER,
	EOBIN_TYPE_GREATER,
	/* FIXED TYPES STORED IN ObinAny::data*/
	EOBIN_TYPE_INTEGER,
	EOBIN_TYPE_FLOAT,
	EOBIN_TYPE_CHAR,
	/* CELL TYPES ALLOCATED IN HEAP */
	EOBIN_TYPE_BEGIN_CELL_TYPES,

	EOBIN_BEGIN_COLLECTION_TYPES,
	EOBIN_TYPE_STRING,
	EOBIN_TYPE_ARRAY,
	EOBIN_TYPE_DICT,
	EOBIN_TYPE_TUPLE,
	EOBIN_TYPE_END_COLLECTION_TYPES,

	EOBIN_TYPE_COMPOSITE_CELL,
	EOBIN_TYPE_BIG_INTEGER,

	EOBIN_TYPE_END_CELL_TYPES

} EOBIN_TYPE;

typedef struct _ObinCell ObinCell;


typedef union {
	obin_integer integer_value;
	obin_float float_value;
	struct {
		obin_byte size;
		obin_char data[1];
	} char_value;

	ObinCell * cell;
} ObinValue;

typedef struct {
	EOBIN_TYPE type;
	ObinValue data;
} ObinAny;
/************************* INTERFACES ************************************/
typedef ObinAny (*obin_function)(ObinAny arg);
typedef ObinAny (*obin_function_2)(ObinAny arg1, ObinAny arg2);

typedef ObinAny (*obin_method)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_method_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
/********************** TYPE_TRAIT **************************************/
/* EACH TYPE MUST DEFINE type_trait with this macro */
#define OBIN_DEFINE_TYPE_TRAIT(type) type type_trait

/* METHODS */

typedef struct {
	obin_method __string__;
	obin_method __destroy__;
	obin_method __clone__;
	obin_method_2 __equal__;
	obin_method __hash__;
	obin_method_2 __compare__;
	obin_method __iterator__;
	obin_method_2 __item__;
	obin_method __next__;
} ObinTypeTrait;

/************************* STATE *************************************/
typedef struct _ObinState ObinState;

struct _ObinState {
	ObinAny root;
};


/* we set type value to data enum too,
 * without any reason, just for debugging
*/
#define OBIN_ANY_STATIC_INIT(type) {type, {type}}

ObinAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
ObinAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
ObinAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
ObinAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

ObinAny ObinSuccess = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_SUCCESS);
ObinAny ObinFailure = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FAILURE);

ObinAny ObinLesser = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_LESSER);
ObinAny ObinGreater = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_GREATER);
ObinAny ObinEqual = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_EQUAL);
/********************** ERRORS ************************************/

ObinAny ObinMemoryError;
ObinAny ObinInternalError;
ObinAny ObinInvalidSliceError;
ObinAny ObinTypeError;
ObinAny ObinValueError;
ObinAny ObinIndexError;

#define OBIN_MODULE_NAME(name) OBIN_MODULE_##name##_INIT

#define OBIN_MODULE_DECLARE(name) static int  OBIN_MODULE_NAME(name) = 0
#define OBIN_MODULE_INIT(name) OBIN_MODULE_NAME(name) = 1
#define OBIN_MODULE_CHECK(name) obin_assert(OBIN_MODULE_NAME(name))

/* we mark cells once we initialized them with special type to prevent overwriting types
 *  and values*/
#ifndef NDEBUG
#define OBIN_ANY_CHECK_TYPE(any, type) obin_assert(any.type==type)
#define OBIN_ANY_BEFORE_SET(any) obin_assert(any.type == EOBIN_TYPE_UNKNOWN)
#else
#define OBIN_ANY_CHECK_TYPE(any, type)
#define OBIN_ANY_BEFORE_SET(any)
#endif

/* NEVER FORGET TO CALL THIS BEFORE SETTING TYPE*/
static ObinAny obin_any_new() {
	ObinAny proto;
	proto.type = EOBIN_TYPE_UNKNOWN;
	return proto;
}

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
#define obin_any_float(any) (any.data.float_value)

#define obin_any_cast_cell(any, type) ((type*) (any.data.cell))

#define OBIN_CHECK_TYPE_RANGE(type, min, max) (type > min && type < max)
#define obin_type_is_cell(type) OBIN_CHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_CELL_TYPES, EOBIN_TYPE_END_CELL_TYPES)
#define obin_type_is_collection(type) OBIN_CHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_COLLECTION_TYPES, EOBIN_TYPE_END_COLLECTION_TYPES)

#define obin_any_is_equal(any) (any.type == EOBIN_TYPE_EQUAL)
#define obin_any_is_bool(any) ((any.type == EOBIN_TYPE_TRUE) || (any.type == EOBIN_TYPE_FALSE))
#define obin_any_is_true(any) (any.type == EOBIN_TYPE_TRUE)
#define obin_any_is_success(any) (any.type == EOBIN_TYPE_SUCCESS)
#define obin_any_is_nil(any) (any.type == EOBIN_TYPE_NIL)
#define obin_any_is_nothing(any) (any.type == EOBIN_TYPE_NOTHING)

#define obin_any_is_integer(any) (any.type == EOBIN_TYPE_INTEGER)
#define obin_any_is_float(any) (any.type == EOBIN_TYPE_FLOAT)
#define obin_any_is_char(any) (any.type == EOBIN_TYPE_CHAR)

#define obin_any_is_string(any) (any.type == EOBIN_TYPE_STRING || any.type == EOBIN_TYPE_CHAR)
#define obin_any_is_array(any) (any.type == EOBIN_TYPE_ARRAY)
#define obin_any_is_dict(any) (any.type == EOBIN_TYPE_DICT)
#define obin_any_is_cell(any) obin_type_is_cell(any.type)
#define obin_any_is_collection(any) obin_type_is_collection(any.type)

#define OBIN_END_PROC return ObinNothing

#endif
