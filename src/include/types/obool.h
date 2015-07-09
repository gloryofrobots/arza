#ifndef OBOOL_H_
#define OBOOL_H_

#include "obuiltin.h"

ObinAny obin_bool_new(obin_bool condition);
ObinAny obin_bool_from_any(ObinAny condition);

ObinNativeTraits* obin_bool_traits();


#endif /* OBOOL_H_ */
