#include "test_base_types.c"
#include "test_string.c"
#include "test_integer.c"

static CU_TestInfo TestGroup_BaseTypes[] = {
  { "Test_BaseTypes", Test_BaseTypes },
  { "Test_BaseAnyNew", Test_BaseAnyNew },
  {"Test_Char", Test_Char},
  /*{"Test_String", Test_String},*/
  {"Test_Integer", Test_Integer},
	CU_TEST_INFO_NULL,
};
