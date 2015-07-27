static void Test_Float(void) {
	OState * S = obin_init(1024 * 1024 * 1);
	OAny intmax, intmin, int1, int0, intneg1;
	OAny var1, var2;

	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(1.0)), 1.0);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(-1.0)), -1.0);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(-1.23232323232)), -1.23232323232);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(1.23232323232)), 1.23232323232);

	/*__tostring__ */
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(42.001))), "42.001");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(-1232316642.0233123301))), "-1232316642.0233123301");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(1))), "1.00");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(0))), "0.00");

	/*__tobool__ */
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, OFloat(42))));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, OFloat(-42))));
	CU_ASSERT_FALSE(OAny_isTrue(otobool(S, OFloat(0))));
	CU_ASSERT_TRUE(OAny_isFalse(otobool(S, OFloat(0))));



	/**TODO hash**/

	/**__tointeger__**/
	CU_ASSERT_EQUAL(OAny_toInteger(otointeger(S, OFloat(42.00042))), 42);
	CU_ASSERT_EQUAL(OAny_toInteger(otointeger(S, OFloat(-42.00042))), -42);
	CU_ASSERT_EQUAL(OAny_toInteger(otointeger(S, OFloat(0.9912020))), 0);

	/**__tonegative__**/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(1.0))), -1.0);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(-1.0))), 1.0);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(-990909999.909222))), 990909999.909222);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(0))), 0);

	/**__compare__**/
	var1 = ocompare(S, intmax, intmin);
	CU_ASSERT_EQUAL(OAny_toFloat(var1), 1);
	var1 = ocompare(S, intmin, intmax);
	CU_ASSERT_EQUAL(OAny_toFloat(var1), -1);
	var1 = ocompare(S, intmin, intmin);
	CU_ASSERT_EQUAL(OAny_toFloat(var1), 0);
	var1 = ocompare(S, intmax, intmax);
	CU_ASSERT_EQUAL(OAny_toFloat(var1), 0);
	var1 = ocompare(S, int0, int0);
	CU_ASSERT_EQUAL(OAny_toFloat(var1), 0);

	/*__mod__*/
	CU_ASSERT_EQUAL(OAny_toFloat(omod(S, OFloat(23), OFloat(2))), 1);
	CU_ASSERT_EQUAL(OAny_toFloat(omod(S, OFloat(4665), OFloat(65))), 50);
	CU_ASSERT_EQUAL(OAny_toFloat(omod(S, OFloat(-90), OFloat(4))), -2);
	CU_ASSERT_EQUAL(OAny_toFloat(omod(S, OFloat(-90), OFloat(-4))), -2);

	/**add**/
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(10), OFloat(3))), 13);
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(42), OFloat(35))), 77);
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(-42), OFloat(35))), -7);
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(35), OFloat(-42))), -7);
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(134), OFloat(12))), 146);
	CU_ASSERT_EQUAL(OAny_toFloat(oadd(S, OFloat(OINT_MIN), OFloat(1))), OINT_MIN + 1);
	/*__subtract__*/
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(10), OFloat(3))), 7);
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(42), OFloat(35))), 7);
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(-42), OFloat(35))), -77);
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(35), OFloat(-42))), 77);
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(134), OFloat(12))), 122);
	CU_ASSERT_EQUAL(OAny_toFloat(osubtract(S, OFloat(OINT_MAX), OFloat(1))), OINT_MAX - 1);
	/*__multiply__*/
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(10), OFloat(3))), 30);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(42), OFloat(35))), 1470);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(-42), OFloat(35))), -1470);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(35), OFloat(-42))), -1470);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(134), OFloat(12))), 1608);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(OINT_MAX), OFloat(1))), OINT_MAX);
	CU_ASSERT_EQUAL(OAny_toFloat(omultiply(S, OFloat(OINT_MAX), OFloat(0))), 0);
	/*__divide__*/
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(10), OFloat(3))), 3);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(42), OFloat(35))), 1);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(-42), OFloat(35))), -1);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(35), OFloat(-42))), 0);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(134), OFloat(12))), 11);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(OINT_MAX), OFloat(1))), OINT_MAX);
	CU_ASSERT_EQUAL(OAny_toFloat(odivide(S, OFloat(OINT_MAX), OFloat(OINT_MIN))), 0);
	/*TODO CHECK DIVISION BY ZERO*/
}
/*
 *TODO BELOW
	__BEHAVIOR__.__tofloat__ = __tofloat__;
*/
