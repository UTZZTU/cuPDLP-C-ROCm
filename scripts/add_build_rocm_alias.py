from pathlib import Path

path = Path("CMakeLists.txt")

if not path.exists():
    raise SystemExit("CMakeLists.txt not found")

s = path.read_text()
old = s

# 1. Add BUILD_ROCM option after BUILD_CUDA if missing.
if 'option(BUILD_ROCM "<BUILD_ROCM_OR_NOT>" OFF)' not in s:
    s = s.replace(
        'option(BUILD_CUDA "<BUILD_CUDA_OR_NOT>" OFF)\n'
        'option(BUILD_HIP "<BUILD_HIP_OR_NOT>" OFF)\n',
        'option(BUILD_CUDA "<BUILD_CUDA_OR_NOT>" OFF)\n'
        'option(BUILD_ROCM "<BUILD_ROCM_OR_NOT>" OFF)\n'
        'option(BUILD_HIP "<BUILD_HIP_OR_NOT_LEGACY_ALIAS>" OFF)\n'
    )

# 2. Replace CUDA/HIP conflict block with CUDA/ROCm plus legacy BUILD_HIP alias.
old_block = '''if (${BUILD_CUDA} STREQUAL "ON" AND ${BUILD_HIP} STREQUAL "ON")
    message(FATAL_ERROR "BUILD_CUDA and BUILD_HIP cannot both be ON")
endif ()

message(NOTICE "-- Sets build with CUDA ${BUILD_CUDA}")
message(NOTICE "-- Sets build with HIP ${BUILD_HIP}")

if (${BUILD_CUDA} STREQUAL "ON")
    include(FindCUDAConf.cmake)
elseif (${BUILD_HIP} STREQUAL "ON")
    enable_language(HIP)'''

new_block = '''# BUILD_HIP is kept as a legacy compatibility alias.
# New ROCm builds should prefer BUILD_ROCM=ON.
if (BUILD_HIP AND NOT BUILD_ROCM)
    message(WARNING "BUILD_HIP is a legacy alias. Prefer BUILD_ROCM=ON for ROCm builds.")
    set(BUILD_ROCM ON CACHE BOOL "Enable ROCm/HIP backend" FORCE)
endif ()

if (BUILD_ROCM)
    set(BUILD_HIP ON CACHE BOOL "Enable HIP backend implementation for ROCm" FORCE)
endif ()

if (BUILD_CUDA AND BUILD_ROCM)
    message(FATAL_ERROR "BUILD_CUDA and BUILD_ROCM cannot both be ON")
endif ()

message(NOTICE "-- Sets build with CUDA ${BUILD_CUDA}")
message(NOTICE "-- Sets build with ROCm ${BUILD_ROCM}")
message(NOTICE "-- Sets build with HIP backend ${BUILD_HIP}")

if (BUILD_CUDA)
    include(FindCUDAConf.cmake)
elseif (BUILD_ROCM)
    enable_language(HIP)'''

if old_block not in s:
    raise SystemExit(
        "Expected CMake block not found. Please inspect CMakeLists.txt around BUILD_CUDA / BUILD_HIP."
    )

s = s.replace(old_block, new_block)

if s == old:
    print("No changes made.")
else:
    path.write_text(s)
    print("updated: CMakeLists.txt")
