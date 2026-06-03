add_library(hiplin SHARED
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_kernels.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_linalg.cpp
)

set_source_files_properties(
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_kernels.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_linalg.cpp
    PROPERTIES LANGUAGE HIP
)

target_include_directories(hiplin PUBLIC
    ${CUPDLP_INCLUDE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${HIP_INCLUDE_DIRS}
)

target_compile_definitions(hiplin PUBLIC
    CUPDLP_USE_HIP=1
    __HIP_PLATFORM_AMD__=1
)

target_link_libraries(hiplin
    PRIVATE
    hip::device
    roc::hipblas
    roc::hipsparse
    m
)
