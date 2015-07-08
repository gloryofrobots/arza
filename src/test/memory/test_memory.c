#include "test_memory_groups.c"
#include "test_memory_tree.c"

static CU_TestInfo TestGroup_Memory[] = {
  { "Test_MemoryGroups", Test_MemoryGroups },
  { "Test_MemoryTree", Test_MemoryTree },
	CU_TEST_INFO_NULL,
};
