cmake_minimum_required(VERSION 2.6)
project(obin)


SET(OBIN_EXE_NAME obin)
SET(OBIN_LIB_NAME libobin)

SET(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/../CMakeModules)
set(CMAKE_C_FLAGS "-std=c89") 
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -Wall")

SET(OBIN_LIB_SRC
   core/_memory.c
   )
   
SET(OBIN_EXE_SRC
   main.c
   )

include_directories(
	${INCLUDE_DIRECTORIES}
	"./"
)

add_subdirectory(test)	

add_library(${OBIN_LIB_NAME} ${OBIN_LIB_SRC})
SET_TARGET_PROPERTIES(${OBIN_LIB_NAME} PROPERTIES PREFIX "")


add_executable(${OBIN_EXE_NAME} ${OBIN_EXE_SRC})
target_link_libraries(${OBIN_EXE_NAME} ${OBIN_LIB_NAME})