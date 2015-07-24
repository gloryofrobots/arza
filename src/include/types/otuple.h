#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"

/*TODO RENAME IT TO obin_tuple_init */
obin_bool obin_module_tuple_init(OState* state);

OAny obin_tuple_new(OState* state,  OAny size, OAny* items);
OAny obin_tuple_pack(OState* state, obin_index size, ...);
#endif /* OTUPLE_H_ */
