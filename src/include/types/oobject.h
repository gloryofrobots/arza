#ifndef OOBJECT_H_
#define OOBJECT_H_
#include "obuiltin.h"
/* cc in method names  is shortcut to composite cell */
ObinAny obin_cc_new(ObinState* state);
ObinAny obin_cc_lookup(ObinState* state, ObinAny name);
ObinAny obin_cc_add_trait(ObinState* state, ObinAny trait);
ObinAny obin_cc_remove_trait(ObinState* state, ObinAny trait);

#endif /* OOBJECT_H_ */
