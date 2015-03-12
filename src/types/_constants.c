
ObinAny obin_tostring(ObinState* state, ObinAny any) {
	ObinNativeTraits* traits;
	obin_method method;
	ObinContext* ctx;

	ctx = obin_ctx_get();

	switch (any.type) {
	case EOBIN_TYPE_TRUE:
		return ctx->internal_strings.True;
		break;
	case EOBIN_TYPE_FALSE:
		return ctx->internal_strings.False;
		break;
	case EOBIN_TYPE_NIL:
		return ctx->internal_strings.Nil;
		break;
	case EOBIN_TYPE_NOTHING:
		return ctx->internal_strings.Nothing;
		break;

	default:
		method = _base(any, __tostring__);
		if(!method) {
				return obin_raise_type_error(state, "__tostring__ must be supported", any);
		}

		return method(state, any);
	}
}
