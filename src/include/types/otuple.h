#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "obuiltin.h"


ObinAny obin_tuple_new(ObinState* state, ObinAny* items, obin_integer size);
ObinAny obin_tuple_pack(ObinState* state, obin_mem_t size, ...);

ObinAny obin_tuple1(ObinState* state, ...);
ObinAny obin_tuple2(ObinState* state, ...);
ObinAny obin_tuple3(ObinState* state, ...);
ObinAny obin_tuple4(ObinState* state, ...);

#endif /* OTUPLE_H_ */
