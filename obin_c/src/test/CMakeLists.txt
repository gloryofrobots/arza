find_package(CUnit)

SET(SRC
   main.c
   )

include_directories(
	${INCLUDE_DIRECTORIES}
	${CURRENT_SOURCE_DIR}/include
)
add_executable(obin-tests ${SRC})

target_link_libraries(
		obin-tests
		${OBIN_LIBRARY}
		${CUNIT_LIBRARY}
		)