#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"


obool obin_module_array_init(OState* state);

OAny obin_array_new(OState* state, OAny size);
OAny obin_array_push(OState* state, OAny self, OAny value);
OAny obin_array_indexof(OState* state, OAny self, OAny item);
OAny obin_array_lastindexof(OState* state, OAny self, OAny item);
OAny obin_array_pop(OState* state, OAny self);
OAny obin_array_clear(OState* state, OAny self);
/*return true if removes something*/
OAny obin_array_remove(OState* state, OAny self, OAny item);
OAny obin_array_insert(OState* state, OAny self, OAny item, OAny position);
OAny obin_array_insert_collection(OState* state, OAny self, OAny collection, OAny position);
/*
 * implemented __add__
 * */
/*
ObinAny obin_array_merge(ObinState* state, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* state, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* state, ObinAny self);
MAYBE IMPLEMENT IT IN SOURCE
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/

#endif /* OARRAY_H_ */
