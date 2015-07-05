#ifndef OCOLLECTION_H_
#define OCOLLECTION_H_

#include "obuiltin.h"

ObinAny obin_sequence_iterator_new(ObinState* state, ObinAny sequence);
ObinAny obin_collection_compare(ObinState * state, ObinAny self, ObinAny other);
#endif
