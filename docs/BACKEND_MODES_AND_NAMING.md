# Backend modes and naming policy

This repository keeps three mutually exclusive build modes:

| Mode | CMake options | Role |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | Correctness and portability baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | Upstream-compatible NVIDIA backend and benchmark baseline |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD Radeon 890M / gfx1150 target backend |

`BUILD_CUDA` and `BUILD_ROCM` must not be enabled at the same time.

`BUILD_HIP` has been removed as a public option. Use `BUILD_ROCM=ON` for the ROCm/HIP backend.

## Why CUDA is retained

This project is a ROCm/HIP port of upstream cuPDLP-C, but the CUDA backend is intentionally retained.

The CUDA backend is useful because:

- it keeps the repository close to the upstream implementation,
- it provides an NVIDIA baseline for cross-device benchmark comparison,
- it helps distinguish ROCm-specific issues from general GPU-backend behavior,
- it provides context for CUDA-to-ROCm migration documentation.

For example, the `greenbea` case shows GPU-backend convergence sensitivity on both CUDA and ROCm paths. Keeping the CUDA backend makes that interpretation possible.

## Backend source layout

Important backend-related paths:

```text
cupdlp/cuda/     CUDA backend source inherited from upstream cuPDLP-C
cupdlp/hip/      ROCm/HIP backend source
cupdlp/          Shared CPU/GPU solver code
interface/       Solver executable frontends
```

Shared C sources should not directly call CUDA-only or HIP-only runtime/library APIs. They should use backend compatibility aliases defined in:

```text
cupdlp/cupdlp_backend_compat.h
```

This file maps shared backend operations to CUDA or ROCm/HIP implementations depending on the active build mode.

Examples:

| Shared alias | CUDA mode | ROCm/HIP mode |
|---|---|---|
| `CUPDLP_BLAS_DAXPY` | `cublasDaxpy` | `hipblasDaxpy` |
| `CUPDLP_SPARSE_CREATE_CSR` | `cusparseCreateCsr` | `hipsparseCreateCsr` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |

## Naming policy

This repository uses the following naming policy.

### Keep CUDA names when they are real CUDA backend code

CUDA naming is expected and correct in:

```text
cupdlp/cuda/
README_UPSTREAM.md
upstream history
CUDA benchmark notes
```

These names should not be renamed just to remove the word CUDA.

### Prefer ROCm/HIP names in ROCm user-facing paths

ROCm/HIP user-facing output and documentation should avoid misleading CUDA wording.

Examples of names that should be avoided in ROCm-facing output:

```text
CudaPrepare
CUDA timing
cuSPARSE timing
cuBLAS timing
```

Prefer backend-neutral or ROCm-specific wording:

```text
DevicePrepare
GPU timing
ROCm timing
sparse backend timing
BLAS backend timing
hipSPARSE timing
hipBLAS timing
```

### Preserve compatibility symbols until safely refactored

Some internal function or field names still use legacy CUDA-style names because they are shared across C and C++/HIP boundaries.

Examples include compatibility symbols such as:

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

These should not be removed by a blind rename. They should only be refactored after:

1. adding replacement backend-neutral symbols,
2. keeping temporary aliases or wrappers,
3. validating CPU, CUDA, and ROCm builds,
4. running smoke validation on all supported backends.

## Current validation expectation

Before claiming a backend-mode change is safe, run at least:

| Mode | Minimum check |
|---|---|
| CPU | build `plc` and run `afiro` |
| CUDA | build `plc` and run `afiro`; preferably also `sc50b` and `lotfi` |
| ROCm/HIP | build `plc` and run `afiro`; preferably run the smoke validation script |

Recent compatibility restoration verified:

| Backend | Smoke result |
|---|---|
| CPU | `afiro` reaches `OPTIMAL` |
| ROCm/HIP | `afiro` reaches `OPTIMAL` |
| CUDA | `afiro`, `sc50b`, and `lotfi` reach `OPTIMAL` |

## Build directory policy

Use separate build directories for different backend modes.

Recommended names:

```text
build-cpu
build-cuda
build-rocm-plc
```

Do not reuse a CUDA build directory for ROCm or a ROCm build directory for CUDA, because CMake cache variables are persistent across reconfiguration.

## Recommended commands

CPU mode:

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

CUDA mode:

```bash
cmake -S . -B build-cuda -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DCMAKE_PREFIX_PATH="$HIGHS_HOME"

cmake --build build-cuda --target plc -j"$(nproc)"
```

ROCm/HIP mode:

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

Legacy option behavior:

```bash
cmake -S . -B build-hip-removed-check -G Ninja -DBUILD_HIP=ON
```

This should fail with a message telling the user to use `BUILD_ROCM=ON`.

## Practical rule for future cleanup

Do not remove CUDA-related names globally.

Instead:

1. keep real CUDA backend code in `cupdlp/cuda/`,
2. keep upstream history in `README_UPSTREAM.md` and migration notes,
3. clean misleading CUDA wording from ROCm/HIP user-facing output,
4. preserve compatibility symbols until CPU, CUDA, and ROCm smoke tests pass after replacement,
5. document every backend-facing rename in the validation notes.
