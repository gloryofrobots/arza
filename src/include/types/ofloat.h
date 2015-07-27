#ifndef OFLOAT_H_
#define OFLOAT_H_
#include "obuiltin.h"

OAny OFloat(ofloat number);
obool ofloat_init(OState* S);
OAny OFloat_fromInt(OAny integer);
#endif
