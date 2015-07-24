#ifndef OBOOL_H_
#define OBOOL_H_

#include "obuiltin.h"

OAny obin_bool_new(obool condition);
OAny obin_bool_from_any(OAny condition);

obool obin_module_bool_init(OState* state);

#endif /* OBOOL_H_ */
