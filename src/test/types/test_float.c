#define GRANULARITY 0.000001

static void Test_Float(void) {
	OState * S = obin_init(1024 * 1024 * 1);

	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(1.0)), 1.0, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(-1.0)), -1.0, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(-1.23232323232)), -1.23232323232, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(OFloat(1.23232323232)), 1.23232323232, GRANULARITY);

	/*__tostring__ */
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(42.001))), "42.001");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(-1232316642.0233123301))), "-1.23232e+09");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(1.0001))), "1.0001");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, otostring(S, OFloat(0))), "0");

	/*__tobool__ */
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, OFloat(42))));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, OFloat(-42))));
	CU_ASSERT_FALSE(OAny_isTrue(otobool(S, OFloat(0))));
	CU_ASSERT_TRUE(OAny_isFalse(otobool(S, OFloat(0))));

	/**__tointeger__**/
	CU_ASSERT_EQUAL(OAny_toInt(otointeger(S, OFloat(42.00042))), 42);
	CU_ASSERT_EQUAL(OAny_toInt(otointeger(S, OFloat(-42.00042))), -42);
	CU_ASSERT_EQUAL(OAny_toInt(otointeger(S, OFloat(0.9912020))), 0);

	/**__tonegative__**/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(1.0))), -1.0, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(-1.0))), 1.0, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(-990909999.909222))), 990909999.909222, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(otonegative(S, OFloat(0))), 0, GRANULARITY);

	/**__compare__**/
	CU_ASSERT_EQUAL(OAny_toInt(ocompare(S, OFloat(0), OFloat(0))), 0);
	CU_ASSERT_EQUAL(OAny_toInt(ocompare(S, OFloat(1), OFloat(0))), 1);
	CU_ASSERT_EQUAL(OAny_toInt(ocompare(S, OFloat(1.2999999), OFloat(1.3))), -1);
	CU_ASSERT_EQUAL(OAny_toInt(ocompare(S, OFloat(-1.2999999), OFloat(-1.3))), 1);

	/*__mod__*/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omod(S, OFloat(24.5), OFloat(4))), 0.5, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omod(S, OFloat(24.5), OFloat(4.2))), 3.49999999, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omod(S, OFloat(-90), OFloat(4))), -2, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omod(S, OFloat(-90.54), OFloat(5.2))), -2.14, GRANULARITY);

	/**add**/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(oadd(S, OFloat(24.5), OFloat(4.2122212))), 28.7122212, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(oadd(S, OFloat(24.5), OFloat(4.7))), 29.2, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(oadd(S, OFloat(-90), OFloat(4.001))), -85.998999999999995, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(oadd(S, OFloat(-90.54), OFloat(-5.2))), -95.74, GRANULARITY);
	/*__subtract__*/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(osubtract(S, OFloat(24.5), OFloat(4.2122212))), 20.287778799999998, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(osubtract(S, OFloat(24.5), OFloat(4.7))), 19.8, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(osubtract(S, OFloat(-90), OFloat(4.001))), -94.001, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(osubtract(S, OFloat(-90.54), OFloat(-5.2))), -85.34, GRANULARITY);
	/*__multiply__*/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(234.560000), OFloat(3434.455400))),  805585.858624, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(1.560000), OFloat(0.045540))),  0.071042, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(-99.000000), OFloat(43.090909))),  -4265.999991, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(-10000234.121300), OFloat(-8.000000))),  80001872.9704, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(42.000000), OFloat(0.000000))),  0.000000, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(omultiply(S, OFloat(1.000000), OFloat(42.100000))),  42.100000, GRANULARITY);
	/*__divide__*/
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(234.560000), OFloat(3434.455400))),  0.068296, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(1.560000), OFloat(0.045540))),  34.255599, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(-99.000000), OFloat(43.090909))),  -2.297468, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(-10000234.121300), OFloat(-8.000000))),  1250029.2651625001, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(42.000000), OFloat(1.000000))),  42.000000, GRANULARITY);
	CU_ASSERT_DOUBLE_EQUAL(OAny_toFloat(odivide(S, OFloat(1.000000), OFloat(42.100000))),  0.023753, GRANULARITY);
	/*TODO CHECK DIVISION BY ZERO*/
}
