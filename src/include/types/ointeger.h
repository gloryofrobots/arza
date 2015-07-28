#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "obuiltin.h"

obool ointeger_init(OState* S);


OAny OInteger(oint number);
OAny OInteger_fromCFloat(ofloat number);
OAny OInteger_fromFloat(OAny number);
OBehavior* OInteger_behavior();

#define OInteger_isFitToMemsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

#endif /* OINTEGER_H_ */
