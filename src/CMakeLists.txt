cmake_minimum_required(VERSION 2.6)
project(obin)

set(CMAKE_C_FLAGS "-std=c89") 
set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} -Wall")

SET(SRC
   main.c
   )


add_executable(obin ${SRC})