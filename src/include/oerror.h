#ifndef OERROR_H_
#define OERROR_H_

#include "obuiltin.h"

obool oerror_init(OState* S);
OAny OError_raise(OState* S, OAny exception);
OAny oraise(OState* S, OAny trait, ostring message, OAny argument);
OAny oraise_vargs(OState* S, OAny trait, ostring message, ...);


#endif /* OERROR_H_ */
