#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"

obool otuple_init(OState* state);

OAny OTuple_fromArray(OState* state,  OAny size, OAny* items);
OAny OTuple(OState* state, oindex_t size, ...);
#endif /* OTUPLE_H_ */
