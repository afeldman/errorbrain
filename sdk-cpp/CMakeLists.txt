cmake_minimum_required(VERSION 3.22)
project(errorbrain-sdk
    VERSION 0.1.0
    DESCRIPTION "ErrorBrain SDK for C++ - AI-powered debugging memory"
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Dependencies
find_package(nlohmann_json 3.2.0 REQUIRED)
find_package(curl REQUIRED)
find_package(OpenSSL REQUIRED)
find_package(ZLIB REQUIRED)
find_package(Boost 1.70 REQUIRED)

# Main library
add_library(errorbrain
    src/client.cpp
    src/models.cpp
    src/error.cpp
)

target_include_directories(errorbrain
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_link_libraries(errorbrain
    PUBLIC
        nlohmann_json::nlohmann_json
        CURL::libcurl
        OpenSSL::SSL
        OpenSSL::Crypto
        ZLIB::ZLIB
        Boost::boost
)

# Examples
if(${CMAKE_PROJECT_NAME}_with_examples OR CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    message(STATUS "Building examples...")
    add_executable(example_basic examples/basic.cpp)
    target_link_libraries(example_basic PRIVATE errorbrain)
    
    add_executable(example_exception examples/exception.cpp)
    target_link_libraries(example_exception PRIVATE errorbrain)
    
    add_executable(example_metadata examples/metadata.cpp)
    target_link_libraries(example_metadata PRIVATE errorbrain)
endif()

# Tests
if(${CMAKE_PROJECT_NAME}_with_tests AND CMAKE_SOURCE_DIR STREQUAL PROJECT_SOURCE_DIR)
    message(STATUS "Building tests...")
    enable_testing()
    
    find_package(GTest REQUIRED)
    
    add_executable(errorbrain_tests
        tests/test_client.cpp
        tests/test_models.cpp
    )
    
    target_link_libraries(errorbrain_tests
        PRIVATE
            errorbrain
            GTest::gtest
            GTest::gtest_main
    )
    
    gtest_discover_tests(errorbrain_tests)
endif()

# Installation
install(TARGETS errorbrain
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)
