#ifndef OBOOL_H_
#define OBOOL_H_

#include "obuiltin.h"

OAny OBool(obool condition);
OAny OBool_fromAny(OAny condition);

obool obool_init(OState* S);

#endif /* OBOOL_H_ */
