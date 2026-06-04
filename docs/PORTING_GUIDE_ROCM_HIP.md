# Porting cuPDLP-C from CUDA to ROCm/HIP

This document describes how this repository was ported from the original CUDA-based cuPDLP-C project to a ROCm/HIP build targeting AMD Radeon 890M / gfx1150.

The guide has two purposes:

1. Record the exact migration path used for this repository.
2. Provide a reusable CUDA-to-HIP migration checklist for similar GPU solver projects.

## 1. Project background

The original cuPDLP-C project contains a CUDA backend for GPU-accelerated linear programming. The goal of this port is to make the GPU backend run on AMD hardware through ROCm/HIP.

The current validated target is:

* GPU: AMD Radeon 890M
* GPU architecture: `gfx1150`
* OS: Ubuntu 24.04.4
* ROCm: 7.2.1
* HIP compiler: ROCm Clang 22.0.0
* HiGHS: 1.6.0
* Example validated: `example/afiro.mps`

This port currently represents a first working ROCm/HIP milestone. It builds successfully and runs `afiro.mps` with `terminationCode = OPTIMAL`.

## 2. Migration strategy

The migration was performed in stages instead of doing a single global replacement.

The main idea was:

1. Keep the original CUDA project as a reference.
2. Create a separate ROCm/HIP working copy.
3. Verify the ROCm environment and GPU architecture.
4. Build and run the CPU baseline first.
5. Convert only the CUDA backend source files with `hipify-clang`.
6. Manually adapt project-level CMake and host-side code.
7. Build the HIP backend as a standalone library first.
8. Link the HIP backend into the full `plc` executable.
9. Validate with a small MPS example.
10. Clean up misleading CUDA names and document the port.

This staged workflow made the migration easier to debug because each step had a clear success condition.

## 3. Hardware and ROCm verification

Before porting any code, verify that ROCm can see the target device.

Useful commands include:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm-smi
/opt/rocm/bin/hipcc --version
```

For this project, ROCm reported:

```text
Name: gfx1150
Marketing Name: AMD Radeon Graphics
```

A minimal HIP smoke test was also compiled and run with:

```bash
hipcc --offload-arch=gfx1150 hip_smoke.cpp -o hip_smoke
./hip_smoke
```

The expected result was:

```text
result=1.000000
```

This confirmed that HIP kernels could compile and execute on the target GPU.

## 4. CPU baseline first

Before modifying the GPU backend, the CPU version was built and tested.

This step is important because it provides a numerical reference for later GPU validation.

Example CPU build:

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DHIGHS_HOME=/usr/local \
  -DCMAKE_C_FLAGS_RELEASE="-O2 -DNDEBUG" \
  -DCMAKE_CXX_FLAGS_RELEASE="-O2 -DNDEBUG"

cmake --build build-cpu --target plc -j"$(nproc)"
```

Example CPU run:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out ~/cupdlp_rocm_port_logs/baseline/afiro_cpu_sum.json \
  -nIterLim 200
```

The CPU baseline was used later to compare objective values, feasibility, gap, and termination status.

## 5. CUDA Toolkit for HIPIFY

`hipify-clang` needs CUDA headers to parse CUDA source files. A CUDA-capable NVIDIA GPU is not required for this parsing step, but the CUDA Toolkit headers are useful.

For this port, CUDA Toolkit 12.3 was installed only to provide headers such as:

```text
cublas_v2.h
cusparse.h
cuda_runtime_api.h
```

The CUDA driver was not used for execution. Runtime execution happens through ROCm/HIP.

## 6. Backend source conversion

Only the original CUDA backend files were converted with HIPIFY:

```text
cupdlp/cuda/cupdlp_cuda_kernels.cu
cupdlp/cuda/cupdlp_cudalinalg.cu
cupdlp/cuda/cupdlp_cuda_kernels.cuh
cupdlp/cuda/cupdlp_cudalinalg.cuh
```

They were copied into a new HIP backend directory:

```text
cupdlp/hip/
```

The generated HIP backend files are:

```text
cupdlp/hip/cupdlp_hip_kernels.cpp
cupdlp/hip/cupdlp_hip_linalg.cpp
cupdlp/hip/cupdlp_hip_kernels.h
cupdlp/hip/cupdlp_hip_linalg.h
```

The general approach was:

```bash
export CUDA_HOME=/usr/local/cuda-12.3
export HIP_HOME=/opt/rocm

