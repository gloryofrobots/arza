static void Test_Integer(void) {
	OState * S = obin_init(1024 * 1024 * 1);
	OAny intmax, intmin, int1, int0, intneg1;
	OAny var1, var2;

	int1 = OInteger(1);
	CU_ASSERT_EQUAL(OAny_toInt(int1), 1);

	intneg1 = OInteger(-1);
	CU_ASSERT_EQUAL(OAny_toInt(intneg1), -1);

	int0 = OInteger(0);
	CU_ASSERT_EQUAL(OAny_toInt(int0), 0);

	intmax = OInteger(OINT_MAX);
	CU_ASSERT_EQUAL(OAny_toInt(intmax), OINT_MAX);
	intmin = OInteger(OINT_MIN);
	CU_ASSERT_EQUAL(OAny_toInt(intmin), OINT_MIN);

	/*__tostring__ */
	var1 = otostring(S, OInteger(42));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "42");
	var1 = otostring(S, OInteger(-42));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "-42");
	var1 = otostring(S, OInteger(0));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "0");
	/*__tobool__ */
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,intmin)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,intmax)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,OInteger(42))));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,OInteger(-42))));
	CU_ASSERT_FALSE(OAny_isTrue(otobool(S,OInteger(0))));
	CU_ASSERT_TRUE(OAny_isFalse(otobool(S,OInteger(0))));

	/**add**/
	var1 = oadd(S, OInteger(1), OInteger(2));
	CU_ASSERT_EQUAL(OAny_toInt(var1), 3);



}
/*
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__hash__ = __hash__;
	__BEHAVIOR__.__compare__ = __compare__;
	__BEHAVIOR__.__tointeger__ = __tointeger__;
	__BEHAVIOR__.__tofloat__ = __tofloat__;
	__BEHAVIOR__.__topositive__ = __topositive__;
	__BEHAVIOR__.__tonegative__ = __tonegative__;
	__BEHAVIOR__.__invert__ = __invert__;
	__BEHAVIOR__.__add__ = __add__;
	__BEHAVIOR__.__subtract__ = __subtract__;
	__BEHAVIOR__.__divide__ = __divide__;
	__BEHAVIOR__.__multiply__ = __multiply__;
	__BEHAVIOR__.__leftshift__ = __leftshift__;
	__BEHAVIOR__.__rightshift__ = __rightshift__;
	__BEHAVIOR__.__mod__ = __mod__;
	__BEHAVIOR__.__bitand__ = __and__;
	__BEHAVIOR__.__bitor__ = __or__;
	__BEHAVIOR__.__bitxor__ = __xor__;
*/
