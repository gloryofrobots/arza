
/************************* BASE **********************************/

OAny obin_tostring(OState* state, OAny self);

OAny obin_tobool(OState* state, OAny self);

OAny obin_clone(OState* state, OAny self);

OAny obin_compare(OState* state, OAny self, OAny arg1);

OAny obin_hash(OState* state, OAny self);

/************************* COLLECTION **********************************/

OAny obin_iterator(OState* state, OAny self);

OAny obin_length(OState* state, OAny self);

OAny obin_getitem(OState* state, OAny self, OAny arg1);

OAny obin_hasitem(OState* state, OAny self, OAny arg1);

OAny obin_delitem(OState* state, OAny self, OAny arg1);

OAny obin_setitem(OState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny obin_next(OState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(OState* state, OAny self);

OAny obin_tofloat(OState* state, OAny self);

OAny obin_topositive(OState* state, OAny self);

OAny obin_tonegative(OState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(OState* state, OAny self);

OAny obin_invert(OState* state, OAny self);

OAny obin_add(OState* state, OAny self, OAny arg1);

OAny obin_subtract(OState* state, OAny self, OAny arg1);

OAny obin_divide(OState* state, OAny self, OAny arg1);

OAny obin_multiply(OState* state, OAny self, OAny arg1);

OAny obin_pow(OState* state, OAny self, OAny arg1);

OAny obin_leftshift(OState* state, OAny self, OAny arg1);

OAny obin_rightshift(OState* state, OAny self, OAny arg1);

OAny obin_mod(OState* state, OAny self, OAny arg1);

OAny obin_and(OState* state, OAny self, OAny arg1);

OAny obin_or(OState* state, OAny self, OAny arg1);

OAny obin_xor(OState* state, OAny self, OAny arg1);
