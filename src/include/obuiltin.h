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
#include "oany.h"
#include "ostate.h"
#include "ocell.h"

/*
#define OBIN_MODULE_NAME(name) OBIN_MODULE_##name##_INIT
#define OBIN_MODULE_DECLARE(name) static int  OBIN_MODULE_NAME(name) = 0
#define OBIN_MODULE_INIT(name) OBIN_MODULE_NAME(name) = 1
#define OBIN_MODULE_CHECK(name) obin_assert(OBIN_MODULE_NAME(name))
*/

/**************************** BUILTINS *******************************************/
/* NEVER FORGET TO CALL THIS BEFORE SETTING TYPE*/

ObinState* obin_init(obin_mem_t heap_size);

void obin_finalise(ObinState* state);
/*TODO REMOVE obin_destroy FROM API*/
void obin_destroy(ObinState * state, OCell* self);

void obin_release(ObinState * state, OAny self);

OAny obin_equal(ObinState * state, OAny any, OAny other);

OAny obin_is(ObinState * state, OAny first, OAny second);

/*shortcuts for tuples and arrays*/
#define obin_getfirst(state, coll) obin_getitem(state, coll, obin_integer_new(0))
#define obin_getsecond(state, coll) obin_getitem(state, coll, obin_integer_new(1))
#define obin_getthird(state, coll) obin_getitem(state, coll, obin_integer_new(2))

/*@return list of results from function applied to iterable
ObinAny obin_map(ObinState * state, obin_function function, ObinAny iterable);

//Construct a list from those elements of iterable for which function returns True.
ObinAny obin_filter(ObinState * state, obin_function function, ObinAny iterable);

Apply function of two arguments cumulatively to the items of iterable,
 from left to right, so as to reduce the iterable to a single value..
ObinAny obin_reduce(ObinState * state, obin_function_2 function, ObinAny iterable);
*/

/*AUTO GENERATED CODE BELOW */

/************************* BASE **********************************/

OAny obin_tostring(ObinState* state, OAny self);

OAny obin_tobool(ObinState* state, OAny self);

OAny obin_clone(ObinState* state, OAny self);

OAny obin_compare(ObinState* state, OAny self, OAny arg1);

OAny obin_hash(ObinState* state, OAny self);

/************************* COLLECTION **********************************/

OAny obin_iterator(ObinState* state, OAny self);

OAny obin_length(ObinState* state, OAny self);

OAny obin_getitem(ObinState* state, OAny self, OAny arg1);

OAny obin_hasitem(ObinState* state, OAny self, OAny arg1);

OAny obin_delitem(ObinState* state, OAny self, OAny arg1);

OAny obin_setitem(ObinState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny obin_next(ObinState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(ObinState* state, OAny self);

OAny obin_tofloat(ObinState* state, OAny self);

OAny obin_topositive(ObinState* state, OAny self);

OAny obin_tonegative(ObinState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(ObinState* state, OAny self);

OAny obin_invert(ObinState* state, OAny self);

OAny obin_add(ObinState* state, OAny self, OAny arg1);

OAny obin_subtract(ObinState* state, OAny self, OAny arg1);

OAny obin_divide(ObinState* state, OAny self, OAny arg1);

OAny obin_multiply(ObinState* state, OAny self, OAny arg1);

OAny obin_pow(ObinState* state, OAny self, OAny arg1);

OAny obin_leftshift(ObinState* state, OAny self, OAny arg1);

OAny obin_rightshift(ObinState* state, OAny self, OAny arg1);

OAny obin_mod(ObinState* state, OAny self, OAny arg1);

OAny obin_and(ObinState* state, OAny self, OAny arg1);

OAny obin_or(ObinState* state, OAny self, OAny arg1);

OAny obin_xor(ObinState* state, OAny self, OAny arg1);

#endif
