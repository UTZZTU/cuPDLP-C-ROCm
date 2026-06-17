# Porting cuPDLP-C from CUDA to ROCm/HIP

> 中文版: [`ROCM_PORTING_GUIDE.zh-CN.md`](ROCM_PORTING_GUIDE.zh-CN.md)

This document records how this repository was ported from the original CUDA-based cuPDLP-C project to a ROCm/HIP build targeting AMD Radeon 890M / `gfx1150`.

It has two purposes:

1. Record the migration path used for this repository.
2. Provide a reusable CUDA-to-HIP checklist for similar GPU solver projects.

## 1. Project background

The original cuPDLP-C project contains a CUDA backend for GPU-accelerated linear programming. This port keeps the CPU path and upstream-compatible CUDA path, and adds a ROCm/HIP backend for AMD hardware.

Initial validated ROCm target:

| Item | Value |
|---|---|
| GPU/APU | AMD Radeon 890M |
| Architecture | `gfx1150` |
| OS | Ubuntu 24.04.x |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| HiGHS | 1.6.0 |

## 2. Migration strategy

The migration was staged instead of doing a global search-and-replace.

Main workflow:

1. Keep upstream CUDA code as a reference.
2. Verify ROCm can detect and run on the target device.
3. Build and run the CPU baseline first.
4. Convert only CUDA backend source files with `hipify-clang`.
5. Create a separate `cupdlp/hip/` backend directory.
6. Manually adapt headers, CMake, and host-side C/C++ code.
7. Replace CUDA runtime, cuBLAS, and cuSPARSE calls in the ROCm path.
8. Build the HIP backend as a standalone library.
9. Link the HIP backend into the full `plc` executable.
10. Validate against CPU outputs.
11. Add hygiene checks and CTest smoke validation.
12. Add profiling before performance tuning.
13. Add cross-device benchmark comparison against CUDA baselines.

This staged approach made each failure mode easier to isolate.

## 3. ROCm environment verification

Before porting code, verify the target GPU:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm-smi
/opt/rocm/bin/hipcc --version
```

A minimal HIP smoke test should compile and run before touching the solver:

```bash
hipcc --offload-arch=gfx1150 hip_smoke.cpp -o hip_smoke
./hip_smoke
```

## 4. CPU baseline first

Build the CPU baseline before modifying GPU code:

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

Example run:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

The CPU output is the numerical reference for ROCm validation.

## 5. HIPIFY scope

Only the original CUDA backend files should be HIPified:

```text
cupdlp/cuda/cupdlp_cuda_kernels.cu
cupdlp/cuda/cupdlp_cudalinalg.cu
cupdlp/cuda/cupdlp_cuda_kernels.cuh
cupdlp/cuda/cupdlp_cudalinalg.cuh
```

They are migrated into:

```text
cupdlp/hip/cupdlp_hip_kernels.cpp
cupdlp/hip/cupdlp_hip_linalg.cpp
cupdlp/hip/cupdlp_hip_kernels.h
cupdlp/hip/cupdlp_hip_linalg.h
```

Do not HIPIFY the whole repository blindly. Host-side C/C++ integration requires manual review.

## 6. Manual fixes after HIPIFY

Common manual fixes included:

- adjusting ROCm/HIP include paths,
- using 64-bit masks for HIP warp/wavefront shuffle calls where needed,
- replacing CUDA runtime calls with HIP runtime calls,
- replacing cuBLAS calls with hipBLAS calls,
- replacing cuSPARSE calls with hipSPARSE calls,
- adapting unsupported helper APIs,
- adding `CHECK_HIP` and `CHECK_HIP_STRICT` style macros,
- preserving internal compatibility symbols until the C/HIP boundary can be refactored safely.

Examples:

```text
cudaMalloc      -> hipMalloc
cudaFree        -> hipFree
cudaMemcpy      -> hipMemcpy
cudaDeviceReset -> hipDeviceReset
cublas*         -> hipblas*
cusparse*       -> hipsparse*
CUDA_R_32F      -> HIP_R_32F
CUDA_R_64F      -> HIP_R_64F
```

## 7. CMake integration

The public ROCm build option is:

```bash
-DBUILD_ROCM=ON
```

The top-level CMake configuration must reject CUDA and ROCm being enabled together.

For ROCm/HIP builds, CMake enables HIP and locates ROCm packages such as:

```cmake
enable_language(HIP)
find_package(hip REQUIRED CONFIG)
find_package(hipblas REQUIRED CONFIG)
find_package(hipsparse REQUIRED CONFIG)
```

The HIP architecture is set with:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

## 8. Host-side code adaptation

Several C host files required manual adaptation because they allocate GPU memory, create handles, or call BLAS/SPARSE routines.

Important areas:

```text
cupdlp/cupdlp_defs.h
cupdlp/cupdlp_linalg.c
cupdlp/cupdlp_utils.c
interface/mps_highs.c
interface/CMakeLists.txt
```

A small backend compatibility layer maps CUDA and HIP descriptor/handle types behind project-level aliases. This lets the main solver code avoid directly depending on CUDA or HIP types where possible.

## 9. Build the ROCm/HIP port

For `gfx1150`:

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

The generated executable is:

```text
build-rocm-plc/bin/plc
```

## 10. Validate with a smoke example

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

A successful run should report `terminationCode = OPTIMAL`, `primalCode = FEASIBLE`, and `dualCode = FEASIBLE`.

## 11. Adapt to other AMD GPUs

Identify the architecture:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then replace:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

with the target architecture, for example:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

for Radeon PRO W7900, subject to ROCm version and OS support.

## 12. Migration helper scripts

Mechanical migration helpers are stored under:

```text
tools/migration/
```

They document mechanical edits and are not required for normal users building the project.

## 13. Naming policy

User-visible documentation and output should prefer ROCm/HIP terminology. Historical migration notes and upstream backups may retain CUDA terminology. Internal compatibility symbols may remain until the C/HIP boundary is refactored safely.

Do not remove `cuda_csr_Ax`, `cuda_csc_ATy`, or `cuda_alloc_MVbuffer` without a dedicated compatibility pass and validation run.

## 14. Current limitations and completion status

- The ROCm/HIP backend is still experimental and should not be described as
  a production-certified solver release.
- Both `gfx1150` / 890M and `gfx1100` / W7900 now have validation records.
- The W7900 validation pass has been completed for the current project stage:
  smoke validation, Netlib validation, large-MPS baseline, P10 profiling,
  P11 SpMV tuning, and the P12 rejected experiment note are all documented.
- Some internal CUDA-style names remain at the C/HIP compatibility boundary.
- Broad large-MPS validation has curated summaries; raw MPS files and raw
  logs remain outside Git.
- ROCm CI is not yet available.

## 15. Recommended next-step status

The original recommended next steps are mostly completed. The only remaining
optional enhancements are:

1. W7900 P14-A: current-vs-before representative repeated validation.
2. W7900 P14-B: CSR ALG1-vs-ALG2 representative repeated validation.

Beyond these, do not add deeper numerical-path optimization unless a full
validation protocol is designed first.
