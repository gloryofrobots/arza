#ifndef OTABLE_H
#define OTABLE_H
#include "obuiltin.h"

obin_bool obin_module_table_init(OState* state);

OAny obin_table_new(OState* state, OAny size);

OAny obin_table_clear(OState* state, OAny self);
OAny obin_table_update(OState* state, OAny self, OAny other);

/*return iterators*/
OAny obin_table_items(OState* state, OAny self);
OAny obin_table_keys(OState* state, OAny self);
OAny obin_table_values(OState* state, OAny self);
#endif
