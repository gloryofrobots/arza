#define STR_ARR_SIZE 1024 * 4

static void print_str(ObinState* state, ObinAny str) {
	static int c = 0;
	printf("\n%d. %s\n", ++c, obin_string_cstr(state, str));
}

static void Test_Char(void) {
	ObinState * state = obin_init(1024 * 1024 * 90);
	char str_arr[STR_ARR_SIZE] = {'\0'};
	ObinAny str1, str2;
	/*******************************/
	str1 = obin_char_new('T');
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), "T");
}

static void Test_String(void) {
	ObinState * state = obin_init(1024 * 1024 * 90);
	char str_arr[STR_ARR_SIZE] = {'\0'};
	ObinAny str1, str2, str3;
	/*******************************/
	str1 = obin_string_new(state, "Hello!");
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), "Hello!");
	/********************C ARRAY CREATION***********/
	#define TEXT "Octopuses inhabit diverse regions of the ocean," \
	"including coral reefs, pelagic waters, and the ocean floor." \
	" They have numerous strategies for defending themselves against predators,"\
	" including the expulsion of ink, the use of camouflage and deimatic displays,"\
	" their ability to jet quickly through the water, and their ability to hide. " \
	" An octopus trails its eight arms behind it as it swims."\
	" All octopuses are venomous, but only one group, the blue-ringed octopus," \
	" is known to be deadly to humans."

	obin_memcpy(str_arr, TEXT, obin_strlen(TEXT));

	str1 = obin_string_from_carray(state, str_arr, STR_ARR_SIZE);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT);

	str1 = obin_string_from_carray(state, str_arr, obin_strlen(TEXT));
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT);

	/********************C ARRAY CREATION 2***********/
	#undef TEXT
	#define TEXT "The giant Pacific octopus, Enteroctopus dofleini, is often cited as the largest known octopus species. Adults usually weigh around 15 kg (33 lb), with an arm span of up to 4.3 m (14 ft).[41] The largest specimen of this species to be scientifically documented was an animal with a live mass of 71 kg (156.5 lb).[42] The alternative contender is the seven-arm octopus, Haliphron atlanticus, based on a 61 kg (134 lb) carcass estimated to have a live mass of 75 kg (165 lb).[43][44] However, a number of questionable size records would suggest E. dofleini is the largest of all known octopus species by a considerable margin;[45] one such record is of a specimen weighing 272 kg (600 lb) and having an arm span of 9 m (30 ft).[46]"
	#define TEXT_UPPERCASE "THE GIANT PACIFIC OCTOPUS, ENTEROCTOPUS DOFLEINI, IS OFTEN CITED AS THE LARGEST KNOWN OCTOPUS SPECIES. ADULTS USUALLY WEIGH AROUND 15 KG (33 LB), WITH AN ARM SPAN OF UP TO 4.3 M (14 FT).[41] THE LARGEST SPECIMEN OF THIS SPECIES TO BE SCIENTIFICALLY DOCUMENTED WAS AN ANIMAL WITH A LIVE MASS OF 71 KG (156.5 LB).[42] THE ALTERNATIVE CONTENDER IS THE SEVEN-ARM OCTOPUS, HALIPHRON ATLANTICUS, BASED ON A 61 KG (134 LB) CARCASS ESTIMATED TO HAVE A LIVE MASS OF 75 KG (165 LB).[43][44] HOWEVER, A NUMBER OF QUESTIONABLE SIZE RECORDS WOULD SUGGEST E. DOFLEINI IS THE LARGEST OF ALL KNOWN OCTOPUS SPECIES BY A CONSIDERABLE MARGIN;[45] ONE SUCH RECORD IS OF A SPECIMEN WEIGHING 272 KG (600 LB) AND HAVING AN ARM SPAN OF 9 M (30 FT).[46]"
	#define TEXT_LOWERCASE "the giant pacific octopus, enteroctopus dofleini, is often cited as the largest known octopus species. adults usually weigh around 15 kg (33 lb), with an arm span of up to 4.3 m (14 ft).[41] the largest specimen of this species to be scientifically documented was an animal with a live mass of 71 kg (156.5 lb).[42] the alternative contender is the seven-arm octopus, haliphron atlanticus, based on a 61 kg (134 lb) carcass estimated to have a live mass of 75 kg (165 lb).[43][44] however, a number of questionable size records would suggest e. dofleini is the largest of all known octopus species by a considerable margin;[45] one such record is of a specimen weighing 272 kg (600 lb) and having an arm span of 9 m (30 ft).[46]"

	obin_memcpy(str_arr, TEXT, obin_strlen(TEXT));

	str1 = obin_string_from_carray(state, str_arr, STR_ARR_SIZE);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT);

	str1 = obin_string_from_carray(state, str_arr, obin_strlen(TEXT));
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT);

	/****************LOWER AND UPPER**********************************************/
	/* check to upper */
	str2 = obin_string_to_uppercase(state, str1);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), TEXT_UPPERCASE);

	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_upper(state, str1)));
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_upper(state, str2)));

	/* to lower both */
	str1 = obin_string_to_lowercase(state, str1);
	str2 = obin_string_to_lowercase(state, str2);

	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_lower(state, str1)));
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_lower(state, str2)));

	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_upper(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_upper(state, str2)));

	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), TEXT_LOWERCASE);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), obin_string_cstr(state, str1));
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str1), TEXT_UPPERCASE);

	/* to upper both and check with source */
	str2 = obin_string_to_uppercase(state, str1);
	str1 = obin_string_to_uppercase(state, str2);

	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_upper(state, str1)));
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_upper(state, str2)));

	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_lower(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_lower(state, str2)));

	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), obin_string_cstr(state, str1));
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), TEXT_UPPERCASE);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT_UPPERCASE);
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str1), TEXT_LOWERCASE);

	/****************CAPITALIZE****************/
	#undef TEXT

	#define TEXT "octopus is eaten in many cultures. 123 sd"
	#define TEXT_CAPITALIZE "Octopus is eaten in many cultures. 123 sd"
	#define TEXT_CAPITALIZE_WORDS "Octopus Is Eaten In Many Cultures. 123 Sd"

	str1 = obin_string_new(state, TEXT);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str1), TEXT);
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str1), TEXT_CAPITALIZE);
	str2 = obin_string_capitalize(state, str1);
	str3 = obin_string_capitalize_words(state, str1);
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str1), obin_string_cstr(state, str2));
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str1), obin_string_cstr(state, str3));
	CU_ASSERT_STRING_NOT_EQUAL(obin_string_cstr(state, str2), obin_string_cstr(state, str3));
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str2), TEXT_CAPITALIZE);
	CU_ASSERT_STRING_EQUAL(obin_string_cstr(state, str3), TEXT_CAPITALIZE_WORDS);


	/********************************/
	#undef TEXT
	#define TEXT_ALPHA "octopus"
	#define TEXT_NOTALPHA "octopus ..."
	#define TEXT_ALPHANUM "octopus1488"
	#define TEXT_NOTALPHANUM "octopus1488..."
	#define TEXT_DIGIT "42"
	#define TEXT_NOTDIGIT "42o"
	#define TEXT_SPACE " \
				 	 	 	  	  	  	   	   	   " 	 
	#define TEXT_NOTSPACE " \
							 	 	 	 	 	  ."			

	str1 = obin_string_new(state, TEXT_ALPHA);
	str2 = obin_string_new(state, TEXT_NOTALPHA);
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_alpha(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_alpha(state, str2)));

	str1 = obin_string_new(state, TEXT_ALPHANUM);
	str2 = obin_string_new(state, TEXT_NOTALPHANUM);
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_alphanum(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_alphanum(state, str2)));

	str1 = obin_string_new(state, TEXT_DIGIT);
	str2 = obin_string_new(state, TEXT_NOTDIGIT);
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_digit(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_digit(state, str2)));

	str1 = obin_string_new(state, TEXT_SPACE);
	str2 = obin_string_new(state, TEXT_NOTSPACE);
	CU_ASSERT_TRUE(obin_any_is_true(obin_string_is_space(state, str1)));
	CU_ASSERT_FALSE(obin_any_is_true(obin_string_is_space(state, str2)));
	/*
	 *
 Return the lowest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.

ObinAny obin_string_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);

 Return the highest index in the string
 where substring sub is found, such that sub is contained
 within s[start:end]. Optional arguments start and end
 are interpreted as in slice notation. Return -1 on failure.

ObinAny obin_string_last_index_of(ObinState* state, ObinAny self, ObinAny other,
		ObinAny start, ObinAny end);

ObinAny obin_string_dublicate(ObinState* state, ObinAny self, ObinAny _count);
ObinAny obin_string_format(ObinState* state, ObinAny format, ...);
ObinAny obin_string_concat(ObinState* state, ObinAny str1, ObinAny str2);
ObinAny obin_string_join(ObinState* state, ObinAny self, ObinAny collection);
ObinAny obin_string_split(ObinState* state, ObinAny self, ObinAny separator);

obin_string obin_string_cstr(ObinState* state, ObinAny self);

ObinAny obin_string_pack(ObinState* state, obin_index count, ...);
	 *
	 * */
}
