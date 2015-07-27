#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"

/*TODO RENAME IT TO obin_tuple_init */
obool OTuple_init(OState* state);

OAny OTuple_new(OState* state,  OAny size, OAny* items);
OAny OTuple_pack(OState* state, oindex_t size, ...);
#endif /* OTUPLE_H_ */
