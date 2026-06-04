# ROCm porting guide

This document describes how this repository was ported from the original CUDA-oriented cuPDLP-C project to a ROCm/HIP backend for AMD GPUs/APUs.

The guide has two purposes:

1. Record the migration path used by this repository.
2. Provide a reusable migration checklist for similar CUDA-to-ROCm solver projects.

The public project identity is **ROCm**. Internally, the GPU backend is implemented with **HIP**, **hipBLAS**, and **hipSPARSE**.

## Current target

The current verified ROCm target is:

| Item | Value |
|---|---|
| GPU/APU | AMD Radeon 890M |
| Architecture | `gfx1150` |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| HiGHS | 1.6.0 |
| Build system | CMake + Ninja |
| Recommended build option | `BUILD_ROCM=ON` |

## Current porting status

The current ROCm port is experimental but functional.

Working items:

- CPU baseline build works.
- ROCm/HIP backend library builds.
- `plc` executable links against the ROCm/HIP backend.
- ROCm/HIP smoke validation passes.
- Extended Netlib validation has multiple passing cases.
- CTest integration is available.
- Initial `rocprofv3` profiling workflow is available.
- User-facing README, validation, and tuning documentation have been updated.

Known limitations:

- The validation matrix is still small.
- Larger LP instances still need to be tested.
- No ROCm CI runner is currently configured.
- Performance tuning is still at the profiling-baseline stage.
- Some internal CUDA-style names remain for compatibility across C and HIP/C++ boundaries.
- The legacy CUDA source directory is still present for upstream reference and future cleanup.

## Why ROCm and HIP both appear

ROCm is the AMD GPU compute software platform.

HIP is the C++ runtime API and kernel language used inside ROCm to write portable GPU code and to migrate CUDA-oriented code.

This repository therefore uses the following naming rule:

| Layer | Preferred wording |
|---|---|
| Project identity | ROCm |
| Public build option | `BUILD_ROCM=ON` |
| Backend implementation | HIP |
| BLAS library | hipBLAS |
| Sparse library | hipSPARSE |
| CMake language | HIP |
| Architecture variable | `CMAKE_HIP_ARCHITECTURES` |

This is why the project is called `cuPDLP-C-ROCm`, while the backend source directory is still:

```text
cupdlp/hip/
```

## High-level migration strategy

The migration was performed in stages instead of doing a single global replacement.

The staged strategy was:

1. Keep the original upstream project as a reference.
2. Create a separate ROCm working branch/repository.
3. Verify that ROCm detects the target AMD GPU/APU.
4. Build and run the CPU baseline first.
5. Convert only CUDA backend files with `hipify-clang`.
6. Manually adapt CMake.
7. Manually adapt host-side C/C++ code that touches GPU handles and descriptors.
8. Build the HIP backend library by itself.
9. Link the full `plc` executable.
10. Validate ROCm/HIP results against the CPU baseline.
11. Add hygiene checks to prevent accidental regressions.
12. Add CTest integration.
13. Add profiling workflow before attempting performance tuning.
14. Document the port.

This staged approach made the migration easier to debug because each stage had a clear success condition.

## Original code areas involved

The original CUDA-oriented backend was mainly under:

```text
cupdlp/cuda/
```

Important CUDA backend files included:

```text
cupdlp/cuda/cupdlp_cuda_kernels.cu
cupdlp/cuda/cupdlp_cudalinalg.cu
cupdlp/cuda/cupdlp_cuda_kernels.cuh
cupdlp/cuda/cupdlp_cudalinalg.cuh
```

The new ROCm/HIP backend lives under:

```text
cupdlp/hip/
```

Current ROCm/HIP backend files include:

```text
cupdlp/hip/cupdlp_hip_kernels.cpp
cupdlp/hip/cupdlp_hip_linalg.cpp
cupdlp/hip/cupdlp_hip_kernels.h
cupdlp/hip/cupdlp_hip_linalg.h
cupdlp/hip/CMakeLists.txt
```

Host-side files that required manual adaptation included:

```text
cupdlp/cupdlp_defs.h
cupdlp/cupdlp_linalg.c
cupdlp/cupdlp_utils.c
interface/mps_highs.c
CMakeLists.txt
cupdlp/CMakeLists.txt
interface/CMakeLists.txt
```

## Step 1: verify the ROCm environment

Before changing code, verify that ROCm can see the target device.

