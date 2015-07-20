#ifndef OTABLE_H
#define OTABLE_H
#include "obuiltin.h"

obin_bool obin_module_table_init(ObinState* state);

ObinAny obin_table_new(ObinState* state, ObinAny size);

ObinAny obin_table_clear(ObinState* state, ObinAny self);
ObinAny obin_table_update(ObinState* state, ObinAny self, ObinAny other);

/*return iterators*/
ObinAny obin_table_items(ObinState* state, ObinAny self);
ObinAny obin_table_keys(ObinState* state, ObinAny self);
ObinAny obin_table_values(ObinState* state, ObinAny self);
#endif
