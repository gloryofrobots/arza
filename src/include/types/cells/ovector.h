#ifndef OVECTOR_H_
#define OVECTOR_H_
#include "obuiltin.h"

obool ovector_init(OState* S);

OAny OVector(OState* S, OAny size);
OAny OVector_pack(OState* S, oint count, ...);

OAny OVector_push(OState* S, OAny self, OAny value);
OAny OVector_pushCString(OState* S, OAny self, ostring value);
OAny OVector_pushAsString(OState* S, OAny self, OAny value);
OAny OVector_pushInt(OState* S, OAny self, oint value);

OAny OVector_pushMany(OState* S, OAny self, omem_t count, ...);
OAny OVector_indexOf(OState* S, OAny self, OAny item);
OAny OVector_lastIndexOf(OState* S, OAny self, OAny item);
OAny OVector_pop(OState* S, OAny self);
OAny OVector_clear(OState* S, OAny self);
/*return true if removes something*/
OAny OVector_remove(OState* S, OAny self, OAny item);
OAny OVector_insert(OState* S, OAny self, OAny item, OAny position);
OAny OVector_insertCollection(OState* S, OAny self, OAny collection, OAny position);
OAny OVector_concat(OState* S, OAny self, OAny collection);
/*return new array with self inserted between each collection element*/
OAny OVector_join(OState* S, OAny self, OAny collection);
/*reverse array. return self*/
OAny OVector_reverse(OState* S, OAny self);
/*fill array with value. return self*/
OAny OVector_fill(OState* S, OAny self, OAny item, OAny start, OAny end);

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

#endif /* OVECTOR_H_ */
