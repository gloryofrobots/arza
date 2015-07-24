#include <orandom.h>
#include <time.h>
static OHashSecret _ObinHashSecret;


OHashSecret ohash_secret(){
	return _ObinHashSecret;
}

obool ORandom_init(OState* state){
	_ObinHashSecret.prefix = (oint) time(NULL);
	/*suffix whill contain garbage */

	return OTRUE;
}

