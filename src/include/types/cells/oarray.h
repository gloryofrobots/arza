#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"

obool oarray_init(OState* S);

OAny OArray_fromCArray(OState* S,  OAny size, OAny* items);
OAny OArray_pack(OState* S, oindex_t size, ...);
OAny OArray(OState* S, oindex_t size);


#endif /* OARRAY_H_ */
