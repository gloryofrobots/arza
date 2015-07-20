#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"

obin_bool obin_module_tuple_init(ObinState* state);

ObinAny obin_tuple_new(ObinState* state,  ObinAny size, ObinAny* items);
ObinAny obin_tuple_pack(ObinState* state, obin_index size, ...);
#endif /* OTUPLE_H_ */
