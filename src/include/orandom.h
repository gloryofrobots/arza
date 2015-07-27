#ifndef OBIN_ORANDOM_H_
#define OBIN_ORANDOM_H_
#include "obuiltin.h"

typedef struct{
	oint prefix;
	oint suffix;
} OHashSecret;

OHashSecret ohash_secret();
obool orandom_init(OState* S);

#endif /* OBIN_ORANDOM_H_ */
