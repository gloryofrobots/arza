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

/*ObinAny obin_any_new();*/

ObinAny obin_any_new();

ObinState* obin_init(obin_mem_t heap_size);

void obin_finalise(ObinState* state);

ObinAny obin_tostring(ObinState* state, ObinAny self);

ObinAny obin_tobool(ObinState* state, ObinAny self);

/*TODO REMOVE IT FROM API*/
void obin_destroy(ObinState * state, ObinCell* self);

void obin_release(ObinState * state, ObinAny self);
ObinAny obin_clone(ObinState * state, ObinAny self);
ObinAny obin_compare(ObinState * state, ObinAny self, ObinAny other);
ObinAny obin_hash(ObinState * state, ObinAny any);
ObinAny obin_equal(ObinState * state, ObinAny any, ObinAny other);

ObinAny obin_iterator(ObinState * state, ObinAny iterable);
ObinAny obin_length(ObinState* state, ObinAny self);

ObinAny obin_getitem(ObinState* state, ObinAny self, ObinAny key);
/*shortcuts for tuples and arrays*/
#define obin_getfirst(state, coll) obin_getitem(state, coll, obin_integer_new(0))
#define obin_getsecond(state, coll) obin_getitem(state, coll, obin_integer_new(1))
#define obin_getthird(state, coll) obin_getitem(state, coll, obin_integer_new(2))

ObinAny obin_setitem(ObinState* state, ObinAny self, ObinAny key, ObinAny value);
ObinAny obin_hasitem(ObinState* state, ObinAny self, ObinAny key);
ObinAny obin_delitem(ObinState* state, ObinAny self, ObinAny key);

ObinAny obin_next(ObinState * state, ObinAny iterator);

ObinAny obin_is(ObinState * state, ObinAny first, ObinAny second);
/*Number*/

ObinAny obin_add(ObinState* state, ObinAny first, ObinAny second);

/*
ObinAny obin_tointeger(ObinState* state, ObinAny self);
ObinAny obin_tofloat(ObinState* state, ObinAny self);
ObinAny obin_topositive(ObinState* state, ObinAny self);
ObinAny obin_tonegative(ObinState* state, ObinAny self);

ObinAny obin_abs(ObinState* state, ObinAny self);
ObinAny obin_invert(ObinState* state, ObinAny self);
ObinAny obin_subtract(ObinState* state, ObinAny first, ObinAny second);

ObinAny obin_divide(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_multiply(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_pow(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_leftshift(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_rightshift(ObinState* state, ObinAny first, ObinAny second);

ObinAny obin_mod(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_and(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_or(ObinState* state, ObinAny first, ObinAny second);
ObinAny obin_xor(ObinState* state, ObinAny first, ObinAny second);
*/

/*@return list of results from function applied to iterable
ObinAny obin_map(ObinState * state, obin_function function, ObinAny iterable);

//Construct a list from those elements of iterable for which function returns True.
ObinAny obin_filter(ObinState * state, obin_function function, ObinAny iterable);

Apply function of two arguments cumulatively to the items of iterable,
 from left to right, so as to reduce the iterable to a single value..
ObinAny obin_reduce(ObinState * state, obin_function_2 function, ObinAny iterable);
*/

#endif
