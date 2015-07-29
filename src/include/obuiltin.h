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

void obin_finalise(OState* S);
/*TODO REMOVE obin_destroy FROM API*/
void OCell_destroy(OState * S, OCell* self);

void orelease(OState * S, OAny self);

OAny oequal(OState * S, OAny any, OAny other);

OAny ois(OState * S, OAny first, OAny second);

/*shortcuts for tuples and arrays*/
#define ogetfirst(S, coll) ogetitem(S, coll, OInteger(0))
#define ogetsecond(S, coll) ogetitem(S, coll, OInteger(1))
#define ogetthird(S, coll) ogetitem(S, coll, OInteger(2))

/*@return list of results from function applied to iterable
ObinAny obin_map(ObinState * S, obin_function function, ObinAny iterable);

//Construct a list from those elements of iterable for which function returns True.
ObinAny obin_filter(ObinState * S, obin_function function, ObinAny iterable);

Apply function of two arguments cumulatively to the items of iterable,
 from left to right, so as to reduce the iterable to a single value..
ObinAny obin_reduce(ObinState * S, obin_function_2 function, ObinAny iterable);
*/

/*AUTO GENERATED CODE BELOW */
/************************* BASE **********************************/

OAny otostring(OState* S, OAny self);

OAny otobool(OState* S, OAny self);

OAny oclone(OState* S, OAny self);

OAny ocompare(OState* S, OAny self, OAny arg1);

OAny ohash(OState* S, OAny self);

/************************* COLLECTION **********************************/

OAny oiterator(OState* S, OAny self);

OAny olength(OState* S, OAny self);

OAny ogetitem(OState* S, OAny self, OAny arg1);

OAny ohasitem(OState* S, OAny self, OAny arg1);

OAny odelitem(OState* S, OAny self, OAny arg1);

OAny osetitem(OState* S, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny onext(OState* S, OAny self);

/************************* NUMBER **********************************/

OAny otointeger(OState* S, OAny self);

OAny otofloat(OState* S, OAny self);

OAny otonegative(OState* S, OAny self);

OAny oinvert(OState* S, OAny self);

OAny oadd(OState* S, OAny self, OAny arg1);

OAny osubtract(OState* S, OAny self, OAny arg1);

OAny odivide(OState* S, OAny self, OAny arg1);

OAny omultiply(OState* S, OAny self, OAny arg1);

OAny oleftshift(OState* S, OAny self, OAny arg1);

OAny orightshift(OState* S, OAny self, OAny arg1);

OAny omod(OState* S, OAny self, OAny arg1);

OAny obitand(OState* S, OAny self, OAny arg1);

OAny obitor(OState* S, OAny self, OAny arg1);

OAny obitxor(OState* S, OAny self, OAny arg1);

#endif
