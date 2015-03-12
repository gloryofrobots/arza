#ifndef OBIN_ODICT_H
#define OBIN_ODICT_H
#include "oany.h"

ObinAny obin_dict_new(ObinState* state);
ObinAny obin_dict_new_size(ObinState* state, ObinAny size);
ObinAny obin_dict_clone(ObinState* state, ObinAny self);

ObinAny obin_dict_length(ObinState* state, ObinAny self);
ObinAny obin_dict_items(ObinState* state, ObinAny self);
ObinAny obin_dict_keys(ObinState* state, ObinAny self);
ObinAny obin_dict_values(ObinState* state, ObinAny self);

ObinAny obin_dict_at(ObinState* state, ObinAny self, ObinAny key);
ObinAny obin_dict_set(ObinState* state, ObinAny self, ObinAny key, ObinAny value);
ObinAny obin_dict_remove(ObinState* state, ObinAny self, ObinAny key);
ObinAny obin_dict_has(ObinState* state, ObinAny self, ObinAny key);

ObinAny obin_dict_clear(ObinState* state, ObinAny self);
ObinAny obin_dict_update(ObinState* state, ObinAny self, ObinAny other);
#endif
