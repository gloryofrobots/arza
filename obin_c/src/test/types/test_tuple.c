/*
 *TODO TEST
	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
*/

static void Test_Tuple(void) {
	OState * S = obin_init(1024 * 1024 * 90);
	OAny t1, t2, t3;
	OAny i1, i2, i3, i4, i5;
	OAny var1, var2;
	i1 = OString(S, "XXX");
	i2 = OInteger(42);
	i3 = OInteger(-42);
	i4 = OCharacter('A');
	i5 = OTuple(S, 2, i1, i2);

	t1 = OTuple(S, 5, i1, i2, i3, i4, i5);
	t2 = OTuple(S, 4, i2, i3, i4, i5);

	var1 = ogetitem(S, t1, OInteger(1));
	var2 = ogetitem(S, t2, OInteger(0));

	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, var1, var2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t1, i1)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t1, i2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t1, i3)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t1, i4)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t1, i5)));

	t3 = oclone(S, t1);
	var1 = ogetitem(S, t3, OInteger(1));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, var1, var2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t3, i1)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t3, i2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t3, i3)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t3, i4)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, t3, i5)));

	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, t3, t1)));
	CU_ASSERT_TRUE(OAny_isFalse(oequal(S, t3, t2)));

	t3 = OTuple(S, 5, i1, i2, i3, i5, i5);
	CU_ASSERT_TRUE(OAny_isTrue(ois(S, ocompare(S, t1, t3), ointegers(S)->Lesser)));
	CU_ASSERT_TRUE(OAny_isTrue(ois(S, ocompare(S, t3, t1), ointegers(S)->Greater)));
	CU_ASSERT_TRUE(OAny_isFalse(oequal(S, t3, t1)));
	CU_ASSERT_NOT_EQUAL(OAny_intVal(ohash(S, t3)), OAny_intVal(ohash(S, t1)));
	t3 = oclone(S, t1);
	CU_ASSERT_EQUAL(OAny_intVal(ohash(S, t3)), OAny_intVal(ohash(S, t1)));
	CU_ASSERT_EQUAL(OAny_intVal(ohash(S, t1)), OAny_intVal(ohash(S, t1)));

	t1 = OTuple(S, 0);
	t2 = oclone(S, t1);

	CU_ASSERT_EQUAL(OAny_intVal(ohash(S, t1)), OAny_intVal(ohash(S, t1)));
	CU_ASSERT_TRUE(OAny_isFalse(otobool(S, t1)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, t1, t2)));
	CU_ASSERT_TRUE(OAny_isFalse(ohasitem(S, t1, ObinNil)));
	CU_ASSERT_TRUE(OAny_isFalse(ohasitem(S, t2, ObinNil)));
	CU_ASSERT_TRUE(OAny_isTrue(ois(S, ocompare(S, t1, t2), ointegers(S)->Equal)));
	CU_ASSERT_TRUE(OAny_isTrue(ois(S, ocompare(S, t1, t3), ointegers(S)->Lesser)));

	omemory_collect(S);
}
