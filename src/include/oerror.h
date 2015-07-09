#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

typedef struct _ObinErrors {
	ObinAny Error;
	ObinAny MemoryError;
	ObinAny IOError;
	ObinAny InternalError;
	ObinAny InvalidSliceError;
	ObinAny TypeError;
	ObinAny ValueError;
	ObinAny IndexError;
	ObinAny KeyError;
} ObinInternalErrors;

ObinInternalErrors* obin_errors();

obin_bool obin_module_error_init(ObinState* state);
ObinAny obin_raise_error(ObinState* state, ObinAny exception);
ObinAny obin_raise(ObinState* state, ObinAny trait, obin_string message, ObinAny argument);
ObinAny obin_raise_vargs(ObinState* state, ObinAny trait, obin_string message, ...);


#endif /* OERROR_H_ */
