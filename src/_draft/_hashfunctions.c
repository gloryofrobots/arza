
static void
Float_hash (st_machine *machine)
{
    st_oop receiver = ST_STACK_POP (machine);
    unsigned int hash = 0;
    int result;
    double value;
    unsigned char *c;

    value = st_float_value (receiver);

    if (value == 0)
	value = fabs (value);

    c = (unsigned char *) & value;
    for (int i = 0; i < sizeof (double); i++) {
	hash = (hash * 971) ^ c[i];
    }

    result = hash;

    if (result < 0)
	result = -result;

    ST_STACK_PUSH (machine, st_smi_new (result));
}
/*PARTIALY STOLEN FROM Python*/
/*NOT USED FOR NOW*/
static OAny __hash__(OState* S, OAny self) {
	ofloat v;
	ofloat intpart, fractpart;
	oint hipart;
	oint x;             /* the final hash value */
	/* This is designed so that  numbers of different types
	 * that compare equal hash to the same value; otherwise comparisons
	 * of mapping keys will turn out weird.
	 */
	_CHECK_SELF_TYPE(S, self, __hash__);

	v = _float(self);
	if (!__oisfinite(v)) {
		if (__oisinf(v)) {
			return OInteger(v < 0 ? -271828 : 314159);
		}
		else {
			return OInteger(0);
		}
	}

	fractpart = __omodf(v, &intpart);
	if (fractpart == 0.0) {
		/* This must return the same hash as an equal int or long. */
		if (intpart > OINT_MAX/2 || -intpart > OINT_MAX/2) {
			/* Convert to long and use its hash. */
			return OFloat_toInteger(self);
		}
		/* Fits in a C long == a Python int, so is its own hash. */
		x = (oint)intpart;
		return OInteger(x);
	}
	/*Making it simpler than python here */
	x = (oint)hipart & (oint)intpart;
	x = x * (oint) v;
	return OInteger(x);
}

long
_Py_HashPointer(void *p)
{
    long x;
    size_t y = (size_t)p;
    /* bottom 3 or 4 bits are likely to be 0; rotate y by 4 to avoid
       excessive hash collisions for dicts and sets */
    y = (y >> 4) | (y << (8 * sizeof(opointer) - 4));
    x = (long)y;
    if (x == -1)
        x = -2;
    return x;
}
