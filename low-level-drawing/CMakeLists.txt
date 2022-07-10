cmake_minimum_required(VERSION 3.10)

# set the project name
project(draw-low-level)

find_library(CAIRO_LIB asfcairo)
if(NOT CAIRO_LIB)
    message("Cairo Not Found")
else()
    message("Cairo Found")
endif()

# add the executable
add_executable(draw-low-level draw.c)
add_library()

target_link_libraries(draw-low-level )