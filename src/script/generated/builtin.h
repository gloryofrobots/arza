
/************************* BASE **********************************/

OAny otostring(OState* state, OAny self);

OAny otobool(OState* state, OAny self);

OAny oclone(OState* state, OAny self);

OAny ocompare(OState* state, OAny self, OAny arg1);

OAny ohash(OState* state, OAny self);

/************************* COLLECTION **********************************/

OAny oiterator(OState* state, OAny self);

OAny olength(OState* state, OAny self);

OAny ogetitem(OState* state, OAny self, OAny arg1);

OAny ohasitem(OState* state, OAny self, OAny arg1);

OAny odelitem(OState* state, OAny self, OAny arg1);

OAny osetitem(OState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny onext(OState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny otointeger(OState* state, OAny self);

OAny otofloat(OState* state, OAny self);

OAny otopositive(OState* state, OAny self);

OAny otonegative(OState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny oabs(OState* state, OAny self);

OAny oinvert(OState* state, OAny self);

OAny oadd(OState* state, OAny self, OAny arg1);

OAny osubtract(OState* state, OAny self, OAny arg1);

OAny odivide(OState* state, OAny self, OAny arg1);

OAny omultiply(OState* state, OAny self, OAny arg1);

OAny opow(OState* state, OAny self, OAny arg1);

OAny oleftshift(OState* state, OAny self, OAny arg1);

OAny orightshift(OState* state, OAny self, OAny arg1);

OAny omod(OState* state, OAny self, OAny arg1);

OAny oand(OState* state, OAny self, OAny arg1);

OAny oor(OState* state, OAny self, OAny arg1);

OAny oxor(OState* state, OAny self, OAny arg1);
