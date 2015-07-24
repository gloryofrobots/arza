#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

obool OError_Init(OState* state);
OAny OError_raise(OState* state, OAny exception);
OAny oraise(OState* state, OAny trait, ostring message, OAny argument);
OAny oraise_vargs(OState* state, OAny trait, ostring message, ...);


#endif /* OERROR_H_ */
