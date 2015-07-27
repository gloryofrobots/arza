#ifndef OTABLE_H
#define OTABLE_H
#include "obuiltin.h"

obool otable_init(OState* S);

OAny OTable(OState* S, OAny size);

OAny OTable_clear(OState* S, OAny self);
OAny OTable_merge(OState* S, OAny self, OAny other);

/*return iterators*/
OAny OTable_items(OState* S, OAny self);
OAny OTable_keys(OState* S, OAny self);
OAny OTable_values(OState* S, OAny self);
#endif
