#ifndef OCOMPOSITE_H_
#define OCOMPOSITE_H_
#include <core/obuiltin.h>
/* cc in method names  is shortcut to composite cell */
ObinAny obin_cc_new(ObinState* state);
ObinAny obin_cc_lookup(ObinState* state, ObinAny name);
ObinAny obin_cc_add_trait(ObinState* state, ObinAny trait);
ObinAny obin_cc_remove_trait(ObinState* state, ObinAny trait);

#endif /* OCOMPOSITE_H_ */
