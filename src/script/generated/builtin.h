
/************************* BASE **********************************/

OAny obin_tostring(ObinState* state, OAny self);

OAny obin_tobool(ObinState* state, OAny self);

OAny obin_clone(ObinState* state, OAny self);

OAny obin_compare(ObinState* state, OAny self, OAny arg1);

OAny obin_hash(ObinState* state, OAny self);

/************************* COLLECTION **********************************/

OAny obin_iterator(ObinState* state, OAny self);

OAny obin_length(ObinState* state, OAny self);

OAny obin_getitem(ObinState* state, OAny self, OAny arg1);

OAny obin_hasitem(ObinState* state, OAny self, OAny arg1);

OAny obin_delitem(ObinState* state, OAny self, OAny arg1);

OAny obin_setitem(ObinState* state, OAny self, OAny arg1, OAny arg2);

/************************* GENERATOR **********************************/

OAny obin_next(ObinState* state, OAny self);

/************************* NUMBER_CAST **********************************/

OAny obin_tointeger(ObinState* state, OAny self);

OAny obin_tofloat(ObinState* state, OAny self);

OAny obin_topositive(ObinState* state, OAny self);

OAny obin_tonegative(ObinState* state, OAny self);

/************************* NUMBER_OPERATIONS **********************************/

OAny obin_abs(ObinState* state, OAny self);

OAny obin_invert(ObinState* state, OAny self);

OAny obin_add(ObinState* state, OAny self, OAny arg1);

OAny obin_subtract(ObinState* state, OAny self, OAny arg1);

OAny obin_divide(ObinState* state, OAny self, OAny arg1);

OAny obin_multiply(ObinState* state, OAny self, OAny arg1);

OAny obin_pow(ObinState* state, OAny self, OAny arg1);

OAny obin_leftshift(ObinState* state, OAny self, OAny arg1);

OAny obin_rightshift(ObinState* state, OAny self, OAny arg1);

OAny obin_mod(ObinState* state, OAny self, OAny arg1);

OAny obin_and(ObinState* state, OAny self, OAny arg1);

OAny obin_or(ObinState* state, OAny self, OAny arg1);

OAny obin_xor(ObinState* state, OAny self, OAny arg1);
