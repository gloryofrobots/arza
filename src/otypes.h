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

	/* FIXED TYPES STORED IN ObinAny::data*/
	EOBIN_TYPE_INTEGER,
	EOBIN_TYPE_FLOAT,

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
/********************** TYPE_TRAIT **************************************/
/* EACH TYPE MUST DEFINE type_trait with this macro */
#define OBIN_DEFINE_TYPE_TRAIT(type) type type_trait

/* METHODS */

typedef struct {
	obin_method __string__;
	obin_method __destroy__;
	obin_method __clone__;
	obin_method __iterator__;
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

/********************** ERRORS ************************************/

ObinAny ObinMemoryError;
ObinAny ObinInternalError;
ObinAny ObinInvalidSliceError;
ObinAny ObinInvalidArgumentError;
#endif
