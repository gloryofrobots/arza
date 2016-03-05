
static void Test_Parser(void) {
	OState * S = obin_init(1024 * 1024 * 90);
	OAny result;
	OAny s;

	result = OParser_parseCString(S, "2+3*4");
	s = otostring(S, result);
	printf("%s \n", OString_cstr(S, s));

	omemory_collect(S);
}
