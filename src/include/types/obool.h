#ifndef OBOOL_H_
#define OBOOL_H_

#include "obuiltin.h"

OAny OBool_new(obool condition);
OAny OBool_fromAny(OAny condition);

obool OBool_init(OState* state);

#endif /* OBOOL_H_ */
