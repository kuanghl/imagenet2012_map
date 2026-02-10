cmake_minimum_required(VERSION 3.0.0 FATAL_ERROR)

project(driver VERSION 0.1.0 LANGUAGES C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Find kernel headers
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
find_package(KernelHeaders REQUIRED)
include_directories(${KERNELHEADERS_INCLUDE_DIRS})
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Build the kernel module
# message(STATUS "Make: ${CMAKE_MAKE_PROGRAM}")
set(DRIVER_FILE hello.ko)
set(KBUILD_CMD $(MAKE) -C ${KERNELHEADERS_DIR} modules M=${CMAKE_CURRENT_BINARY_DIR} src=${CMAKE_CURRENT_SOURCE_DIR})

# Generate the Kbuild file through cmake.
FILE(WRITE ${CMAKE_CURRENT_SOURCE_DIR}/Kbuild "obj-m := hello.o\n")
FILE(APPEND ${CMAKE_CURRENT_SOURCE_DIR}/Kbuild "hello-y := greet.o\n")

add_custom_command(OUTPUT ${DRIVER_FILE}
        COMMAND ${KBUILD_CMD}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS hello.c greet.c greet.h VERBATIM)

add_custom_target(driver ALL DEPENDS ${DRIVER_FILE})

