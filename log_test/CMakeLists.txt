# 指定CMake编译最低要求版本
cmake_minimum_required(VERSION 2.8...3.5)

project(log_test)

# 编译条件设置,让程序按照cmake设置编译条件编译
# 这部分配置放置在项目根目录CMakeLists.txt下全局生效，否则引用log.h文件中的预编译无法获取loglevel
# 而log.c文件中的logcolor_en因为已编译成库不受影响
# case 0
option(loglevel "set the log level(0-fatal, 1-error, 2-warn, 3-info, 4-debug, 5-trace, default 3)" 3)
if(loglevel)
	message(STATUS "Config: loglevel=${loglevel}")
	add_definitions("-Dloglevel=${loglevel}")
endif()

# case 1
option(logcolor_en "Enable the log color to use: on/off" off)
if(logcolor_en STREQUAL "off")
	message(STATUS "Config: logcolor_en=off")
	add_definitions("-Dlogcolor_en=0")
else()
	message(STATUS "Config: logcolor_en=on")
	add_definitions("-Dlogcolor_en=1")
endif()

# 设置LIBLOG_SRC变量
file(GLOB LIBLOG_SRC "${CMAKE_CURRENT_SOURCE_DIR}/log.c") 

# 取变量LIBLOG_SRC值，指定生成动态库liblog.so
add_library(log SHARED ${LIBLOG_SRC})
target_link_libraries(log pthread)

# 为动态库liblog.so指定头文件目录为当前目录CMAKE_CURRENT_SOURCE_DIR
target_include_directories(log PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# 设置log动态库版本VERSION=${${PROJECT_NAME}_VERSION}
# 设置api版本SOVERSION=${${PROJECT_NAME}_SOVERSION
# set_target_properties(log PROPERTIES VERSION ${${PROJECT_NAME}_1.0} SOVERSION ${${PROJECT_NAME}_1.0})

# 将头文件安装到CMAKE_INSTALL_INCLUDEDIR目录下log
# 将库安装到CMAKE_INSTALL_LIBDIR目录下log
# install(FILES log.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(TARGETS log LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/log)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/log.h DESTINATION ${CMAKE_INSTALL_PREFIX}/include/log)

# 测试
add_executable(log_test ${CMAKE_CURRENT_SOURCE_DIR}/log_test.c
						${CMAKE_CURRENT_SOURCE_DIR}/log.c)
target_link_libraries(log_test pthread)