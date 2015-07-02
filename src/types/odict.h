#ifndef ODICT_H
#define ODICT_H
#include <core/obuiltin.h>

ObinAny obin_dict_new(ObinState* state, ObinAny size);

ObinAny obin_dict_clear(ObinState* state, ObinAny self);
ObinAny obin_dict_update(ObinState* state, ObinAny self, ObinAny other);
#endif
