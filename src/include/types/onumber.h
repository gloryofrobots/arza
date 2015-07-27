#ifndef ONUMBER_H_
#define ONUMBER_H_
#include "obuiltin.h"

obool onumber_init(OState* S);

OAny onumber_from_float(ofloat f);
OAny onumber_from_int(oint i);
OAny onumber_cast_upper(OState* S, OAny any);

#endif /* ONUMBER_H_ */
