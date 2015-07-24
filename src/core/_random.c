#include <orandom.h>
#include <time.h>
static ObinHashSecret _ObinHashSecret;


ObinHashSecret obin_hash_secret(){
	return _ObinHashSecret;
}

obin_bool obin_module_random_init(OState* state){
	_ObinHashSecret.prefix = (obin_integer) time(NULL);
	/*suffix whill contain garbage */

	return OTRUE;
}

