#ifndef OBIN_ORANDOM_H_
#define OBIN_ORANDOM_H_
#include "obuiltin.h"

typedef struct{
	obin_integer prefix;
	obin_integer suffix;
} ObinHashSecret;

ObinHashSecret obin_hash_secret();
void obin_random_init();

#endif /* OBIN_ORANDOM_H_ */
