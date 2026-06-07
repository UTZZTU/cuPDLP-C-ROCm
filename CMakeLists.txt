cmake_minimum_required(VERSION 3.24)

project(CUPDLP VERSION 0.0.1)

option(BUILD_CUDA "<BUILD_CUDA_OR_NOT>" OFF)
option(BUILD_ROCM "<BUILD_ROCM_OR_NOT>" OFF)
option(BUILD_HIP "<LEGACY_ALIAS_FOR_BUILD_ROCM>" OFF)
option(BUILD_APPS "<BUILD_APPS_OR_NOT>" OFF)
option(BUILD_PYTHON "<BUILD_PYTHON_OR_NOT>" OFF)

message(NOTICE "-----------------------      cuPDLP-C      ------------------------")

enable_language(C CXX)
include(CTest)

set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED True)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

string(REPLACE "-O3" "-O2" CMAKE_C_FLAGS_RELEASE "${CMAKE_C_FLAGS_RELEASE}")
string(REPLACE "-O3" "-O2" CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
string(REPLACE "-O3" "-O2" CMAKE_CUDA_FLAGS_RELEASE "${CMAKE_CUDA_FLAGS_RELEASE}")

set(CMAKE_C_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")
set(CMAKE_CUDA_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE}")

message("reset release flags: ${CMAKE_C_FLAGS_RELEASE}")

message(NOTICE "--------------------- cuPDLP CPU/GPU CONFIG -----------------------")

list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR})

# Internal selector for the legacy CUDA backend.
# CPU and ROCm/HIP builds keep this OFF.
set(CUPDLP_USE_LEGACY_CUDA OFF)

# BUILD_HIP is kept as a legacy compatibility alias.
# New ROCm builds should prefer BUILD_ROCM=ON.
if (BUILD_HIP AND NOT BUILD_ROCM)
    message(WARNING "BUILD_HIP is a legacy alias. Prefer BUILD_ROCM=ON for ROCm builds.")
    set(BUILD_ROCM ON CACHE BOOL "Enable ROCm/HIP backend" FORCE)
endif ()

if (BUILD_ROCM)
    set(BUILD_HIP ON CACHE BOOL "Enable ROCm/HIP backend implementation" FORCE)
endif ()

if (BUILD_CUDA AND BUILD_ROCM)
    message(FATAL_ERROR "BUILD_CUDA and BUILD_ROCM cannot both be ON")
endif ()

message(NOTICE "-- Sets build with CUDA ${BUILD_CUDA}")
message(NOTICE "-- Sets build with ROCm ${BUILD_ROCM}")
message(NOTICE "-- Sets build with ROCm/HIP backend ${BUILD_HIP}")

if (BUILD_CUDA)
    add_compile_definitions(CUPDLP_USE_CUDA=1)
endif()

if (BUILD_ROCM)
    add_compile_definitions(CUPDLP_USE_ROCM=1)
endif()

if (BUILD_CUDA)
    include(FindCUDAConf.cmake)
    set(CUPDLP_USE_LEGACY_CUDA ON)
elseif (BUILD_ROCM)
    enable_language(HIP)

    list(APPEND CMAKE_PREFIX_PATH /opt/rocm)

    find_package(hip REQUIRED CONFIG)
    find_package(hipblas REQUIRED CONFIG)
    find_package(hipsparse REQUIRED CONFIG)

    set(CMAKE_HIP_ARCHITECTURES gfx1150 CACHE STRING "AMD GPU architecture")
else ()
endif ()

add_subdirectory(cupdlp)
add_subdirectory(interface)
add_subdirectory(third-party)

message(NOTICE "-- Sets build applications ${BUILD_APPS}")
if (${BUILD_APPS} STREQUAL "ON")
    add_subdirectory(apps)
endif ()

message(NOTICE "-- Sets build PYTHON ${BUILD_PYTHON}")
if (${BUILD_PYTHON} STREQUAL "ON")
    add_subdirectory("pycupdlp")
else ()
endif ()

if (BUILD_TESTING)
    add_test(
            NAME rocm_port_hygiene
            COMMAND ${CMAKE_COMMAND} -E env
                    bash "${PROJECT_SOURCE_DIR}/scripts/check_rocm_port_hygiene.sh"
            WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )

    if (${BUILD_ROCM} STREQUAL "ON")
        add_test(
                NAME rocm_smoke_validation
                COMMAND ${CMAKE_COMMAND} -E env
                        CPU_BUILD_DIR=build-ctest-cpu
                        ROCM_BUILD_DIR=build-ctest-rocm
                        RESULT_ROOT=validation/results/ctest
                        ROCM_ARCH=${CMAKE_HIP_ARCHITECTURES}
                        bash "${PROJECT_SOURCE_DIR}/scripts/run_validation.sh"
                WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
        )
    endif ()
endif ()
