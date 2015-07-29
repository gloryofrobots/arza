#include "test_base_types.c"
#include "test_string.c"
#include "test_integer.c"
#include "test_float.c"
#include "test_character.c"
#include "test_tuple.c"

static CU_TestInfo TestGroup_BaseTypes[] = {
  { "Test_BaseTypes", Test_BaseTypes },
  { "Test_BaseAnyNew", Test_BaseAnyNew },
  {"Test_Character", Test_Character},
  {"Test_String", Test_String},
  {"Test_Integer", Test_Integer},
  {"Test_Float", Test_Float},
  {"Test_Tuple", Test_Tuple},
	CU_TEST_INFO_NULL,
};
