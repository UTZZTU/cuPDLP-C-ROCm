# Backend modes and naming policy

> 中文版：[BACKEND_MODES_AND_NAMING.zh-CN.md](BACKEND_MODES_AND_NAMING.zh-CN.md)

This repository maintains three backend modes. They are **mutually exclusive by project policy**:

| Mode | CMake options | Role |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | Correctness and portability baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | Upstream-compatible NVIDIA reference backend |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD GPU backend; current primary platform is W7900 / `gfx1100` |

Radeon 890M / `gfx1150` is the earlier ROCm migration and tuning milestone. Radeon PRO W7900 / `gfx1100` is the current branch focus.

## Build-mode contract

Use exactly one mode at a time and keep a separate build directory for each mode:

```text
build-cpu
build-cuda
build-rocm-w7900
```

Do not reuse a CMake cache across backends.

The current top-level CMake configuration does not yet provide a dedicated fatal guard for the invalid combination `BUILD_CUDA=ON` and `BUILD_ROCM=ON`. Therefore, documentation and automation must pass both options explicitly. Adding a CMake-level guard is a future engineering hardening task; it is not part of this documentation-only change.

`BUILD_HIP` is not a supported public option. Use `BUILD_ROCM=ON`.

## Why CUDA is retained

The CUDA path is intentionally preserved because it:

- keeps the code close to upstream cuPDLP-C;
- provides NVIDIA reference measurements;
- helps distinguish ROCm-specific defects from general GPU-backend behavior;
- supports a controlled CUDA-to-ROCm migration case study;
- preserves a comparison path for convergence-sensitive cases.

Retaining CUDA does not make this a CUDA-first branch. The current branch focus is the ROCm/HIP path on W7900.

## Source layout

```text
cupdlp/cuda/                    upstream-compatible CUDA backend
cupdlp/hip/                     ROCm/HIP backend
cupdlp/                         shared solver code
cupdlp/cupdlp_backend_compat.h  backend compatibility aliases
interface/                      command-line solver frontends
```

Shared C code should use compatibility aliases instead of directly calling a backend-specific runtime where practical.

Examples:

| Shared alias | CUDA | ROCm/HIP |
|---|---|---|
| `CUPDLP_BLAS_DAXPY` | `cublasDaxpy` | `hipblasDaxpy` |
| `CUPDLP_SPARSE_CREATE_CSR` | `cusparseCreateCsr` | `hipsparseCreateCsr` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |

## Naming policy

### Keep real backend names

CUDA names are correct in:

```text
cupdlp/cuda/
README_UPSTREAM.md
CUDA benchmark records
historical migration notes
```

ROCm/HIP names are correct in:

```text
cupdlp/hip/
ROCm build and validation output
W7900 profiling and tuning documents
```

### Prefer backend-neutral names in shared interfaces

User-facing shared output should prefer terms such as:

```text
device
GPU
sparse backend
BLAS backend
device preparation
```

Avoid presenting CUDA-specific names as if they described the ROCm backend.

### Preserve compatibility symbols until a validated refactor

Some internal shared symbols still contain `cuda_`, including names such as:

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

Do not rename them mechanically. A safe rename requires replacement symbols or wrappers plus CPU, CUDA, and ROCm validation.

## Recommended build commands

CPU:

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

CUDA:

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

W7900 ROCm/HIP:

```bash
cmake -S . -B build-rocm-w7900 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100 \
  -DCMAKE_PREFIX_PATH="$CMAKE_PREFIX_PATH"

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
```

On the recorded W7900 environment, prefer the maintained scripts because the ROCm SDK and HiGHS paths are machine-specific:

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

## Minimum validation after backend-facing changes

| Changed area | Minimum check |
|---|---|
| Shared CPU code | CPU build and `afiro` |
| CUDA backend or compatibility aliases | CUDA build and smoke cases |
| ROCm/HIP backend | W7900 build and smoke |
| Algorithm-adjacent GPU code | Extended Netlib plus representative large-MPS checks |
| Performance-sensitive code | Correctness validation, repeated timing, and profiling |
| Naming or documentation only | Markdown/link checks and `git diff --check` |

The primary validated executable is `plc`. Optional Python/apps paths are not part of the current ROCm validation contract.

## Related documents

- [ROCm workflow](ROCM_WORKFLOW.md)
- [ROCm porting guide](ROCM_PORTING_GUIDE.md)
- [Validation semantics](VALIDATION.md)
- [W7900 current status](W7900_CURRENT_STATUS.md)
