

static void Test_Vector(void) {
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

	a1 = OVector_pack(S, 6, i1, i2, i3, i4, i5, i6);
	a2 = OVector(S, ObinNil);
	OVector_push(S, a2, i1); OVector_push(S, a2, i2); OVector_push(S, a2, i3);
	OVector_push(S, a2, i4); OVector_push(S, a2, i5); OVector_push(S, a2, i6);

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

	a4 = OVector_pack(S, 2, ObinTrue, ObinFalse);
	osetitem(S, a2, OInteger(0), a4);
	OVector_push(S, a4, i1);
	/*************************************************/
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a4)), 3);
	CU_ASSERT_EQUAL(OAny_intVal(OVector_indexOf(S, a4, ObinTrue)), 0);
	CU_ASSERT_EQUAL(OAny_intVal(OVector_indexOf(S, a4, i1)), 2);
	OVector_push(S, a4, i2);
	OVector_push(S, a4, i1);
	OVector_push(S, a4, i2);
	OVector_push(S, a4, i1);
	/*************************************************/
	CU_ASSERT_EQUAL(OAny_intVal(OVector_indexOf(S, a4, i2)), 3);
	CU_ASSERT_EQUAL(OAny_intVal(OVector_lastIndexOf(S, a4, i2)), 5);
	/*************************************************/
    var1 = OVector_pop(S, a4);
	CU_ASSERT_TRUE(OAny_isTrue(ois(S, var1, i1)));
	OVector_pop(S, a4); OVector_pop(S, a4); OVector_pop(S, a4);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a4)), 3);
	OVector_pop(S, a4); OVector_pop(S, a4); OVector_pop(S, a4);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a4)), 0);
	/*************************************************/
	OVector_clear(S, a3);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a3)), 0);
	/*************************************************/
	OVector_remove(S, a1, i1);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a1)), 5);
	/*************************************************/
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(2)), i3)));
	OVector_insert(S, a2, i1, OInteger(2));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(2)), i1)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(3)), i3)));
	/*************************************************/
	a1 = OVector_pack(S, 3, i1, i2, i3);
	a3 = OVector_concat(S, a2, a1);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a3)), 10);
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a3, OInteger(7)), i1)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a3, OInteger(8)), i2)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a3, OInteger(9)), i3)));
	/*************************************************/
	a2 = OVector_pack(S, 2, ObinFalse, ObinTrue);
	a3 = OVector_join(S, a2, a1);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a3)), 7);

	a1 = OVector_pack(S, 1, i1);
	a2 = OVector_pack(S, 2, i2);
	a3 = OVector_join(S, a2, a1);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, a3)), 1);
	/*************************************************/
	a1 = OVector_pack(S, 6, i1, i2, i3, i4, i5, i6);
	OVector_fill(S, a1, i1, OInteger(0), OInteger(6));
	/*************************************************/
	a1 = OVector_pack(S, 6, i1, i2, i3, i4, i5, i6);
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(0)), i1)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(1)), i2)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(2)), i3)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(3)), i4)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(4)), i5)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a1, OInteger(5)), i6)));
	a2 = OVector_reverse(S, a1);
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(5)), i1)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(4)), i2)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(3)), i3)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(2)), i4)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(1)), i5)));
	CU_ASSERT_TRUE(OAny_isTrue(oequal(S, ogetitem(S, a2, OInteger(0)), i6)));
	/********* ****************************************/
	omemory_collect(S);
}
