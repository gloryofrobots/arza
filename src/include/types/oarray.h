#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"


obin_bool obin_module_array_init(ObinState* state);

OAny obin_array_new(ObinState* state, OAny size);
OAny obin_array_push(ObinState* state, OAny self, OAny value);
OAny obin_array_indexof(ObinState* state, OAny self, OAny item);
OAny obin_array_lastindexof(ObinState* state, OAny self, OAny item);
OAny obin_array_pop(ObinState* state, OAny self);
OAny obin_array_clear(ObinState* state, OAny self);
/*return true if removes something*/
OAny obin_array_remove(ObinState* state, OAny self, OAny item);
OAny obin_array_insert(ObinState* state, OAny self, OAny item, OAny position);
OAny obin_array_insert_collection(ObinState* state, OAny self, OAny collection, OAny position);
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
