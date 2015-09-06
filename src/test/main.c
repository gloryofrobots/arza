/*
 *  CUnit - A Unit testing framework library for C.
 *  Copyright (C) 2001  Anil Kumar
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Library General Public
 *  License as published by the Free Software Foundation; either
 *  version 2 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Library General Public License for more details.
 *
 *  You should have received a copy of the GNU Library General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "CUnit/Console.h"
#include "CUnit/Basic.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <obin.h>
#include "types/test_types.c"
#include "memory/test_memory.c"
#include "compile/test_compile.c"

static CU_SuiteInfo suites[] = {
  { "Suite_BaseTypes",  NULL, NULL,    TestGroup_BaseTypes },
  { "Suite_Memory",  NULL, NULL,    TestGroup_Memory },
  { "Suite_Compile",  NULL, NULL,    TestGroup_Compile },

  /*  { "suite_success_both",  suite_base_init, suite_base_clean,    tests_base_types },
  { "suite_success_init",  suite_base_init, NULL,                tests_base_types },
  { "suite_success_clean", NULL,               suite_base_clean, tests_base_types },*/
	CU_SUITE_INFO_NULL,
};

void AddTests(void)
{
  assert(NULL != CU_get_registry());
  assert(!CU_is_test_running());

	/* Register suites. */
	if (CU_register_suites(suites) != CUE_SUCCESS) {
		fprintf(stderr, "suite registration failed - %s\n",
			CU_get_error_msg());
		exit(EXIT_FAILURE);
	}
}

void print_example_results(void)
{
  fprintf(stdout, "\n\nExpected Test Results:"
                  "\n\n  Error Handling  Type      # Run   # Pass   # Fail"
                  "\n\n  ignore errors   suites%9u%9u%9u"
                    "\n                  tests %9u%9u%9u"
                    "\n                  asserts%8u%9u%9u"
                  "\n\n  stop on error   suites%9u%9u%9u"
                    "\n                  tests %9u%9u%9u"
                    "\n                  asserts%8u%9u%9u\n\n",
                  14, 14, 3,
                  31, 10, 21,
                  89, 47, 42,
                  4, 4, 1,
                  12, 9, 3,
                  12, 9, 3);
}
int main(int argc, char* argv[])
{
  CU_BOOL Run = CU_FALSE ;
  CU_BasicRunMode mode = CU_BRM_VERBOSE;

  setvbuf(stdout, NULL, _IONBF, 0);

  if (argc > 1) {
    if (!strcmp("-i", argv[1])) {
      Run = CU_TRUE ;
      CU_set_error_action(CUEA_IGNORE);
    }
    else if (!strcmp("-f", argv[1])) {
      Run = CU_TRUE ;
      CU_set_error_action(CUEA_FAIL);
    }
    else if (!strcmp("-A", argv[1])) {
      Run = CU_TRUE ;
      CU_set_error_action(CUEA_ABORT);
    }
    else if (!strcmp("-h", argv[1])) {
      Run = CU_TRUE ;
      CU_set_error_action(CUEA_ABORT);
    }
    else {
      printf("\nUsage:  ConsoleTest [option]\n\n"
               "Options:   -i   Run, ignoring framework errors [default].\n"
               "           -f   Run, failing on framework error.\n"
               "           -A   run, aborting on framework error.\n"
               "           -h   Print this message.\n\n");
    }
  }
  else {
    Run = CU_TRUE;
    CU_set_error_action(CUEA_IGNORE);
  }

  if (CU_TRUE == Run) {
    if (CU_initialize_registry()) {
      printf("\nInitialization of Test Registry failed.");
    }
    else {
      AddTests();
      CU_basic_set_mode(mode);
      printf("\nTests completed with return value %d.\n", CU_basic_run_tests());
/*      CU_console_run_tests();*/
      CU_cleanup_registry();
    }
  }

  return 0;
}
