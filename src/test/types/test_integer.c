static void Test_Integer(void) {
	printf("{OINT_MAX="OBIN_INTEGER_FORMATTER" OINT_MIN="OBIN_INTEGER_FORMATTER"} ", OINT_MAX, OINT_MIN);
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
	var1 = otostring(S, OInteger(2147483647));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "2147483647");
	var1 = otostring(S, OInteger(-2147483647));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, var1), "-2147483647");

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
	/*__leftshift__*/
	CU_ASSERT_EQUAL(OAny_toInt(oleftshift(S, int1, int0)), 1);
	CU_ASSERT_EQUAL(OAny_toInt(oleftshift(S, int0, int1)), 0);
	CU_ASSERT_EQUAL(OAny_toInt(oleftshift(S, OInteger(214), OInteger(12))), 876544);
	CU_ASSERT_EQUAL(OAny_toInt(oleftshift(S, OInteger(-8888), OInteger(7))), -1137664);
	/*__rightshift__*/
	CU_ASSERT_EQUAL(OAny_toInt(orightshift(S, int1, int0)), 1);
	CU_ASSERT_EQUAL(OAny_toInt(orightshift(S, int0, int1)), 0);
	CU_ASSERT_EQUAL(OAny_toInt(orightshift(S, OInteger(23), OInteger(2))), 5);
	CU_ASSERT_EQUAL(OAny_toInt(orightshift(S, OInteger(-1233), OInteger(3))), -155);

	/*__mod__*/
	CU_ASSERT_EQUAL(OAny_toInt(omod(S, OInteger(23), OInteger(2))), 1);
	CU_ASSERT_EQUAL(OAny_toInt(omod(S, OInteger(4665), OInteger(65))), 50);
	CU_ASSERT_EQUAL(OAny_toInt(omod(S, OInteger(-90), OInteger(4))), -2);
	CU_ASSERT_EQUAL(OAny_toInt(omod(S, OInteger(-90), OInteger(-4))), -2);

	/*__bitand__*/
	CU_ASSERT_EQUAL(OAny_toInt(obitand(S, OInteger(10), OInteger(2))), 2);
	CU_ASSERT_EQUAL(OAny_toInt(obitand(S, OInteger(42), OInteger(35))), 34);
	CU_ASSERT_EQUAL(OAny_toInt(obitand(S, OInteger(-42), OInteger(35))), 2);
	CU_ASSERT_EQUAL(OAny_toInt(obitand(S, OInteger(134), OInteger(12))), 4);

	/*__bitor__*/
	CU_ASSERT_EQUAL(OAny_toInt(obitor(S, OInteger(10), OInteger(3))), 11);
	CU_ASSERT_EQUAL(OAny_toInt(obitor(S, OInteger(42), OInteger(35))), 43);
	CU_ASSERT_EQUAL(OAny_toInt(obitor(S, OInteger(-42), OInteger(35))), -9);
	CU_ASSERT_EQUAL(OAny_toInt(obitor(S, OInteger(134), OInteger(12))), 142);
	/*__bitxor__*/
	CU_ASSERT_EQUAL(OAny_toInt(obitxor(S, OInteger(10), OInteger(3))), 9);
	CU_ASSERT_EQUAL(OAny_toInt(obitxor(S, OInteger(42), OInteger(35))), 9);
	CU_ASSERT_EQUAL(OAny_toInt(obitxor(S, OInteger(-42), OInteger(35))), -11);
	CU_ASSERT_EQUAL(OAny_toInt(obitxor(S, OInteger(134), OInteger(12))), 138);

	/**add**/
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(10), OInteger(3))), 13);
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(42), OInteger(35))), 77);
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(-42), OInteger(35))), -7);
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(35), OInteger(-42))), -7);
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(134), OInteger(12))), 146);
	CU_ASSERT_EQUAL(OAny_toInt(oadd(S, OInteger(OINT_MIN), OInteger(1))), OINT_MIN + 1);
	/*__subtract__*/
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(10), OInteger(3))), 7);
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(42), OInteger(35))), 7);
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(-42), OInteger(35))), -77);
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(35), OInteger(-42))), 77);
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(134), OInteger(12))), 122);
	CU_ASSERT_EQUAL(OAny_toInt(osubtract(S, OInteger(OINT_MAX), OInteger(1))), OINT_MAX - 1);
	/*__multiply__*/
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(10), OInteger(3))), 30);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(42), OInteger(35))), 1470);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(-42), OInteger(35))), -1470);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(35), OInteger(-42))), -1470);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(134), OInteger(12))), 1608);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(OINT_MAX), OInteger(1))), OINT_MAX);
	CU_ASSERT_EQUAL(OAny_toInt(omultiply(S, OInteger(OINT_MAX), OInteger(0))), 0);
	/*__divide__*/
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(10), OInteger(3))), 3);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(42), OInteger(35))), 1);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(-42), OInteger(35))), -1);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(35), OInteger(-42))), 0);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(134), OInteger(12))), 11);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(OINT_MAX), OInteger(1))), OINT_MAX);
	CU_ASSERT_EQUAL(OAny_toInt(odivide(S, OInteger(OINT_MAX), OInteger(OINT_MIN))), 0);
	/*TODO CHECK DIVISION BY ZERO*/
}
/*
 *TODO BELOW
	__BEHAVIOR__.__tofloat__ = __tofloat__;
*/
