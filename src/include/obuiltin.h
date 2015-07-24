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

OState* obin_init(obin_mem_t heap_size);

void obin_finalise(OState* state);
/*TODO REMOVE obin_destroy FROM API*/
void obin_destroy(OState * state, OCell* self);

void obin_release(OState * state, OAny self);

OAny obin_equal(OState * state, OAny any, OAny other);

OAny obin_is(OState * state, OAny first, OAny second);

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

OAny obin_tostring(OState* state, OAny self);

OAny obin_tobool(OState* state, OAny self);

OAny obin_clone(OState* state, OAny self);

OAny obin_compare(OState* state, OAny self, OAny arg1);

OAny obin_hash(OState* state, OAny self);

/************************* COLLECTION **********************************/

OAny obin_iterator(OState* state, OAny self);

OAny obin_length(OState* state, OAny self);

OAny obin_getitem(OState* state, OAny self, OAny arg1);

OAny obin_hasitem(OState* state, OAny self, OAny arg1);

OAny obin_delitem(OState* state, OAny self, OAny arg1);

OAny obin_setitem(OState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny obin_next(OState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(OState* state, OAny self);

OAny obin_tofloat(OState* state, OAny self);

OAny obin_topositive(OState* state, OAny self);

OAny obin_tonegative(OState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(OState* state, OAny self);

OAny obin_invert(OState* state, OAny self);

OAny obin_add(OState* state, OAny self, OAny arg1);

OAny obin_subtract(OState* state, OAny self, OAny arg1);

OAny obin_divide(OState* state, OAny self, OAny arg1);

OAny obin_multiply(OState* state, OAny self, OAny arg1);

OAny obin_pow(OState* state, OAny self, OAny arg1);

OAny obin_leftshift(OState* state, OAny self, OAny arg1);

OAny obin_rightshift(OState* state, OAny self, OAny arg1);

OAny obin_mod(OState* state, OAny self, OAny arg1);

OAny obin_and(OState* state, OAny self, OAny arg1);

OAny obin_or(OState* state, OAny self, OAny arg1);

OAny obin_xor(OState* state, OAny self, OAny arg1);

#endif
