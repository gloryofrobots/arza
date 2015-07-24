#ifndef OCOLLECTION_H_
#define OCOLLECTION_H_

#include "obuiltin.h"

OAny obin_sequence_iterator_new(ObinState* state, OAny sequence);
OAny obin_collection_compare(ObinState * state, OAny self, OAny other);
#endif
