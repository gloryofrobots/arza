#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

obin_bool obin_module_error_init(OState* state);
OAny obin_raise_error(OState* state, OAny exception);
OAny obin_raise(OState* state, OAny trait, obin_string message, OAny argument);
OAny obin_raise_vargs(OState* state, OAny trait, obin_string message, ...);


#endif /* OERROR_H_ */