Useful commands:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
hipcc --version
```

For this project, the important architecture value is:

```text
gfx1150
```

The build must pass this architecture to CMake:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

## Step 2: build the CPU baseline

Before touching the GPU backend, build and run the CPU version.

Example:

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_HIP=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

Run a baseline case:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

The CPU result is used later as the numerical reference for the ROCm/HIP backend.

## Step 3: use hipify only where it helps

`hipify-clang` is useful for CUDA `.cu` and `.cuh` backend files.

It is not a full-project migration tool.

Use it for files that contain CUDA runtime, CUDA kernels, cuBLAS, or cuSPARSE code.

Do not rely on it for:

- top-level CMake design,
- host-side solver architecture,
- project option naming,
- validation design,
- documentation,
- performance tuning,
- compatibility wrappers.

For this project, the practical rule is:

```text
Use hipify-clang for CUDA backend files.
Use manual review for C, C++, CMake, and documentation.
```

## Step 4: convert CUDA backend files

The original backend files were copied from `cupdlp/cuda/` into `cupdlp/hip/`, then converted.

Example conversion pattern:

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

After conversion, the generated files were renamed to HIP-oriented names.

Example final file names:

```text
cupdlp_hip_kernels.cpp
cupdlp_hip_linalg.cpp
cupdlp_hip_kernels.h
cupdlp_hip_linalg.h
```

## Step 5: manually fix HIP headers

HIPIFY may not produce exactly the include layout wanted by the project.

The HIP backend uses ROCm/HIP headers such as:

```cpp
#include <hip/hip_runtime.h>
#include <hipblas/hipblas.h>
#include <hipsparse/hipsparse.h>
#include <hip/hip_cooperative_groups.h>
```

The exact includes depend on which runtime, BLAS, sparse, and kernel features are used.

## Step 6: replace CUDA runtime and library APIs

Common replacements include:

| CUDA / NVIDIA API | ROCm/HIP API |
|---|---|
| `cudaMalloc` | `hipMalloc` |
| `cudaFree` | `hipFree` |
| `cudaMemcpy` | `hipMemcpy` |
| `cudaMemcpyAsync` | `hipMemcpyAsync` |
| `cudaDeviceSynchronize` | `hipDeviceSynchronize` |
| `cudaDeviceReset` | `hipDeviceReset` |
| `cublasCreate` | `hipblasCreate` |
| `cublasDestroy` | `hipblasDestroy` |
| `cublasDaxpy` | `hipblasDaxpy` |
| `cublasDdot` | `hipblasDdot` |
| `cusparseCreate` | `hipsparseCreate` |
| `cusparseDestroy` | `hipsparseDestroy` |
| `cusparseSpMV` | `hipsparseSpMV` |
| `cusparseCreateCsr` | `hipsparseCreateCsr` |
| `cusparseCreateCsc` | `hipsparseCreateCsc` |
| `cusparseCreateDnVec` | `hipsparseCreateDnVec` |
| `CUDA_R_64F` | `HIP_R_64F` |
| `CUDA_R_32F` | `HIP_R_32F` |
| `CUSPARSE_OPERATION_TRANSPOSE` | `HIPSPARSE_OPERATION_TRANSPOSE` |

Some APIs do not have a direct one-line equivalent and require manual handling.

## Step 7: handle warp and wavefront assumptions

CUDA code often assumes a 32-lane warp.

AMD GPUs commonly use a 64-lane wavefront.

This project encountered CUDA-style shuffle masks such as:

```cpp
__shfl_down_sync(0xFFFFFFFF, value, offset)
```

For the AMD HIP path, the mask was changed to a 64-bit mask:

```cpp
__shfl_down_sync(0xFFFFFFFFFFFFFFFFULL, value, offset)
```

This was necessary for ROCm Clang on `gfx1150`.

When porting other code, search for assumptions such as:

```text
warpSize == 32
0xFFFFFFFF
threadIdx.x % 32
lane < 32
```

These may need review for AMD wavefront behavior.

## Step 8: add CMake ROCm support

The public build option is:

```cmake
option(BUILD_ROCM "<BUILD_ROCM_OR_NOT>" OFF)
```

A legacy compatibility alias is kept:

```cmake
option(BUILD_HIP "<LEGACY_ALIAS_FOR_BUILD_ROCM>" OFF)
```

`BUILD_ROCM=ON` is the recommended user-facing option.

`BUILD_HIP=ON` exists only because the ROCm backend is implemented with HIP and earlier migration steps used the HIP name directly.

The top-level CMake logic must prevent incompatible backend combinations:

```cmake
if (${BUILD_CUDA} STREQUAL "ON" AND ${BUILD_ROCM} STREQUAL "ON")
    message(FATAL_ERROR "BUILD_CUDA and BUILD_ROCM cannot both be ON")
endif ()
```

The ROCm/HIP path enables HIP and finds ROCm packages:

```cmake
enable_language(HIP)

find_package(hip REQUIRED CONFIG)
find_package(hipblas REQUIRED CONFIG)
find_package(hipsparse REQUIRED CONFIG)

