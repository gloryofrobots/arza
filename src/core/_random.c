#include <orandom.h>
#include <time.h>
static ObinHashSecret _ObinHashSecret;

OBIN_MODULE_DECLARE(RANDOM);

ObinHashSecret obin_hash_secret(){
	OBIN_MODULE_CHECK(RANDOM);
	return _ObinHashSecret;
}

obin_bool obin_module_random_init(){
	_ObinHashSecret.prefix = (obin_integer) time(NULL);
	/*suffix whill contain garbage */

	OBIN_MODULE_INIT(RANDOM);
	return OTRUE;
}

