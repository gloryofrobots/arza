#include <obin.h>

ObinAny obin_bool_new(obin_bool condition){
	if(condition){
		return ObinTrue;
	}

	return ObinFalse;
}

ObinBehavior* obin_bool_behavior() {
	return NULL;
}
