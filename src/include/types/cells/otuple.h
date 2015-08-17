#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"

obool otuple_init(OState* S);

OAny OTuple_fromArray(OState* S,  OAny size, OAny* items);
OAny OTuple(OState* S, oindex_t size, ...);
#endif /* OTUPLE_H_ */
