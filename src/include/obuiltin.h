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

OState* obin_init(omem_t heap_size);

void obin_finalise(OState* state);
/*TODO REMOVE obin_destroy FROM API*/
void odestroy(OState * state, OCell* self);

void orelease(OState * state, OAny self);

OAny oequal(OState * state, OAny any, OAny other);

OAny ois(OState * state, OAny first, OAny second);

/*shortcuts for tuples and arrays*/
#define ogetfirst(state, coll) ogetitem(state, coll, OInteger(0))
#define ogetsecond(state, coll) ogetitem(state, coll, OInteger(1))
#define ogetthird(state, coll) ogetitem(state, coll, OInteger(2))

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

OAny otostring(OState* state, OAny self);

OAny otobool(OState* state, OAny self);

OAny oclone(OState* state, OAny self);

OAny ocompare(OState* state, OAny self, OAny arg1);

OAny ohash(OState* state, OAny self);

/************************* COLLECTION **********************************/

OAny oiterator(OState* state, OAny self);

OAny olength(OState* state, OAny self);

OAny ogetitem(OState* state, OAny self, OAny arg1);

OAny ohasitem(OState* state, OAny self, OAny arg1);

OAny odelitem(OState* state, OAny self, OAny arg1);

OAny osetitem(OState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny onext(OState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny otointeger(OState* state, OAny self);

OAny otofloat(OState* state, OAny self);

OAny otopositive(OState* state, OAny self);

OAny otonegative(OState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny oabs(OState* state, OAny self);

OAny oinvert(OState* state, OAny self);

OAny oadd(OState* state, OAny self, OAny arg1);

OAny osubtract(OState* state, OAny self, OAny arg1);

OAny odivide(OState* state, OAny self, OAny arg1);

OAny omultiply(OState* state, OAny self, OAny arg1);

OAny opow(OState* state, OAny self, OAny arg1);

OAny oleftshift(OState* state, OAny self, OAny arg1);

OAny orightshift(OState* state, OAny self, OAny arg1);

OAny omod(OState* state, OAny self, OAny arg1);

OAny oand(OState* state, OAny self, OAny arg1);

OAny oor(OState* state, OAny self, OAny arg1);

OAny oxor(OState* state, OAny self, OAny arg1);


#endif
