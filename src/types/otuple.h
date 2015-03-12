#ifndef OTUPLE_H_
#define OTUPLE_H_
#include "oany.h"


ObinAny obin_tuple_new(ObinState* state, ObinAny* elements, ObinAny size);
ObinAny obin_tuple_new_pair(ObinState* state, ObinAny first, ObinAny second);


#endif /* OTUPLE_H_ */
