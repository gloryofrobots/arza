#ifndef OCOLLECTION_H_
#define OCOLLECTION_H_

#include "obuiltin.h"

OAny obin_sequence_iterator_new(OState* state, OAny sequence);
OAny obin_collection_compare(OState * state, OAny self, OAny other);
#endif
