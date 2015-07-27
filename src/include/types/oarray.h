#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"


obool oarray_init(OState* S);

OAny OArray(OState* S, OAny size);
OAny OArray_push(OState* S, OAny self, OAny value);
OAny OArray_indexOf(OState* S, OAny self, OAny item);
OAny OArray_lastIndexOf(OState* S, OAny self, OAny item);
OAny OArray_pop(OState* S, OAny self);
OAny OArray_clear(OState* S, OAny self);
/*return true if removes something*/
OAny OArray_remove(OState* S, OAny self, OAny item);
OAny OArray_insert(OState* S, OAny self, OAny item, OAny position);
OAny OArray_insertCollection(OState* S, OAny self, OAny collection, OAny position);
/*
 * implemented __add__
 * */
/*
ObinAny obin_array_merge(ObinState* S, ObinAny self, ObinAny sequence,
		ObinAny start, ObinAny end);
ObinAny obin_array_fill(ObinState* S, ObinAny self, ObinAny item,
		ObinAny start, ObinAny end);
ObinAny obin_array_reverse(ObinState* S, ObinAny self);
MAYBE IMPLEMENT IT IN SOURCE
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.concat()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/

#endif /* OARRAY_H_ */
