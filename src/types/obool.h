#ifndef OBOOL_H_
#define OBOOL_H_

#include "oany.h"

ObinAny obin_bool_new(obin_bool condition){
	if(condition){
		return ObinTrue;
	}

	return ObinFalse;
}

ObinNativeTraits* obin_bool_type_trait();



#endif /* OBOOL_H_ */
