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
OAny OArray_concat(OState* S, OAny self, OAny collection);
/*return new array with self inserted between each collection element*/
OAny OArray_join(OState* S, OAny self, OAny collection);
/*return reversed copy of array*/
OAny OArray_reverse(OState* S, OAny self);
OAny OArray_fill(OState* S, OAny self, OAny item, OAny start, OAny end);

/*
 * implemented __add__
 * */
/*
MAYBE IMPLEMENT IT IN SOURCE
Array.prototype.sort()
Array.prototype.splice()
Array.prototype.slice()
MAY BE INTERESTING THING
Array.prototype.toSource()
*/

#endif /* OARRAY_H_ */