set(CMAKE_HIP_ARCHITECTURES gfx1150 CACHE STRING "AMD GPU architecture")
```

## Step 9: build the HIP backend library

The HIP backend library is built from `.cpp` files compiled as HIP sources.

Representative structure:

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

Building `hiplin` alone is a useful intermediate milestone because it isolates HIP compilation and linking problems from the full solver executable.

## Step 10: adapt host-side type aliases

Host-side C files also need GPU descriptor and handle types.

This project introduced type aliases in `cupdlp_defs.h`.

Representative idea:

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

This allows the main solver data structures to use project-level aliases instead of directly depending on CUDA or HIP type names everywhere.

## Step 11: adapt host-side setup and cleanup

Host-side setup code must create ROCm/HIP handles when building the ROCm backend.

Examples:

```c
hipsparseCreate(&w->cusparsehandle);
hipblasCreate(&w->cublashandle);
```

Cleanup paths must destroy the corresponding handles:

```c
hipsparseDestroy(w->cusparsehandle);
hipblasDestroy(w->cublashandle);
```

Device reset uses:

```c
hipDeviceReset();
```

Some field names still contain legacy CUDA-style words, such as `cusparsehandle` or `cublashandle`. These are internal compatibility names and should be renamed only after validation coverage is stronger.

## Step 12: preserve C/HIP boundary compatibility

Some exported HIP backend function names still use legacy CUDA-style prefixes.

Examples:

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

These names are currently kept intentionally because host-side C files call them.

Directly renaming these functions without wrappers can cause linker errors such as:

```text
undefined reference to `cuda_csr_Ax'
undefined reference to `cuda_csc_ATy'
```

Safe future cleanup should use wrappers:

```text
hip_csr_Ax       -> new implementation name
cuda_csr_Ax      -> compatibility wrapper calling hip_csr_Ax
```

Only after all host-side call sites are migrated should the legacy wrappers be removed.

## Step 13: add hygiene checks

The hygiene script is:

```bash
./scripts/check_rocm_port_hygiene.sh
```

It checks that:

- HIP backend `.cpp` files do not reintroduce direct legacy check macros,
- CMake files do not reintroduce `plchip`,
- CMake files do not reintroduce the misleading `CUDA_LIBRARY-NOTFOUND` flag,
- required HIP check macros are present,
- required legacy exported compatibility symbols are still present.

This script exists because some CUDA-style names are intentionally preserved for compatibility, while others should be cleaned from user-visible ROCm/HIP code.

## Step 14: validate against CPU

The recommended full local check is:

```bash
./scripts/check_rocm_port.sh
```

This runs:

1. ROCm port hygiene checks.
2. CPU-vs-ROCm smoke validation.

Smoke validation currently includes:

| Case | Result |
|---|---|
| `afiro` | PASS |
| `sc50b` | PASS |

Extended Netlib validation currently includes:

| Case | Result |
|---|---|
| `afiro` | PASS |
| `adlittle` | PASS |
| `blend` | PASS |
| `sc50a` | PASS |
| `sc50b` | PASS |
| `share2b` | INCOMPLETE |

Run extended validation with:

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

See `docs/VALIDATION.md` for the validation semantics.

## Step 15: add CTest integration

CTest is available when configuring with:

```bash
-DBUILD_TESTING=ON
```

Run:

```bash
ctest --test-dir build-rocm-plc --output-on-failure
```

Current registered tests:

| Test | Purpose |
|---|---|
| `rocm_port_hygiene` | ROCm/HIP naming and compatibility guardrails |
| `rocm_smoke_validation` | CPU-vs-ROCm smoke validation |

CTest is useful because it provides a standard validation entry point for future CI.

## Step 16: profile before tuning

Do not start performance tuning before validation is stable.

The current smoke profiling script is:

```bash
./scripts/profile_rocm_smoke.sh
```

It runs baseline smoke cases and then `rocprofv3` runtime tracing when available.

Initial profiling on `gfx1150` shows hot areas including:

- HIP kernel launch overhead,
- HIP memory copy activity,
- ROCclr copy buffer dispatches,
- rocSPARSE SpMV kernels,
- rocBLAS vector kernels,
- custom PDLP update kernels.

The first tuning direction should be:

```text
reduce synchronization + reduce copies + reduce small kernel launch overhead
```

See `docs/TUNING_GUIDE_ROCM.md` for profiling notes.

## Building the ROCm port

For the current `gfx1150` target:

```bash
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

Run:

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

## Adapting to other ROCm GPUs

For a different ROCm-supported AMD GPU/APU, first identify the architecture:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then replace:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

with the target architecture.

Examples:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1030
-DCMAKE_HIP_ARCHITECTURES=gfx1100
-DCMAKE_HIP_ARCHITECTURES=gfx1103
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

The exact support status depends on:

