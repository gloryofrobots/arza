static void _ints_test_compare(OState* state, OAny int1, OAny int2) {

}
static void Test_Integer(void) {
	printf("OINT_MAX ="OBIN_INTEGER_FORMATTER" OINT_MIN="OBIN_INTEGER_FORMATTER, OINT_MAX, OINT_MIN);
	/*TODO overflows*/

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
	var1 = otostring(S, intmax);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "2147483647");
	var1 = otostring(S, intmin);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "-2147483648");

	/*__tobool__ */
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,intmin)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,intmax)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,OInteger(42))));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S,OInteger(-42))));
	CU_ASSERT_FALSE(OAny_isTrue(otobool(S,OInteger(0))));
	CU_ASSERT_TRUE(OAny_isFalse(otobool(S,OInteger(0))));

	/**clone**/
	var2 = int1;
	var1 = oclone(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = int0;
	var1 = oclone(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmin;
	var1 = oclone(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmax;
	var1 = oclone(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));

	/**hash**/
	var2 = int1;
	var1 = ohash(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = int0;
	var1 = ohash(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmin;
	var1 = ohash(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmax;
	var1 = ohash(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));

	/**__tointeger__**/
	var2 = int1;
	var1 = otointeger(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = int0;
	var1 = otointeger(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmin;
	var1 = otointeger(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));
	var2 = intmax;
	var1 = otointeger(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), OAny_toInt(var1));

	/**__tonegative__**/
	var2 = int1;
	var1 = otonegative(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), -1*OAny_toInt(var1));
	var2 = int0;
	var1 = otonegative(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), -1*OAny_toInt(var1));
	var2 = OInteger(OINT_MIN + 1);
	var1 = otonegative(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), -1*OAny_toInt(var1));
	var2 = intmax;
	var1 = otonegative(S, var2);
	CU_ASSERT_EQUAL(OAny_toInt(var2), -1*OAny_toInt(var1));
	/**__compare__**/
	var1 = ocompare(S, intmax, intmin);
	CU_ASSERT_EQUAL(OAny_toInt(var1), 1);
	var1 = ocompare(S, intmin, intmax);
	CU_ASSERT_EQUAL(OAny_toInt(var1), -1);
	var1 = ocompare(S, intmin, intmin);
	CU_ASSERT_EQUAL(OAny_toInt(var1), 0);
	var1 = ocompare(S, intmax, intmax);
	CU_ASSERT_EQUAL(OAny_toInt(var1), 0);
	var1 = ocompare(S, int0, int0);
	CU_ASSERT_EQUAL(OAny_toInt(var1), 0);
	/*__invert__*/
	CU_ASSERT_EQUAL(OAny_toInt(oinvert(S, int1)), -2);
	CU_ASSERT_EQUAL(OAny_toInt(oinvert(S, int0)), -1);
	CU_ASSERT_EQUAL(OAny_toInt(oinvert(S, intmax)), OINT_MIN);
	CU_ASSERT_EQUAL(OAny_toInt(oinvert(S, intmin)), OINT_MAX);
	/*__invert__*/

	/*TODO tofloat*/

	/**add**/
	var1 = oadd(S, OInteger(1), OInteger(2));
	CU_ASSERT_EQUAL(OAny_toInt(var1), 3);



}
/*
 *__BEHAVIOR__.__leftshift__ = __leftshift__;
	__BEHAVIOR__.__rightshift__ = __rightshift__;
	__BEHAVIOR__.__mod__ = __mod__;
	__BEHAVIOR__.__bitand__ = __and__;
	__BEHAVIOR__.__bitor__ = __or__;
	__BEHAVIOR__.__bitxor__ = __xor__;
	__BEHAVIOR__.__tofloat__ = __tofloat__;
	__BEHAVIOR__.__add__ = __add__;
	__BEHAVIOR__.__subtract__ = __subtract__;
	__BEHAVIOR__.__divide__ = __divide__;
	__BEHAVIOR__.__multiply__ = __multiply__;

*/
