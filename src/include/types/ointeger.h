#ifndef OINTEGER_H_
#define OINTEGER_H_

#include "obuiltin.h"

obool OInteger_init(OState* state);


OAny OInteger_new(oint number);

#define OInteger_isFitToMemsize(number) \
	(obin_any_integer(number) > 0 && obin_any_integer(number) < OBIN_MEM_MAX)

#endif /* OINTEGER_H_ */
