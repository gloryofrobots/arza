#include "test_base_types.c"
#include "test_string.c"

static CU_TestInfo TestGroup_BaseTypes[] = {
  { "Test_BaseTypes", Test_BaseTypes },
  { "Test_BaseAnyNew", Test_BaseAnyNew },
  {"Test_String", Test_String},
	CU_TEST_INFO_NULL,
};
