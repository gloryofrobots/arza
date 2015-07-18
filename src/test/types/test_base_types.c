
static void Test_BaseTypes(void) {
	ObinState * state = obin_init(1024 * 1024 * 90);
	CU_ASSERT_EQUAL(obin_any_type(ObinFalse), EOBIN_TYPE_FALSE);
	CU_ASSERT_EQUAL(obin_any_type(ObinNil), EOBIN_TYPE_NIL);
	CU_ASSERT_EQUAL(obin_any_type(ObinNothing), EOBIN_TYPE_NOTHING);
	CU_ASSERT_EQUAL(obin_any_type(ObinTrue), EOBIN_TYPE_TRUE);
	CU_ASSERT_EQUAL(obin_any_integer(obin_integers(state)->Lesser), -1);
	CU_ASSERT_EQUAL(obin_any_integer(obin_integers(state)->Greater), 1);
	CU_ASSERT_EQUAL(obin_any_integer(obin_integers(state)->Equal), 0);
}
static void Test_BaseAnyNew(void) {
	ObinAny any = obin_any_new();
	CU_ASSERT_EQUAL(obin_any_type(any), EOBIN_TYPE_UNKNOWN);
}

static CU_TestInfo TestGroup_BaseTypes[] = {
  { "Test_BaseTypes", Test_BaseTypes },
  { "Test_BaseAnyNew", Test_BaseAnyNew },
	CU_TEST_INFO_NULL,
};
