enable_language(CXX)

#############################################
# enable LP parsers
#############################################
add_library(wrapper_lp SHARED
        mps_lp.h mps_lp.c
)

target_link_libraries(
        wrapper_lp PUBLIC cupdlp
)

if (${BUILD_HIP} STREQUAL "ON")
    message(NOTICE "- HIP version PDLP")
    target_compile_definitions(wrapper_lp
            PUBLIC
            -DCUPDLP_USE_HIP=1
            -D__HIP_PLATFORM_AMD__=1
    )
elseif (${CUDA_LIBRARY-NOTFOUND})
    message(NOTICE "- CPU version PDLP")
    target_compile_definitions(wrapper_lp
            PUBLIC
            -DCUPDLP_CPU=1
    )
endif()

#############################################
# enable HiGHS input targets
#############################################

message(NOTICE "--------------------- cuPDLP  HiGHS  CONFIG -----------------------")
include(../FindHiGHSConf.cmake)

add_library(wrapper_highs SHARED
        mps_lp.h mps_lp.c
        wrapper_highs.cpp ${HiGHS_HEADER_FILES}
        wrapper_highs.h)

target_include_directories(
        wrapper_highs PUBLIC
        ${HiGHS_INCLUDE_DIR}
)

target_link_libraries(
        wrapper_highs PUBLIC cupdlp
        ${HiGHS_LIBRARY}
)

if (${BUILD_HIP} STREQUAL "ON")
    message(NOTICE "- HIP version PDLP")
    target_compile_definitions(wrapper_highs
            PUBLIC
            -DCUPDLP_USE_HIP=1
            -D__HIP_PLATFORM_AMD__=1
    )
elseif (${CUDA_LIBRARY-NOTFOUND})
    message(NOTICE "- CPU version PDLP")
    target_compile_definitions(wrapper_highs
            PUBLIC
            -DCUPDLP_CPU=1
    )
endif()

#############################################
# cuPDLP-C binary using HiGHS as parsers
#############################################
add_executable(plc
        ${HiGHS_HEADER_FILES}
        mps_highs.c
)

target_include_directories(
        plc PRIVATE
        ${HiGHS_INCLUDE_DIR}
)

target_link_libraries(
        plc PUBLIC
        wrapper_highs
        ${HiGHS_LIBRARY}
)

if (${BUILD_HIP} STREQUAL "ON")
    target_compile_definitions(plc
            PRIVATE
            -DCUPDLP_USE_HIP=1
            -D__HIP_PLATFORM_AMD__=1
    )

    target_include_directories(plc PRIVATE
            /opt/rocm/include
    )

    target_link_libraries(plc
            PRIVATE
            cupdlp
            hiplin
            hip::host
            roc::hipblas
            roc::hipsparse
            m
    )
elseif (${CUDA_LIBRARY-NOTFOUND})
    target_link_libraries(plc PRIVATE cupdlp m)
else ()
    target_link_libraries(plc PRIVATE cupdlp ${CUDA_LIBRARY} m)
endif ()

if (${BUILD_HIP} STREQUAL "ON")
    add_custom_target(
            deploy
            COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plchip"
            DEPENDS plc plc
    )
elseif (${CUDA_LIBRARY-NOTFOUND})
    add_custom_target(
            deploy
            COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plccpu"
            DEPENDS plc plc
    )
else()
    add_custom_target(
            deploy
            COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plcgpu"
            DEPENDS plc plc
    )
endif()
