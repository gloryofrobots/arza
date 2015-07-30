/*
OAny OArray(OState* S, OAny size);
OAny OArray_push(OState* S, OAny self, OAny value);
OAny OArray_indexOf(OState* S, OAny self, OAny item);
OAny OArray_lastIndexOf(OState* S, OAny self, OAny item);
OAny OArray_pop(OState* S, OAny self);
OAny OArray_clear(OState* S, OAny self);
OAny OArray_remove(OState* S, OAny self, OAny item);
OAny OArray_insert(OState* S, OAny self, OAny item, OAny position);
OAny OArray_insertCollection(OState* S, OAny self, OAny collection, OAny position);
OAny OArray_concat(OState* S, OAny self, OAny collection);
OAny OArray_join(OState* S, OAny self, OAny collection);
OAny OArray_reverse(OState* S, OAny self);
OAny OArray_fill(OState* S, OAny self, OAny item, OAny start, OAny end);
*/

static void Test_Array(void) {
	OState * S = obin_init(1024 * 1024 * 90);

	OAny a1, a2, a3, a4;
	OAny i1, i2, i3, i4, i5, i6, i7, i8;
	OAny var1, var2;
	i1 = OString(S, "XXX");
	i2 = OInteger(42);
	i3 = OInteger(-42);
	i4 = OCharacter('A');
	i5 = OTuple(S, 2, i1, i2);
	i6 = OFloat(3455.23344);

	a1 = OArray_pack(S, 6, i1, i2, i3, i4, i5, i6);
	a2 = OArray(S, ObinNil);
	OArray_push(S, a2, i1); OArray_push(S, a2, i2); OArray_push(S, a2, i3);
	OArray_push(S, a2, i4); OArray_push(S, a2, i5); OArray_push(S, a2, i6);

	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i1)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i3)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i4)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i5)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a2, i6)));
	CU_ASSERT_TRUE(OAny_isFalse(ohasitem(S, a2, ObinTrue)));

	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i1)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i2)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i3)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i4)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i5)));
	CU_ASSERT_TRUE(OAny_isTrue(ohasitem(S, a1, i6)));
	CU_ASSERT_TRUE(OAny_isFalse(ohasitem(S, a1, ObinFalse)));

	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, a1, a2)));
	a3 = oclone(S, a1);
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, a1, a3)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, a2, a3)));

	a4 = OArray_pack(S, 2, ObinTrue, ObinFalse);
	osetitem(S, a2, OInteger(0), a4);

	omemory_collect(S);
}
