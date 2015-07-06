#ifndef OBUILTIN_H_
#define OBUILTIN_H_
/* TODO remove obin_any_xxx to obin_to_xxx */
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

	EOBIN_TYPE_OBJECT,

	EOBIN_TYPE_END_CELL_TYPES,

	EOBIN_TYPE_EXCEPTION,
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

/************************* STATE *************************************/
typedef struct _ObinState ObinState;
typedef struct _ObinMemory ObinMemory;
struct _ObinState {
	ObinAny globals;
	ObinMemory* memory;
};

/* we set type value to data enum too,
 * without any reason, just for debugging
*/

#define OBIN_ANY_STATIC_INIT(type) {type, {type}}
#define OBIN_ANY_INTEGER_INIT(type, value) {type, {value}}

static ObinAny ObinFalse = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_FALSE);
static ObinAny ObinTrue = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_TRUE);
static ObinAny ObinNil = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NIL);
static ObinAny ObinNothing = OBIN_ANY_STATIC_INIT(EOBIN_TYPE_NOTHING);

static ObinAny ObinLesser = OBIN_ANY_INTEGER_INIT(EOBIN_TYPE_INTEGER, -1);
static ObinAny ObinGreater = OBIN_ANY_INTEGER_INIT(EOBIN_TYPE_INTEGER, 1);
static ObinAny ObinEqual = OBIN_ANY_INTEGER_INIT(EOBIN_TYPE_INTEGER, 0);

/********************** ERRORS ************************************/

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
#define obin_any_mem_t(any) (obin_mem_t)(any.data.integer_value)

#define obin_any_float(any) (any.data.float_value)

#define obin_any_cast_cell(any, type) ((type*) (any.data.cell))

#define OBIN_CHECK_TYPE_RANGE(type, min, max) (type > min && type < max)
#define obin_type_is_cell(type) OBIN_CHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_CELL_TYPES, EOBIN_TYPE_END_CELL_TYPES)
#define obin_type_is_collection(type) OBIN_CHECK_TYPE_RANGE(type, EOBIN_TYPE_BEGIN_COLLECTION_TYPES, EOBIN_TYPE_END_COLLECTION_TYPES)

#define obin_any_is_interrupt(any) (any.type == EOBIN_TYPE_INTERRUPT)
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
#define obin_any_is_table(any) (any.type == EOBIN_TYPE_TABLE)
#define obin_any_is_object(any) (any.type == EOBIN_TYPE_OBJECT)
#define obin_any_is_cell(any) obin_type_is_cell(any.type)
#define obin_any_is_collection(any) obin_type_is_collection(any.type)

#define obin_cast(type, value) ((type) value)
#define obin_is_fit_to_memsize(size) (size > 0 && size < OBIN_MAX_CAPACITY)
#define obin_integer_is_fit_to_memsize(any) (obin_is_fit_to_memsize(obin_any_integer(any)))

#define obin_is_stop_iteration(any) (obin_any_is_nothing(any))


/********************** NATIVE_TRAIT **************************************/
typedef ObinAny (*obin_function)(ObinAny arg);
typedef ObinAny (*obin_function_2)(ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_function_3)(ObinAny arg1, ObinAny arg2, ObinAny arg3);

typedef void (*obin_proc)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_method_2_proc)(ObinState* state, ObinAny arg, obin_proc each);

typedef ObinAny (*obin_method)(ObinState* state, ObinAny arg);
typedef ObinAny (*obin_method_2)(ObinState* state, ObinAny arg1, ObinAny arg2);
typedef ObinAny (*obin_method_3)(ObinState* state, ObinAny arg1, ObinAny arg2, ObinAny arg3);


typedef struct {
	obin_method __iterator__;
	obin_method __length__;
	obin_method_2 __getitem__;
	obin_method_3 __setitem__;
	obin_method_2 __hasitem__;
	obin_method_2 __delitem__;
} ObinCollectionTrait;

typedef struct {
	obin_method __next__;
} ObinGeneratorTrait;

typedef struct {
	obin_method __tointeger__;
} ObinNumberTrait;

typedef struct {
	obin_method __tostring__;
	obin_method __destroy__;
	obin_method __clone__;
	obin_method_2 __compare__;
	obin_method __hash__;
	obin_method_2_proc __foreach_internal_objects__;
} ObinBaseTrait;

typedef struct {
	obin_string name;

	ObinBaseTrait* base;
	ObinCollectionTrait* collection;
	ObinGeneratorTrait* generator;
	ObinNumberTrait* number;
} ObinNativeTraits;


/**************************** BUILTINS *******************************************/
/* NEVER FORGET TO CALL THIS BEFORE SETTING TYPE*/

/*ObinAny obin_any_new();
ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell);*/

static ObinAny obin_any_new() {
	ObinAny proto;
	proto.type = EOBIN_TYPE_UNKNOWN;
	return proto;
}


ObinState* obin_init();

ObinAny obin_tostring(ObinState* state, ObinAny self);
ObinAny obin_destroy(ObinState * state, ObinAny self);
ObinAny obin_clone(ObinState * state, ObinAny self);
ObinAny obin_compare(ObinState * state, ObinAny self, ObinAny other);
ObinAny obin_hash(ObinState * state, ObinAny any);
ObinAny obin_equal(ObinState * state, ObinAny any);

ObinAny obin_iterator(ObinState * state, ObinAny iterable);
ObinAny obin_length(ObinState* state, ObinAny self);

ObinAny obin_getitem(ObinState* state, ObinAny self, ObinAny key);
/*shortcuts for tuples and arrays*/
#define obin_getfirst(state, item) obin_getitem(state, item, ObinZero)
#define obin_getsecond(state, item) obin_getitem(state, item, ObinOne)
#define obin_getthird(state, item) obin_getitem(state, item, ObinTwo)

ObinAny obin_setitem(ObinState* state, ObinAny self, ObinAny key, ObinAny value);
ObinAny obin_hasitem(ObinState* state, ObinAny self, ObinAny key);
ObinAny obin_delitem(ObinState* state, ObinAny self, ObinAny key);

ObinAny obin_next(ObinState * state, ObinAny iterator);

ObinAny obin_is(ObinState * state, ObinAny first, ObinAny second);

/*@return list of results from function applied to iterable
ObinAny obin_map(ObinState * state, obin_function function, ObinAny iterable);

//Construct a list from those elements of iterable for which function returns True.
ObinAny obin_filter(ObinState * state, obin_function function, ObinAny iterable);

Apply function of two arguments cumulatively to the items of iterable,
 from left to right, so as to reduce the iterable to a single value..
ObinAny obin_reduce(ObinState * state, obin_function_2 function, ObinAny iterable);
*/

#endif
