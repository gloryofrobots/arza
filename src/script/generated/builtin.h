
/************************* BASE **********************************/

ObinAny obin_tostring(ObinState* state, ObinAny self);

ObinAny obin_tobool(ObinState* state, ObinAny self);

ObinAny obin_clone(ObinState* state, ObinAny self);

ObinAny obin_compare(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_hash(ObinState* state, ObinAny self);

/************************* COLLECTION **********************************/

ObinAny obin_iterator(ObinState* state, ObinAny self);

ObinAny obin_length(ObinState* state, ObinAny self);

ObinAny obin_getitem(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_hasitem(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_delitem(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_setitem(ObinState* state, ObinAny self, ObinAny arg1, ObinAny arg2);

/************************* GENERATOR **********************************/

ObinAny obin_next(ObinState* state, ObinAny self);

/************************* NUMBER_CAST **********************************/

ObinAny obin_tointeger(ObinState* state, ObinAny self);

ObinAny obin_tofloat(ObinState* state, ObinAny self);

ObinAny obin_topositive(ObinState* state, ObinAny self);

ObinAny obin_tonegative(ObinState* state, ObinAny self);

/************************* NUMBER_OPERATIONS **********************************/

ObinAny obin_abs(ObinState* state, ObinAny self);

ObinAny obin_invert(ObinState* state, ObinAny self);

ObinAny obin_add(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_subtract(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_divide(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_multiply(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_pow(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_leftshift(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_rightshift(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_mod(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_and(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_or(ObinState* state, ObinAny self, ObinAny arg1);

ObinAny obin_xor(ObinState* state, ObinAny self, ObinAny arg1);
