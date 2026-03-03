# 指定CMake编译最低要求版本
cmake_minimum_required(VERSION 2.8...3.5)

project(reg_test)
set(CMAKE_C_FLAGS "-Wall -g -O0")

# hps测试
add_executable(reg_hps_test ${CMAKE_CURRENT_SOURCE_DIR}/reg_hps_test.c
							${CMAKE_CURRENT_SOURCE_DIR}/reg_shm.c
							${CMAKE_CURRENT_SOURCE_DIR}/reg_packet.c
							${CMAKE_CURRENT_SOURCE_DIR}/log.c)
target_include_directories(reg_hps_test PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(reg_hps_test pthread)

# mcu测试
add_executable(reg_mcu_test ${CMAKE_CURRENT_SOURCE_DIR}/reg_mcu_test.c
							${CMAKE_CURRENT_SOURCE_DIR}/reg_shm.c
							${CMAKE_CURRENT_SOURCE_DIR}/reg_packet.c
							${CMAKE_CURRENT_SOURCE_DIR}/log.c)
target_include_directories(reg_mcu_test PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(reg_mcu_test pthread)