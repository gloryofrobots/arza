#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

obin_bool obin_module_error_init(ObinState* state, ObinInternals* internals);
ObinAny obin_raise_error(ObinState* state, ObinAny exception);
ObinAny obin_raise(ObinState* state, ObinAny trait, obin_string message, ObinAny argument);
ObinAny obin_raise_vargs(ObinState* state, ObinAny trait, obin_string message, ...);


#endif /* OERROR_H_ */
