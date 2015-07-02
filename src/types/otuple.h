#ifndef OTUPLE_H_
#define OTUPLE_H_
#include <core/obuiltin.h>


ObinAny obin_tuple_new(ObinState* state, ObinAny* items, obin_integer size);
ObinAny obin_tuple_pack(ObinState* state, obin_mem_t size, ...);

#endif /* OTUPLE_H_ */