- ROCm version,
- Linux distribution,
- kernel version,
- AMD GPU/APU model,
- ROCm packaging support for that GPU.

For a new GPU target, the recommended workflow is:

1. Verify ROCm device detection.
2. Build CPU baseline.
3. Build ROCm/HIP backend with the correct architecture.
4. Run smoke validation.
5. Run extended validation.
6. Run profiling smoke.
7. Compare results with `gfx1150` baseline behavior.

## Migration checklist for similar projects

For another CUDA-based numerical solver project, use this checklist:

1. Create a separate ROCm working copy.
2. Keep the upstream CUDA version as a reference.
3. Build a CPU or non-GPU baseline first.
4. Verify ROCm sees the target GPU.
5. Identify CUDA kernel and library files.
6. Use `hipify-clang` only on CUDA backend files.
7. Manually review generated HIP code.
8. Fix headers and platform macros.
9. Replace CUDA runtime calls with HIP runtime calls.
10. Replace cuBLAS calls with hipBLAS calls.
11. Replace cuSPARSE calls with hipSPARSE calls.
12. Review warp-size assumptions.
13. Review shuffle masks.
14. Review atomic operations.
15. Review stream and synchronization logic.
16. Review device memory allocation and copy logic.
17. Add CMake ROCm/HIP support.
18. Build the GPU backend library independently.
19. Link the full application.
20. Validate numerics against the CPU baseline.
21. Add regression scripts.
22. Add hygiene checks.
23. Add profiling workflow.
24. Tune only after correctness is stable.

## Common migration pitfalls

Common pitfalls include:

- assuming AMD wavefront size is always the same as CUDA warp size,
- using 32-bit CUDA shuffle masks on AMD HIP paths,
- converting only `.cu` files and forgetting host-side C/C++ GPU handle code,
- letting `BUILD_HIP` become the public project identity instead of `BUILD_ROCM`,
- changing exported C/HIP boundary symbols too early,
- forgetting to link hipBLAS and hipSPARSE at the executable level,
- using `hipcc` directly as `CMAKE_HIP_COMPILER` with newer CMake versions,
- assuming small smoke cases represent real GPU performance,
- optimizing before CPU-vs-ROCm validation is stable.

## File naming policy

Use ROCm for public project and documentation names:

```text
cuPDLP-C-ROCm
ROCM_PORTING_GUIDE.md
TUNING_GUIDE_ROCM.md
BUILD_ROCM
```

Use HIP for implementation-level code and build language names:

```text
cupdlp/hip/
CMAKE_HIP_ARCHITECTURES
hip::device
hipBLAS
hipSPARSE
```

Use legacy CUDA-style names only when they are compatibility boundaries or upstream reference content.

## Current cleanup policy

CUDA-style names are handled in three categories.

### Keep for history

Keep CUDA wording in:

- upstream reference documentation,
- migration history,
- comments that explicitly describe the original CUDA source,
- `README_UPSTREAM.md`.

### Clean from user-facing ROCm output

Clean CUDA wording from:

- README,
- build messages,
- ROCm logs,
- generated binary names,
- validation docs,
- tuning docs,
- user-visible error messages in the ROCm/HIP backend.

### Refactor gradually

Refactor later, with wrappers and validation:

- `cuda_csr_Ax`,
- `cuda_csc_ATy`,
- `cuda_alloc_MVbuffer`,
- `cuda_vec`,
- `cuda_csr`,
- `cuda_csc`,
- `cusparsehandle`,
- `cublashandle`.

These names should not be mass-replaced without a compatibility plan.

## What this port does not claim yet

This port does not yet claim:

- full production readiness,
- broad ROCm architecture coverage,
- full Netlib coverage,
- large-scale LP performance results,
- finished gfx1150 tuning,
- complete removal of legacy CUDA-style internal names,
- ROCm CI coverage.

The current claim is narrower:

```text
The project builds and runs a ROCm/HIP backend on gfx1150,
passes the current CPU-vs-ROCm smoke validation,
has extended Netlib validation coverage,
has CTest integration,
and has an initial rocprofv3 profiling workflow.
```

## Recommended next steps

Recommended engineering next steps:

1. Keep documentation accurate.
2. Add more validation cases.
3. Investigate the `share2b` INCOMPLETE case.
4. Add larger LP cases.
5. Add profiling summary scripts.
6. Add ROCTx ranges around solver phases.
7. Reduce unnecessary synchronization and memory copies.
8. Investigate kernel launch granularity.
9. Add ROCm CI when a runner is available.
10. Gradually refactor internal CUDA-style names with wrappers.
11. Validate more ROCm GPU architectures.
12. Document architecture-specific tuning notes.

## Related documentation

See also:

```text
README.md
docs/VALIDATION.md
docs/TUNING_GUIDE_ROCM.md
README_UPSTREAM.md
```
