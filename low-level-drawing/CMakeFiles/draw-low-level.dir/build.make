# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/parano/Desktop/docgen/low-level-drawing

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/parano/Desktop/docgen/low-level-drawing

# Include any dependencies generated for this target.
include CMakeFiles/draw-low-level.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/draw-low-level.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/draw-low-level.dir/flags.make

CMakeFiles/draw-low-level.dir/draw.c.o: CMakeFiles/draw-low-level.dir/flags.make
CMakeFiles/draw-low-level.dir/draw.c.o: draw.c
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/parano/Desktop/docgen/low-level-drawing/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/draw-low-level.dir/draw.c.o"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -o CMakeFiles/draw-low-level.dir/draw.c.o   -c /home/parano/Desktop/docgen/low-level-drawing/draw.c

CMakeFiles/draw-low-level.dir/draw.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/draw-low-level.dir/draw.c.i"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /home/parano/Desktop/docgen/low-level-drawing/draw.c > CMakeFiles/draw-low-level.dir/draw.c.i

CMakeFiles/draw-low-level.dir/draw.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/draw-low-level.dir/draw.c.s"
	/usr/bin/cc $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /home/parano/Desktop/docgen/low-level-drawing/draw.c -o CMakeFiles/draw-low-level.dir/draw.c.s

# Object files for target draw-low-level
draw__low__level_OBJECTS = \
"CMakeFiles/draw-low-level.dir/draw.c.o"

# External object files for target draw-low-level
draw__low__level_EXTERNAL_OBJECTS =

draw-low-level: CMakeFiles/draw-low-level.dir/draw.c.o
draw-low-level: CMakeFiles/draw-low-level.dir/build.make
draw-low-level: CMakeFiles/draw-low-level.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/parano/Desktop/docgen/low-level-drawing/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable draw-low-level"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/draw-low-level.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/draw-low-level.dir/build: draw-low-level

.PHONY : CMakeFiles/draw-low-level.dir/build

CMakeFiles/draw-low-level.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/draw-low-level.dir/cmake_clean.cmake
.PHONY : CMakeFiles/draw-low-level.dir/clean

CMakeFiles/draw-low-level.dir/depend:
	cd /home/parano/Desktop/docgen/low-level-drawing && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/parano/Desktop/docgen/low-level-drawing /home/parano/Desktop/docgen/low-level-drawing /home/parano/Desktop/docgen/low-level-drawing /home/parano/Desktop/docgen/low-level-drawing /home/parano/Desktop/docgen/low-level-drawing/CMakeFiles/draw-low-level.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/draw-low-level.dir/depend

