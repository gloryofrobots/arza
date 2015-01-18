#ifndef OBIN_OINTERNAL_H_
#define OBIN_OINTERNAL_H_
#include "omemory.h"
#include "olog.h"

/************************************ ANY **************************************************/
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

#define obin_any_init_number(any, num) \
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

#define obin_any_is_bool(any) ((any.type == EOBIN_TYPE_TRUE) || (any.type == EOBIN_TYPE_FALSE))
#define obin_any_is_true(any) (any.type == EOBIN_TYPE_TRUE)
#define obin_any_is_success(any) (any.type == EOBIN_TYPE_SUCCESS)
#define obin_any_is_nil(any) (any.type == EOBIN_TYPE_NIL)
#define obin_any_is_nothing(any) (any.type == EOBIN_TYPE_NOTHING)
#define obin_any_is_integer(any) (any.type == EOBIN_TYPE_INTEGER)
#define obin_any_is_float(any) (any.type == EOBIN_TYPE_FLOAT)
#define obin_any_is_array(any) (any.type == EOBIN_TYPE_ARRAY)
#define obin_any_is_string(any) (any.type == EOBIN_TYPE_STRING)
#define obin_any_is_dict(any) (any.type == EOBIN_TYPE_DICT)
#define obin_any_is_cell(any) obin_type_is_cell(any.type)
#define obin_any_is_collection(any) obin_type_is_collection(any.type)

#define OBIN_END_PROC return ObinNothing

/********************************************** CELL ******************************************/
static ObinAny obin_cell_new(EOBIN_TYPE type, ObinCell* cell) {
	ObinAny result;
	obin_assert(obin_type_is_cell(type));

	result = obin_any_new();

	obin_any_init_cell(result, type, cell);

	return result;
}

/******************************* COLLECTION **************************************/

typedef ObinAny (*obin_collection_iterator)(ObinAny self);

#define OBIN_COLLECTION_TRAIT \
	OBIN_CELL_TRAIT \
	obin_collection_iterator __iter__;

typedef struct {
	OBIN_COLLECTION_TRAIT
} ObinCollectionTrait;

typedef struct {
	OBIN_CELL_HEADER;OBIN_DEFINE_TYPE_TRAIT(ObinCollectionTrait);
} ObinCollection;

/******************************************* TUPLE  ***************************************************/
ObinAny obin_tuple_new(ObinState* state, ObinAny size);
ObinAny obin_tuple_add(ObinState* state, ObinAny item);
ObinAny obin_tuple_build(ObinState* state, obin_mem_t count, ...);
/********************************************** ERROR AND LOG ******************************************/
ObinAny obin_error_new(ObinState* state, ObinAny proto, ObinAny message,
		ObinAny args);
ObinAny obin_raise(ObinState* state, ObinAny exception);

#define _OBIN_RAISE(state, proto, message, argtuple) \
		obin_raise(state, obin_error_new(state, proto, obin_string_new(state, message), argtuple))

#define _OBIN_RAISE_1(state, proto, message, argument) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 1, argument))

#define _OBIN_RAISE_2(state, proto, message, arg1, arg2) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 2, arg1, arg2))

#define _OBIN_RAISE_3(state, proto, message, arg1, arg2, arg3) \
		_OBIN_RAISE(state, proto, message, obin_tuple_build(state, 3, arg1, arg2, arg3))

/* constructors */
/* TODO add __func__ to error and maybe do something like const strings */
#define obin_raise_internal(state) \
		obin_raise(state, ObinInternalError)

#define obin_raise_invalid_argument(state, message, arg) \
		_OBIN_RAISE_1(state, ObinInvalidArgumentError, message, arg)

#define obin_raise_invalid_slice(state, message, start, end) \
		_OBIN_RAISE_2(state, ObinInvalidSliceError, message, start, end)
/******************************************* STRING  ***************************************************/
/* constructors */
ObinAny obin_string_new(ObinState* state, obin_string data);
ObinAny obin_string_new_from_char_array(ObinState* state, obin_char* data,
		obin_mem_t size);
ObinAny obin_string_new_from_string(ObinState* state, ObinAny string);

/* API */
ObinAny obin_string_length(ObinState* state, ObinAny self);

ObinAny obin_string_capitalize(ObinState* state, ObinAny self);
ObinAny obin_string_capitalize_words(ObinState* state, ObinAny self);
ObinAny obin_string_to_lowercase(ObinState* state, ObinAny self);
ObinAny obin_string_to_uppercase(ObinState* state, ObinAny self);

ObinAny obin_string_is_alphanum(ObinState* state, ObinAny self);
ObinAny obin_string_is_alpha(ObinState* state, ObinAny self);
ObinAny obin_string_is_digit(ObinState* state, ObinAny self);
ObinAny obin_string_is_lower(ObinState* state, ObinAny self);
ObinAny obin_string_is_upper(ObinState* state, ObinAny self);
ObinAny obin_string_is_space(ObinState* state, ObinAny self);

/*
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);
/*
 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.
 */
ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count);
ObinAny obin_string_format(ObinState* state, ObinAny format, ...);
ObinAny obin_string_concat(ObinState* state, ObinAny first_part, ...);
ObinAny obin_string_join(ObinState* state, ObinAny collection);
ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator);
ObinAny obin_any_to_string(ObinState* state, ObinAny any);

#define OSTR(state, data) obin_string_new(state, data)
#define ONUM(state, num) obin_number_new(state, num)

/********************************************** NUMBER **************************************************/
static ObinAny obin_number_new(obin_integer number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_number(result, number);
	return result;
}

#define obin_is_number_fit_to_memsize(number) \
	(obin_any_number(number) > 0 && obin_any_number(number) < OBIN_MEM_MAX)

/********************************************** FLOAT *******************************************/

ObinAny obin_float_new(obin_float number) {
	ObinAny result;

	result = obin_any_new();
	obin_any_init_float(result, number);
	return result;
}

/********************************************** ARRAY *******************************************/

ObinAny obin_array_new(ObinState* state, ObinAny _size);

#endif

