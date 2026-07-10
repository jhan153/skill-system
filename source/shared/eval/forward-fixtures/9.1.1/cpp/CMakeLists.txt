cmake_minimum_required(VERSION 3.20)
project(skill_system_cpp_fixture LANGUAGES CXX)
add_executable(skill-system-cpp src/main.cpp)
target_include_directories(skill-system-cpp PRIVATE include)
