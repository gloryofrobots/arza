#ifndef OTABLE_H
#define OTABLE_H
#include "obuiltin.h"

obool OTable_init(OState* state);

OAny OTable_new(OState* state, OAny size);

OAny OTable_clear(OState* state, OAny self);
OAny OTable_merge(OState* state, OAny self, OAny other);

/*return iterators*/
OAny OTable_items(OState* state, OAny self);
OAny OTable_keys(OState* state, OAny self);
OAny OTable_values(OState* state, OAny self);
#endif
