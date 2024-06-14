cmake_minimum_required(VERSION 3.10)

project(MyCanlibProject)

# Set the C++ standard to C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set the paths to the CANlib headers and libraries
set(CANLIB_INCLUDE_DIR "C:/Program Files (x86)/Kvaser/Canlib/INC")
set(CANLIB_LIB_DIR_X86 "C:/Program Files (x86)/Kvaser/Canlib/Lib/MS")
set(CANLIB_LIB_DIR_X64 "C:/Program Files (x86)/Kvaser/Canlib/Lib/x64")

# Add include directory for indicators
include_directories(include)

# Set the source files
set(SOURCES src/main.cpp)

# Create an executable from the source files
add_executable(${PROJECT_NAME} ${SOURCES})

# Include the CANlib headers
include_directories(${CANLIB_INCLUDE_DIR})

# Check the platform and link against the appropriate CANlib library
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    # 64-bit system
    target_link_directories(${PROJECT_NAME} PRIVATE ${CANLIB_LIB_DIR_X64})
    target_link_libraries(${PROJECT_NAME} canlib32.lib kvmlib.lib kvlclib.lib)
else()
    # 32-bit system
    target_link_directories(${PROJECT_NAME} PRIVATE ${CANLIB_LIB_DIR_X86})
    target_link_libraries(${PROJECT_NAME} canlib32.lib kvmlib.lib kvlclib.lib)
endif()
