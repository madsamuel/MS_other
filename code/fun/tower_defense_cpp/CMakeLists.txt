cmake_minimum_required(VERSION 3.10)
project(TowerDefense)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find SFML package
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)

# Add source files
set(SOURCES
    Game.cpp
    Main.cpp
)

# Create executable
add_executable(TowerDefense ${SOURCES})

# Link SFML
target_link_libraries(TowerDefense sfml-graphics sfml-window sfml-system)

# Set output directory
set_target_properties(TowerDefense PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