hipify-clang \
  --cuda-path="$CUDA_HOME" \
  --cuda-gpu-arch=sm_70 \
  --default-preprocessor \
  --inplace \
  --no-backup \
  cupdlp/hip/cupdlp_cuda_kernels.cu \
  -- \
  -std=c++17 \
  -I./cupdlp \
  -Icupdlp/hip \
  -I"$CUDA_HOME/include" \
  -I"$HIP_HOME/include"
```

The same style of command was used for the other `.cu` and `.cuh` files.

After conversion, the files were renamed from CUDA-oriented names to HIP-oriented names.

## 7. Manual fixes after HIPIFY

HIPIFY handled many CUDA runtime and cuSPARSE references, but some changes required manual fixes.

### 7.1 Header paths

Some HIP headers needed ROCm-style include paths:

```cpp
#include <hip/hip_runtime.h>
#include <hip/hip_runtime_api.h>
#include <hipblas/hipblas.h>
#include <hipsparse/hipsparse.h>
```

### 7.2 CUDA warp mask width

CUDA code used 32-bit masks such as:

```cpp
__shfl_down_sync(0xFFFFFFFF, value, offset)
```

On the AMD HIP path, the mask must be a 64-bit integer. The calls were changed to:

```cpp
__shfl_down_sync(0xFFFFFFFFFFFFFFFFULL, value, offset)
```

This fixed compile-time errors from ROCm Clang on `gfx1150`.

### 7.3 CUDA library names

Remaining CUDA library symbols were manually replaced in the HIP path:

```text
cudaMalloc      -> hipMalloc
cudaFree        -> hipFree
cudaMemcpy      -> hipMemcpy
cudaDeviceReset -> hipDeviceReset

cublas*         -> hipblas*
cusparse*       -> hipsparse*

CUSPARSE_*      -> HIPSPARSE_*
CUDA_R_32F      -> HIP_R_32F
CUDA_R_64F      -> HIP_R_64F
```

### 7.4 Unsupported helper APIs

Some CUDA helper functions did not have a direct HIP equivalent. For example, `cublasGetStatusString(status)` was not directly converted. It was replaced with a simpler HIP-side error message.

## Migration helper scripts

Some project-level changes were applied through small helper scripts stored under:

```text
tools/migration/

These scripts document the mechanical parts of the migration, such as:

cleaning user-visible CUDA wording in the HIP backend
fixing ROCm/HIP include selection
adding BUILD_ROCM=ON while keeping BUILD_HIP=ON as a compatibility alias
updating documentation to prefer the ROCm build option

They are not required for normal users building the project. They are kept to make the porting process easier to audit and reproduce.

## 8. CMake integration

A new CMake option was added:

```cmake
option(BUILD_HIP "<BUILD_HIP_OR_NOT>" OFF)
```

The top-level CMake logic was extended so that CUDA and HIP cannot both be enabled:

```cmake
if (${BUILD_CUDA} STREQUAL "ON" AND ${BUILD_HIP} STREQUAL "ON")
    message(FATAL_ERROR "BUILD_CUDA and BUILD_HIP cannot both be ON")
endif ()
```

For the HIP build, CMake enables the HIP language and locates ROCm packages:

```cmake
enable_language(HIP)

find_package(hip REQUIRED CONFIG)
find_package(hipblas REQUIRED CONFIG)
find_package(hipsparse REQUIRED CONFIG)

set(CMAKE_HIP_ARCHITECTURES gfx1150 CACHE STRING "AMD GPU architecture")
```

The HIP backend library is built as:

```cmake
add_library(hiplin SHARED
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_kernels.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_linalg.cpp
)

set_source_files_properties(
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_kernels.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/cupdlp_hip_linalg.cpp
    PROPERTIES LANGUAGE HIP
)

target_link_libraries(hiplin
    PRIVATE
    hip::device
    roc::hipblas
    roc::hipsparse
    m
)
```

The full `plc` executable links against:

```text
cupdlp
hiplin
hip::host
roc::hipblas
roc::hipsparse
```

### BUILD_ROCM and BUILD_HIP

`BUILD_ROCM=ON` is the recommended public build option for this repository.

`BUILD_HIP=ON` is kept as a legacy compatibility alias. Internally, the ROCm backend is still implemented with HIP, hipBLAS, and hipSPARSE.

## 9. Host-side code adaptation

