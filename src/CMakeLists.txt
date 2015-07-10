cmake_minimum_required(VERSION 2.6)
project(obin)


SET(OBIN_EXECUTABLE obin)
SET(OBIN_LIBRARY libobin)

SET(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/CMakeModules)
set(CMAKE_C_FLAGS "-std=c89") 
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -Wall")

FILE(GLOB_RECURSE HEADERS "include/*.h")

SET(OBIN_LIB_SRC
  ${HEADERS}
   core/_memory.c
   core/_builtin.c
   core/_log.c
   core/_error.c
   core/_random.c
   core/types/_collection.c
   core/types/_tuple.c
   core/types/_string.c
   core/types/_integer.c
   core/types/_float.c
   core/types/_bool.c
   core/types/_fstream.c
   )
   
SET(OBIN_EXE_SRC
   main.c
   )

include_directories(
	${INCLUDE_DIRECTORIES}
	${CMAKE_SOURCE_DIR}/include
)

add_subdirectory(test)	

add_library(${OBIN_LIBRARY} ${OBIN_LIB_SRC})
SET_TARGET_PROPERTIES(${OBIN_LIBRARY} PROPERTIES PREFIX "")


add_executable(${OBIN_EXECUTABLE} ${OBIN_EXE_SRC})
target_link_libraries(${OBIN_EXECUTABLE} ${OBIN_LIBRARY})
