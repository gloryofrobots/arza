
static void Test_BaseTypes(void) {
	OState * S = obin_init(1024 * 1024 * 90);
	printf("\n *************************** Internal sizes ******************************** \n");
	printf("Size of ObinState %d \n", sizeof(OState));
	printf("Size of ObinAny %d \n", sizeof(OAny));
	printf("Size of ObinValue %d \n", sizeof(OValue));
	printf("Size of ObinCell %d \n", sizeof(OCell));

	CU_ASSERT_EQUAL(OAny_type(ObinFalse), EOBIN_TYPE_FALSE);
	CU_ASSERT_EQUAL(OAny_type(ObinNil), EOBIN_TYPE_NIL);
	CU_ASSERT_EQUAL(OAny_type(ObinNothing), EOBIN_TYPE_NOTHING);
	CU_ASSERT_EQUAL(OAny_type(ObinTrue), EOBIN_TYPE_TRUE);
	CU_ASSERT_EQUAL(OAny_toInt(ointegers(S)->Lesser), -1);
	CU_ASSERT_EQUAL(OAny_toInt(ointegers(S)->Greater), 1);
	CU_ASSERT_EQUAL(OAny_toInt(ointegers(S)->Equal), 0);
}
static void Test_BaseAnyNew(void) {
	OAny any = OAny_new();
	CU_ASSERT_EQUAL(OAny_type(any), EOBIN_TYPE_UNKNOWN);
}

