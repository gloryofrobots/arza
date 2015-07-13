#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"

ObinAny obin_array_new(ObinState* state, ObinAny size);
ObinAny obin_array_push(ObinState* state, ObinAny self, ObinAny value);
ObinAny obin_array_indexof(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_lastindexof(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_pop(ObinState* state, ObinAny self);
ObinAny obin_array_clear(ObinState* state, ObinAny self);
ObinAny obin_array_removeitem(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_removeat(ObinState* state, ObinAny self, ObinAny position);
ObinAny obin_array_insert(ObinState* state, ObinAny self, ObinAny item, ObinAny position);
ObinAny obin_array_merge(ObinState* state, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* state, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* state, ObinAny self);
/*
 * implemented __add__
 * */
/*
MAYBE IMPLEMENT IT IN SOURCE
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/

#endif /* OARRAY_H_ */