Not all migration work happened inside `.cu` or `.cuh` files.

Several C host files also needed manual changes because they created GPU handles, allocated GPU memory, or called BLAS/SPARSE routines.

Important files included:

```text
cupdlp/cupdlp_defs.h
cupdlp/cupdlp_linalg.c
cupdlp/cupdlp_utils.c
interface/mps_highs.c
interface/CMakeLists.txt
```

A small abstraction layer was introduced in `cupdlp_defs.h`:

```c
#if defined(CUPDLP_USE_HIP)
#include "hip/cupdlp_hip_kernels.h"
#include "hip/cupdlp_hip_linalg.h"
typedef hipsparseDnVecDescr_t cupdlp_sp_dnvec_descr_t;
typedef hipsparseSpMatDescr_t cupdlp_sp_mat_descr_t;
typedef hipsparseHandle_t cupdlp_sp_handle_t;
typedef hipblasHandle_t cupdlp_blas_handle_t;
#elif !(CUPDLP_CPU)
#include "cuda/cupdlp_cuda_kernels.cuh"
#include "cuda/cupdlp_cudalinalg.cuh"
typedef cusparseDnVecDescr_t cupdlp_sp_dnvec_descr_t;
typedef cusparseSpMatDescr_t cupdlp_sp_mat_descr_t;
typedef cusparseHandle_t cupdlp_sp_handle_t;
typedef cublasHandle_t cupdlp_blas_handle_t;
#endif
```

This allowed the main solver data structures to use project-level type aliases instead of directly depending on CUDA or HIP types.

## 10. Building this ROCm/HIP port

For the current gfx1150 target:

```bash
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

The generated executable is:

```text
build-rocm-plc/bin/plc
```

## 11. Running the validation example

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out ~/cupdlp_rocm_port_logs/hip_run/afiro_hip_sum.json \
  -nIterLim 200
```

The verified output includes:

```json
{
  "solver": "cuPDLP-C",
  "nIter": 199,
  "dPrimalObj": -464.76346057035607,
  "dDualObj": -464.83422735641489,
  "dRelPrimalFeas": 0.00003927125321,
  "dRelDualFeas": 0.00000565531500,
  "dRelDualityGap": 0.00007604444646,
  "terminationCode": "OPTIMAL",
  "primalCode": "FEASIBLE",
  "dualCode": "FEASIBLE"
}
```

## 12. Adapting the port to other AMD GPUs

For a different AMD GPU, the main change is usually the HIP architecture name.

First identify the GPU architecture:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then replace:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

with the architecture reported by ROCm, for example:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1030
-DCMAKE_HIP_ARCHITECTURES=gfx1100
-DCMAKE_HIP_ARCHITECTURES=gfx1103
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

The exact architecture depends on the target GPU and ROCm support.

If the source code is already HIPified, most users should not need to rerun `hipify-clang`. They should only rebuild with the correct `CMAKE_HIP_ARCHITECTURES` value.

If porting a new CUDA project from scratch, the general workflow is:

1. Verify ROCm sees the GPU.
2. Build a CPU baseline.
3. Identify CUDA source files and CUDA host API usage.
4. Run HIPIFY on CUDA backend files.
5. Manually fix headers, CMake, platform macros, and unsupported APIs.
6. Replace cuBLAS/cuSPARSE with hipBLAS/hipSPARSE.
7. Build the HIP backend alone first.
8. Link the full application.
9. Validate numerics against the CPU baseline.
10. Test more problem instances and larger workloads.

## 13. Current limitations

This port is not yet a production-ready ROCm solver.

Known limitations:

* Only `example/afiro.mps` has been validated so far.
* Some internal function names and fields still retain CUDA-style names.
* Some user-visible logs still contain legacy CUDA wording.
* No broad test matrix has been added yet.
* No CI workflow has been added yet.
* No performance tuning has been performed for gfx1150.
* Larger LP instances still need to be tested.

## 14. Recommended next steps

Suggested next engineering steps:

1. Clean user-visible CUDA wording in logs and JSON timer names.
2. Add more MPS validation cases.
3. Add CPU vs HIP result comparison scripts.
4. Add a CI build check where ROCm is available.
5. Add architecture notes for other AMD GPUs.
6. Gradually rename internal CUDA-style function and field names after tests are stable.
7. Profile sparse matrix-vector operations on gfx1150.
8. Document known ROCm version requirements.

