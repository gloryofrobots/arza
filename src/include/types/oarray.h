#ifndef OARRAY_H_
#define OARRAY_H_

#include "obuiltin.h"


ObinAny obin_array_new(ObinState* state, ObinAny size);
ObinAny obin_array_append(ObinState* state, ObinAny self, ObinAny value);
ObinAny obin_array_indexof(ObinState* state, ObinAny self, ObinAny item);
ObinAny obin_array_pop(ObinState* state, ObinAny self);
ObinAny obin_array_clear(ObinState* state, ObinAny self);
ObinAny obin_array_remove(ObinState* state, ObinAny self, ObinAny item);

#endif /* OARRAY_H_ */
