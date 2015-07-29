
/*
OAny OTuple_fromArray(OState* S,  OAny size, OAny* items);
OAny OTuple(OState* S, oindex_t size, ...);
__BEHAVIOR__.__name__ = __TypeName__;

	__BEHAVIOR__.__mark__ = __mark__;

	__BEHAVIOR__.__tostring__ = __tostring__;
	__BEHAVIOR__.__tobool__ = __tobool__;
	__BEHAVIOR__.__clone__ = __clone__;
	__BEHAVIOR__.__compare__ = OCollection_compare;
	__BEHAVIOR__.__hash__ = __hash__;

	__BEHAVIOR__.__iterator__ = __iterator__;
	__BEHAVIOR__.__length__ = __length__;
	__BEHAVIOR__.__getitem__ = __getitem__;
	__BEHAVIOR__.__hasitem__ = __hasitem__;
*/
static void Test_Tuple(void) {
	OState * S = obin_init(1024 * 1024 * 90);
	OAny t1, t2;
	OAny i1, i2, i3, i4, i5;
	OAny var1, var2;
	i1 = OString(S, "XXX");
	i2 = OInteger(42);
	i3 = OFloat(3.14);
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

}
