#ifndef OBIN_ORANDOM_H_
#define OBIN_ORANDOM_H_
#include "obuiltin.h"

typedef struct{
	oint prefix;
	oint suffix;
} ObinHashSecret;

ObinHashSecret obin_hash_secret();
obool obin_module_random_init(OState* state);

#endif /* OBIN_ORANDOM_H_ */
