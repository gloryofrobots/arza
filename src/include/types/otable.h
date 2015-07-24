#ifndef OTABLE_H
#define OTABLE_H
#include "obuiltin.h"

obin_bool obin_module_table_init(ObinState* state);

OAny obin_table_new(ObinState* state, OAny size);

OAny obin_table_clear(ObinState* state, OAny self);
OAny obin_table_update(ObinState* state, OAny self, OAny other);

/*return iterators*/
OAny obin_table_items(ObinState* state, OAny self);
OAny obin_table_keys(ObinState* state, OAny self);
OAny obin_table_values(ObinState* state, OAny self);
#endif
