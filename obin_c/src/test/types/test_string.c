#define STR_ARR_SIZE 1024 * 4
/*
static void print_str(OState* S, OAny str) {
	static int c = 0;
	printf("\n%d. %s\n", ++c, OString_cstr(S, str));
}*/

static void Test_String(void) {
	OState * S = obin_init(1024 * 1024 * 90);
	ochar str_arr[STR_ARR_SIZE] = {'\0'};

	OAny str1, str2, str3, str4;
	OAny val1, val2;
	oint i;
	ostring cstr1;
	/*******************************/
	str1 = OString(S, "Hello!");
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), "Hello!");
	/********************C ARRAY CREATION***********/
	#define TEXT "Octopuses inhabit diverse regions of the ocean," \
	"including coral reefs, pelagic waters, and the ocean floor." \
	" They have numerous strategies for defending themselves against predators,"\
	" including the expulsion of ink, the use of camouflage and deimatic displays,"\
	" their ability to jet quickly through the water, and their ability to hide. " \
	" An octopus trails its eight arms behind it as it swims."\
	" All octopuses are venomous, but only one group, the blue-ringed octopus," \
	" is known to be deadly to humans."

	omemcpy(str_arr, TEXT, ostrlen(TEXT));

	str1 = OString_fromCArray(S, str_arr, STR_ARR_SIZE);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT);

	str1 = OString_fromCArray(S, str_arr, ostrlen(TEXT));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT);

	/********************C ARRAY CREATION 2***********/
	#undef TEXT
	#define TEXT "The giant Pacific octopus, Enteroctopus dofleini, is often cited as the largest known octopus species. Adults usually weigh around 15 kg (33 lb), with an arm span of up to 4.3 m (14 ft).[41] The largest specimen of this species to be scientifically documented was an animal with a live mass of 71 kg (156.5 lb).[42] The alternative contender is the seven-arm octopus, Haliphron atlanticus, based on a 61 kg (134 lb) carcass estimated to have a live mass of 75 kg (165 lb).[43][44] However, a number of questionable size records would suggest E. dofleini is the largest of all known octopus species by a considerable margin;[45] one such record is of a specimen weighing 272 kg (600 lb) and having an arm span of 9 m (30 ft).[46]"
	#define TEXT_UPPERCASE "THE GIANT PACIFIC OCTOPUS, ENTEROCTOPUS DOFLEINI, IS OFTEN CITED AS THE LARGEST KNOWN OCTOPUS SPECIES. ADULTS USUALLY WEIGH AROUND 15 KG (33 LB), WITH AN ARM SPAN OF UP TO 4.3 M (14 FT).[41] THE LARGEST SPECIMEN OF THIS SPECIES TO BE SCIENTIFICALLY DOCUMENTED WAS AN ANIMAL WITH A LIVE MASS OF 71 KG (156.5 LB).[42] THE ALTERNATIVE CONTENDER IS THE SEVEN-ARM OCTOPUS, HALIPHRON ATLANTICUS, BASED ON A 61 KG (134 LB) CARCASS ESTIMATED TO HAVE A LIVE MASS OF 75 KG (165 LB).[43][44] HOWEVER, A NUMBER OF QUESTIONABLE SIZE RECORDS WOULD SUGGEST E. DOFLEINI IS THE LARGEST OF ALL KNOWN OCTOPUS SPECIES BY A CONSIDERABLE MARGIN;[45] ONE SUCH RECORD IS OF A SPECIMEN WEIGHING 272 KG (600 LB) AND HAVING AN ARM SPAN OF 9 M (30 FT).[46]"
	#define TEXT_LOWERCASE "the giant pacific octopus, enteroctopus dofleini, is often cited as the largest known octopus species. adults usually weigh around 15 kg (33 lb), with an arm span of up to 4.3 m (14 ft).[41] the largest specimen of this species to be scientifically documented was an animal with a live mass of 71 kg (156.5 lb).[42] the alternative contender is the seven-arm octopus, haliphron atlanticus, based on a 61 kg (134 lb) carcass estimated to have a live mass of 75 kg (165 lb).[43][44] however, a number of questionable size records would suggest e. dofleini is the largest of all known octopus species by a considerable margin;[45] one such record is of a specimen weighing 272 kg (600 lb) and having an arm span of 9 m (30 ft).[46]"

	omemcpy(str_arr, TEXT, ostrlen(TEXT));

	str1 = OString_fromCArray(S, str_arr, STR_ARR_SIZE);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT);

	str1 = OString_fromCArray(S, str_arr, ostrlen(TEXT));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT);

	/****************LOWER AND UPPER**********************************************/
	/* check to upper */
	str2 = OString_toUpper(S, str1);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), TEXT_UPPERCASE);

	CU_ASSERT_FALSE(OAny_isTrue(OString_isUpper(S, str1)));
	CU_ASSERT_TRUE(OAny_isTrue(OString_isUpper(S, str2)));

	/* to lower both */
	str1 = OString_toLower(S, str1);
	str2 = OString_toLower(S, str2);

	CU_ASSERT_TRUE(OAny_isTrue(OString_isLower(S, str1)));
	CU_ASSERT_TRUE(OAny_isTrue(OString_isLower(S, str2)));

	CU_ASSERT_FALSE(OAny_isTrue(OString_isUpper(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isUpper(S, str2)));

	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), TEXT_LOWERCASE);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str1), TEXT_UPPERCASE);

	/* to upper both and check with source */
	str2 = OString_toUpper(S, str1);
	str1 = OString_toUpper(S, str2);

	CU_ASSERT_TRUE(OAny_isTrue(OString_isUpper(S, str1)));
	CU_ASSERT_TRUE(OAny_isTrue(OString_isUpper(S, str2)));

	CU_ASSERT_FALSE(OAny_isTrue(OString_isLower(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isLower(S, str2)));

	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), TEXT_UPPERCASE);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT_UPPERCASE);
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str1), TEXT_LOWERCASE);

	/****************CAPITALIZE****************/
	#undef TEXT

	#define TEXT "octopus is eaten in many cultures. 123 sd"
	#define TEXT_CAPITALIZE "Octopus is eaten in many cultures. 123 sd"
	#define TEXT_CAPITALIZE_WORDS "Octopus Is Eaten In Many Cultures. 123 Sd"

	str1 = OString(S, TEXT);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), TEXT);
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str1), TEXT_CAPITALIZE);
	str2 = OString_capitalize(S, str1);
	str3 = OString_capitalizeWords(S, str1);
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str1), OString_cstr(S, str2));
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str1), OString_cstr(S, str3));
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str2), OString_cstr(S, str3));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), TEXT_CAPITALIZE);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str3), TEXT_CAPITALIZE_WORDS);


	/********************************/
	#undef TEXT
	#define TEXT_ALPHA "octopus"
	#define TEXT_NOTALPHA "octopus ..."
	#define TEXT_ALPHANUM "octopus42"
	#define TEXT_NOTALPHANUM "octopus42..."
	#define TEXT_DIGIT "42"
	#define TEXT_NOTDIGIT "42o"
	#define TEXT_SPACE " \
				 	 	 	  	  	  	   	   	   " 	 
	#define TEXT_NOTSPACE " \
							 	 	 	 	 	  ."			

	str1 = OString(S, TEXT_ALPHA);
	str2 = OString(S, TEXT_NOTALPHA);
	CU_ASSERT_TRUE(OAny_isTrue(OString_isAlpha(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isAlpha(S, str2)));

	str1 = OString(S, TEXT_ALPHANUM);
	str2 = OString(S, TEXT_NOTALPHANUM);
	CU_ASSERT_TRUE(OAny_isTrue(OString_isAlphanum(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isAlphanum(S, str2)));

	str1 = OString(S, TEXT_DIGIT);
	str2 = OString(S, TEXT_NOTDIGIT);
	CU_ASSERT_TRUE(OAny_isTrue(OString_isDigit(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isDigit(S, str2)));

	str1 = OString(S, TEXT_SPACE);
	str2 = OString(S, TEXT_NOTSPACE);
	CU_ASSERT_TRUE(OAny_isTrue(OString_isSpace(S, str1)));
	CU_ASSERT_FALSE(OAny_isTrue(OString_isSpace(S, str2)));
	/************************INDEXOF************************************/
	#undef TEXT
	#define TEXT "The Squid are cephalopods 12 Squid are cephalopods"

	str1 = OString(S, TEXT);
	str2 = OString(S, "Squid");
	CU_ASSERT_EQUAL(OAny_intVal(OString_indexOf(S, str1, str2, ObinNil, ObinNil)), 4);
	CU_ASSERT_EQUAL(OAny_intVal(OString_indexOf(S, str1, str2, OInteger(6), ObinNil)), 29);
	CU_ASSERT_EQUAL(OAny_intVal(OString_indexOf(S, str1, str2, OInteger(6),
									OInteger(10))),-1);

	CU_ASSERT_EQUAL(OAny_intVal(OString_lastIndexOf(S, str1, str2, ObinNil, ObinNil)), 29);
	CU_ASSERT_EQUAL(OAny_intVal(OString_lastIndexOf(S, str1, str2, OInteger(0), OInteger(10))), 4);
	CU_ASSERT_EQUAL(OAny_intVal(OString_lastIndexOf(S, str1, str2, OInteger(6),
									OInteger(10))),-1);

	/******************DUPLICATE*******************************/
	#undef TEXT
	#define TEXT "squid"
	#define TEXT4 TEXT TEXT TEXT TEXT
	str1 = OString(S, TEXT);
	str2 = OString_dublicate(S, str1, OInteger(4));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), TEXT4);
	/*******************__add__***********************************/
	#undef TEXT
	#undef TEXT2
	#define TEXT "CLASS CEPHALOPODA: \n"
	#define TEXT2 "		-Subclass Nautiloidea: nautilus\n"
	#define TEXT3 "		-Subclass Coleoidea: squid, octopus, cuttlefish\n"
	#define TEXTALL TEXT TEXT2 TEXT3

	str1 = OString(S, TEXT);
	str2 = OString(S, TEXT2);
	str3 = OString(S, TEXT3);
	str4 = oadd(S, str1, str2);
	str4 = oadd(S, str4, str3);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str4), TEXTALL);
	/************tostring******************************/
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	str2 = otostring(S, str1);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	/****************tobool********************************************/
	str2 = OString(S, "");
	str3 = OString(S, "0");
	CU_ASSERT_FALSE(OAny_isTrue(otobool(S, str2)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, str1)));
	CU_ASSERT_TRUE(OAny_isTrue(otobool(S, str3)));

	/****************clone********************************************/
	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	str2 = oclone(S, str1);
	str3 = oclone(S, str2);
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, str3));
	/****************compare********************************************/
	#undef TEXT
	#undef TEXT2
	#undef TEXT3
	#define TEXT "AA"
	#define TEXT2 "B"
	#define TEXT3 "AAA"

	str1 = OString(S, TEXT);
	str2 = OString(S, TEXT2);
	str3 = OString(S, TEXT3);
	str4 = OString(S, TEXT);

	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str1, str2)), 1);
	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str2, str1)), -1);
	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str1, str3)), -1);
	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str3, str1)), 1);

	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str1, str4)), 0);
	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str4, str1)), 0);
	CU_ASSERT_EQUAL(OAny_intVal(ocompare(S, str4, str4)), 0);
	/****************hash******************************************/
	#undef TEXT
	#undef TEXT2
	#undef TEXT3
	#define TEXT "Aaa"
	#define TEXT2 "Bbb"

	str1 = OString(S, TEXT);
	str2 = OString(S, TEXT2);

	CU_ASSERT_STRING_NOT_EQUAL(OString_cstr(S, str2), OString_cstr(S, str1));
	val1 = ohash(S, str1);
	val2 = ohash(S, str2);
	CU_ASSERT_NOT_EQUAL(OAny_intVal(val1), OAny_intVal(val2));

	printf(" {HASH TEST: hash %s = %ld; hash %s = %ld; }",
			OString_cstr(S, str1), OAny_intVal(val1),
			OString_cstr(S, str2), OAny_intVal(val2));
	/***********************iterator ***********************************/
	#undef TEXT
	#undef TEXT2
	#undef TEXT3
	#define TEXT "The molluscs or mollusks[note 1] /ˈmɒləsks/ compose the large phylum of invertebrate animals known as the Mollusca."
	str1 = OString(S, TEXT);
	str3 = OString(S, "");
	cstr1 = TEXT;
	val1 = oiterator(S, str1);
	i = 0;

	while(OTRUE) {
		val2 = onext(S, val1);
		if(OBIN_IS_STOP_ITERATION(val2)) {
			break;
		}

		str2 = OString_fromCArray(S, &cstr1[i], 1);
		CU_ASSERT_STRING_EQUAL(OString_cstr(S, str2), OString_cstr(S, OCharacter_toString(S, val2)));
		CU_ASSERT_EQUAL((ochar)cstr1[i], (ochar)OAny_charVal(val2));
		str3 = oadd(S, str3, OCharacter_toString(S, val2));
		i++;
	}

	CU_ASSERT_STRING_EQUAL(OString_cstr(S, str1), OString_cstr(S, str3));
	/*******************length***********************************************/
	#undef TEXT
	#undef TEXT2
	#undef TEXT3
	#define TEXT "a"
	#define TEXT2 "Good evidence exists for the appearance of gastropods, cephalopods and bivalves in the Cambrian period 541 to 485.4 million years ago."
	#define TEXT3 ""
	str1 = OString(S, TEXT);
	str2 = OString(S, TEXT2);
	str3 = OString(S, TEXT3);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, str1)), 1);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, str2)), 134);
	CU_ASSERT_EQUAL(OAny_intVal(olength(S, str3)), 0);
	/*********************getitem************************************/
	val1 = ogetitem(S, str1, OInteger(0));
	CU_ASSERT_EQUAL(OAny_charVal(val1), 'a');

	val1 = ogetitem(S, str2, OInteger(100));
	CU_ASSERT_EQUAL(OAny_charVal(val1), 'o');

	omemory_collect(S);
	/*need to implement integer behavior to use has_item*/
	/*
	val1 = obin_hasitem(S, str1, obin_char_new('b'));
	CU_ASSERT_TRUE(obin_any_is_true(val1));
	*/

	/*******************FORMAT***********************************/
	/*
	#undef TEXT
	#undef TEXT2
	#define TEXT "%d %p %s %.2f"
	obin_memset(str_arr, 0, STR_ARR_SIZE);
	sprintf(str_arr, TEXT, 42, (void*)obin_any_cell(str1), "SQUID", 99.1799999999999);
	printf(str_arr);
	str2 = obin_string_new(S, TEXT);
	str3 = obin_string_format(S, str2, 42, (void*)obin_any_cell(str1), "SQUID", 99.1799999999999);
	*/
	/*#undef TEXT
	#undef TEXT2
	#define TEXT "SQUID"
	#define TEXT2 "OCTOPUS"

	str1 = obin_string_new(S, TEXT);
	str2 = obin_string_new(S, TEXT2);
	str3 = obin_string_pack(S, 2, str1, str2);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(S, str3), TEXT TEXT2);*/

	/*
	 *
ObinAny obin_string_format(ObinState* S, ObinAny format, ...);
ObinAny obin_string_join(ObinState* S, ObinAny self, ObinAny collection);
ObinAny obin_string_split(ObinState* S, ObinAny self, ObinAny separator);
ObinAny obin_string_pack(ObinState* S, obin_index count, ...);
	 *
	 * */
}
