#include <orandom.h>
#include <time.h>
static ObinHashSecret _ObinHashSecret;


ObinHashSecret obin_hash_secret(){
	return _ObinHashSecret;
}

obool obin_module_random_init(OState* state){
	_ObinHashSecret.prefix = (oint) time(NULL);
	/*suffix whill contain garbage */

	return OTRUE;
}

