#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"


obool oarray_init(OState* state);

OAny OArray(OState* state, OAny size);
OAny OArray_push(OState* state, OAny self, OAny value);
OAny OArray_indexOf(OState* state, OAny self, OAny item);
OAny OArray_lastIndexOf(OState* state, OAny self, OAny item);
OAny OArray_pop(OState* state, OAny self);
OAny OArray_clear(OState* state, OAny self);
/*return true if removes something*/
OAny OArray_remove(OState* state, OAny self, OAny item);
OAny OArray_insert(OState* state, OAny self, OAny item, OAny position);
OAny OArray_insertCollection(OState* state, OAny self, OAny collection, OAny position);
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
