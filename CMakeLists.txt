cmake_minimum_required(VERSION 3.10)

project(CPPConverter)

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

# Set the output directory for the executable for different configurations
set_target_properties(${PROJECT_NAME} PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_SOURCE_DIR}
    RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_SOURCE_DIR}
)

# Include the CANlib headers
include_directories(${CANLIB_INCLUDE_DIR})

# Check the platform and link against the appropriate CANlib library
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    # 64-bit system
    target_link_directories(${PROJECT_NAME} PRIVATE ${CANLIB_LIB_DIR_X64})
    target_link_libraries(${PROJECT_NAME} PRIVATE canlib32.lib kvmlib.lib kvlclib.lib)
else()
    # 32-bit system
    target_link_directories(${PROJECT_NAME} PRIVATE ${CANLIB_LIB_DIR_X86})
    target_link_libraries(${PROJECT_NAME} PRIVATE canlib32.lib kvmlib.lib kvlclib.lib)
endif()

include(FetchContent)

# Fetch YAML-CPP
FetchContent_Declare(
  yaml-cpp
  GIT_REPOSITORY https://github.com/jbeder/yaml-cpp.git
  GIT_TAG master # Can be a tag (yaml-cpp-x.x.x), a commit hash, or a branch name (master)
)
FetchContent_GetProperties(yaml-cpp)

if(NOT yaml-cpp_POPULATED)
  message(STATUS "Fetching yaml-cpp...")
  FetchContent_Populate(yaml-cpp)
  add_subdirectory(${yaml-cpp_SOURCE_DIR} ${yaml-cpp_BINARY_DIR})
endif()

target_link_libraries(${PROJECT_NAME} PUBLIC yaml-cpp)

# Fetch INDICATORS
FetchContent_Declare(
  indicators
  GIT_REPOSITORY https://github.com/p-ranav/indicators.git
  GIT_TAG master # Can be a tag (yaml-cpp-x.x.x), a commit hash, or a branch name (master)
)
FetchContent_GetProperties(indicators)

if(NOT indicators_POPULATED)
  message(STATUS "Fetching indicators...")
  FetchContent_Populate(indicators)
  add_subdirectory(${indicators_SOURCE_DIR} ${indicators_BINARY_DIR})
endif()

target_link_libraries(${PROJECT_NAME} PUBLIC indicators)
