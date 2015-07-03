
find_package(CUnit)

SET(SRC
   main.c
   )
	

add_executable(obin-tests ${SRC})

target_link_libraries(
		obin-tests
		${CUNIT_LIBRARY}
		)