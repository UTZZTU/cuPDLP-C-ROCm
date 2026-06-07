# CUDA to ROCm/HIP migration case study

This document summarizes the practical migration path used in this repository to turn upstream `cuPDLP-C` into a CPU / CUDA / ROCm-HIP three-mode project.

The purpose is to help future contributors understand not only what changed, but also why the migration was done this way.

## Project context

Upstream `cuPDLP-C` is CUDA-oriented. This fork targets AMD Radeon 890M / gfx1150 through ROCm/HIP while preserving:

- CPU mode as the correctness and portability baseline,
- CUDA mode as the upstream-compatible NVIDIA backend,
- ROCm/HIP mode as the AMD target backend.

The final project is not a CUDA-deleted fork. It is a three-backend engineering branch.

## Why not delete CUDA?

At the start of the migration, it was tempting to remove the CUDA backend and keep only CPU + ROCm/HIP.

That turned out to be the wrong long-term direction.

CUDA is useful because:

1. It is the upstream GPU backend.
2. It gives an NVIDIA baseline for cross-device comparison.
3. It helps distinguish ROCm porting issues from general GPU numerical behavior.
4. It keeps the fork easier to compare with upstream `cuPDLP-C`.
5. It helps future contributors understand which parts are original CUDA logic and which parts are ROCm-specific.

The current policy is:

| Backend | Keep? | Reason |
|---|---|---|
| CPU | yes | correctness and portability baseline |
| CUDA | yes | upstream-compatible NVIDIA baseline |
| ROCm/HIP | yes | AMD Radeon 890M / gfx1150 target backend |

## High-level migration strategy

The migration followed a staged approach:

1. Establish a CPU baseline.
2. Add a minimal ROCm/HIP backend.
3. Get a tiny smoke case running first.
4. Add build and validation scripts.
5. Expand Netlib/MPS coverage.
6. Restore CUDA compatibility after ROCm changes.
7. Document backend modes and naming rules.
8. Add cross-device benchmark workflow.
9. Add ROCm tuning ablation evidence.
10. Document numerical behavior on convergence-sensitive cases.

This was more reliable than trying to port everything and optimize everything in one step.

## External guidance and how it maps to this project

AMD's HIP portability guidance notes that automated hipify tools can significantly speed up CUDA-to-HIP translation, but larger projects still need manual work around build systems, unsupported constructs, hardcoded assumptions, and backend-specific optimization. It also explicitly raises the design question of whether a project should maintain separate CUDA and HIP backends.

This repository chose to maintain explicit backend modes instead of replacing all CUDA naming globally.

ROCm documentation also emphasizes CMake package usage and `CMAKE_PREFIX_PATH=/opt/rocm` for locating ROCm package config files. That matches the build strategy used here for ROCm/HIP.

NVIDIA's CMake guidance describes CUDA as a first-class CMake language in modern CMake. This matters because preserving CUDA mode requires not only keeping `.cu` files, but also ensuring CMake can still configure and link the CUDA target cleanly.

Useful references:

- AMD GPUOpen, *Application portability with HIP*: https://gpuopen.com/learn/amd-lab-notes/amd-lab-notes-hipify-readme/
- ROCm documentation, *Using CMake*: https://rocm.docs.amd.com/en/latest/conceptual/cmake-packages.html
- NVIDIA Developer Blog, *Building Cross-Platform CUDA Applications with CMake*: https://developer.nvidia.com/blog/building-cuda-applications-cmake/
- Ginkgo CUDA-to-HIP porting case study: https://arxiv.org/abs/2006.14290
- GPU numerics portability paper: https://arxiv.org/abs/2410.09172
- HIP auto-tuning paper: https://arxiv.org/abs/2407.11488

## Build-mode design

The current public build modes are:

| Mode | CMake options | Purpose |
|---|---|---|
| CPU | `BUILD_CUDA=OFF`, `BUILD_ROCM=OFF` | CPU baseline |
| CUDA | `BUILD_CUDA=ON`, `BUILD_ROCM=OFF` | upstream-compatible NVIDIA backend |
| ROCm/HIP | `BUILD_CUDA=OFF`, `BUILD_ROCM=ON` | AMD target backend |

`BUILD_CUDA` and `BUILD_ROCM` are mutually exclusive.

`BUILD_HIP` was removed as a public option to avoid confusion. The public ROCm/HIP build mode is now `BUILD_ROCM=ON`.

Recommended build-directory layout:

```bash
build-cpu/
build-cuda/
build-rocm-plc/
```

Do not reuse one build directory across CPU, CUDA, and ROCm modes. CMake caches backend-related variables, compilers, and package paths.

## Backend compatibility layer

One of the most important lessons is that a direct CUDA-to-HIP replacement in shared C files can accidentally break CUDA builds.

Examples of problematic patterns:

```c
hipblasCreate(...)
hipsparseCreate(...)
hipDeviceReset()
hipFree(...)
```

If these calls appear in shared code without backend guards, CUDA mode can fail to compile or link.

The solution was to introduce backend compatibility aliases so shared code can call project-level abstractions instead of directly calling CUDA or HIP APIs.

Examples of intended abstraction style:

```c
CUPDLP_BLAS_CREATE(...)
CUPDLP_SPARSE_CREATE(...)
CUPDLP_DEVICE_RESET()
CUPDLP_DEVICE_FREE(...)
```

Then the compatibility header maps these to the correct backend:

| Project-level API | CUDA mode | ROCm/HIP mode |
|---|---|---|
| `CUPDLP_BLAS_CREATE` | `cublasCreate` | `hipblasCreate` |
| `CUPDLP_SPARSE_CREATE` | `cusparseCreate` | `hipsparseCreate` |
| `CUPDLP_DEVICE_RESET` | `cudaDeviceReset` | `hipDeviceReset` |
| `CUPDLP_DEVICE_FREE` | `cudaFree` | `hipFree` |

This made it possible to keep one shared solver path while preserving both CUDA and ROCm/HIP builds.

## What should be renamed, and what should not

A migration project can easily waste time trying to rename every internal `cuda_*` symbol.

This repository uses a staged naming policy:

| Area | Policy |
|---|---|
| README / docs | user-visible backend naming should say CPU / CUDA / ROCm-HIP clearly |
| scripts | use ROCm/HIP names for ROCm workflows |
| user-visible logs | avoid misleading CUDA wording in ROCm-only paths where practical |
| internal compatibility symbols | may retain CUDA-style names if changing them risks breakage |
| upstream history docs | keep upstream CUDA references intact |
| migration tools | preserve history and intent |

This is why some internal fields or symbols may still contain names like `cuda_csr`, `cuda_vec`, or `cupdlp_update_average_cuda`.

Those are compatibility names, not evidence that ROCm/HIP runs are using CUDA libraries.

## Validation progression

The validation workflow evolved in stages.

### Stage 1: tiny smoke

Start with:

```text
example/afiro.mps
```

This answers:

- Does the program build?
- Does it load an MPS file?
- Does it initialize the backend?
- Does it produce a valid JSON result?
- Does it terminate successfully?

### Stage 2: small Netlib cases

Then add small and medium cases such as:

```text
sc50b
sc105
sc205
scagr7
recipe
lotfi
```

This catches parser, memory, sparse matrix, and iteration-path issues.

### Stage 3: full cross-device benchmark

The project later expanded to a full benchmark matrix across:

- RTX 3090 CUDA,
- RTX 4090D CUDA,
- Radeon 890M ROCm/HIP,
- CPU baselines on each machine.

The project uses `nIterLim=200000000` and treats 3600 seconds as the effective long-case wall-clock limit for cross-device reporting.

## Cross-device benchmark lessons

Cross-device results showed several important points:

1. Tiny cases are dominated by overhead.
2. Medium cases are more useful for comparing backend performance.
3. Some cases are faster on CPU than GPU because launch overhead dominates.
4. Some cases benefit from GPU execution.
5. `greenbea` is convergence-sensitive and should be analyzed separately.
6. CPU, CUDA, and ROCm/HIP iteration counts do not always match.

The project therefore separates:

| Workflow | Purpose |
|---|---|
| smoke validation | quick correctness |
| tuning quick set | performance development |
| full validation matrix | cross-device comparison |
| long numerical cases | convergence-trajectory analysis |

## ROCm tuning evidence

Several ROCm tuning changes were made:

| Commit | Change |
|---|---|
| `f9d7f0d` | remove redundant HIP device synchronize |
| `8fed073` | cache HIP device attributes |
| `fa7e860` | fuse ROCm average iterate axpy updates |
| `b44c7ab` | reduce movement interaction scalar copies |

Initially, these changes lacked a clean before/after comparison.

The project later added a repeated ablation:

- 6 tuning milestones,
- 6 cases,
- 5 repeats per milestone/case pair,
- median solve time as the primary metric,
- mean/std/min/max/CV preserved in CSV.

The repeated ablation showed approximately 1.094x geometric mean speedup from `pre_tuning` to current across the 6-case quick set. The strongest current-vs-baseline improvement was on `lotfi`.

The `reduce_scalar_copies` milestone was the fastest observed point for 5 of 6 quick cases, which means future tuning should compare against both current HEAD and that milestone.

## Numerical behavior lessons

`greenbea` is retained as a special numerical-behavior diagnostic case.

It should not be removed just because a GPU backend hits the wall-clock limit.

The project policy is:

- keep `greenbea` in the benchmark set,
- report timeout and feasibility/gap fields,
- distinguish solver convergence limits from runtime failures,
- avoid extending the time limit indefinitely,
- document CPU/CUDA/ROCm trajectory differences.

This is important because GPU numerical behavior can differ across NVIDIA and AMD backends due to library implementations, reduction order, floating-point operation order, and compiler behavior. Recent research on GPU numerics portability also highlights that numerical differences can appear when scientific programs are compiled and run across NVIDIA and AMD GPU stacks.

## Common pitfalls found in this migration

### 1. Backend option ambiguity

Problem:

```text
BUILD_HIP
BUILD_ROCM
BUILD_CUDA
```

Too many overlapping options make builds confusing.

Resolution:

```text
BUILD_CUDA=ON  -> CUDA
BUILD_ROCM=ON  -> ROCm/HIP
both OFF       -> CPU
BUILD_HIP      -> removed as public option
```

### 2. HIP calls leaking into CUDA mode

Problem:

```c
hipDeviceReset()
hipblasCreate()
hipsparseCreate()
```

appearing in shared paths.

Resolution:

Use backend compatibility macros.

### 3. ROCm-specific optimization breaking CUDA

Problem:

A fused ROCm kernel was called from shared code under a generic GPU guard.

Resolution:

Guard ROCm-only fused kernels with:

```c
#if defined(CUPDLP_USE_ROCM) && USE_KERNELS
```

CUDA mode should use the original BLAS/AXPY path unless equivalent CUDA implementation is added and validated.

### 4. Script placement drift

Problem:

Temporary scripts can accumulate in the repository root.

Resolution:

- regular build / validation / benchmark scripts go under `scripts/`,
- migration helper scripts go under `tools/migration/`,
- case lists and curated CSV summaries go under `validation/`,
- large local result directories stay under `validation/results/` and are not treated as the primary committed artifact.

### 5. Single-run benchmark conclusions

Problem:

Single-run timing is noisy.

Resolution:

Use repeated runs for tuning evidence. The current tuning ablation uses 5 repeats and reports median/mean/std/CV.

### 6. CRLF line endings in generated CSV

Problem:

Python `csv` output can use CRLF line endings, which can trip `git diff --check`.

Resolution:

Use:

```python
csv.DictWriter(..., lineterminator="\n")
```

and add `.gitattributes` rules for LF line endings.

## Recommended migration workflow for similar projects

For another CUDA-dependent scientific project, use this order:

1. Clone upstream and preserve a clean baseline branch.
2. Build and run CPU mode first.
3. Build and run upstream CUDA mode before making ROCm changes.
4. Add a minimal ROCm/HIP backend without deleting CUDA.
5. Introduce backend compatibility macros early.
6. Keep public build modes simple.
7. Start with one tiny smoke case.
8. Add small and medium cases.
9. Add scripts only after commands are stable.
10. Use consistent case lists.
11. Add cross-device benchmark summaries.
12. Keep long convergence-sensitive cases, but document them separately.
13. Benchmark performance changes with repeated runs.
14. Only then do deeper ROCm optimization.

## Recommended repository layout

```text
README.md
CMakeLists.txt
cupdlp/
  cuda/
  hip/
  cupdlp_backend_compat.h
interface/
scripts/
  run_validation.sh
  run_benchmark_*.sh
  summarize_benchmark.py
  run_rocm_tuning_*.sh
tools/
  migration/
validation/
  cases.txt
  cases_tuning_quick.txt
  rocm_tuning_ablation_*.csv
  rocm_tuning_ablation_*.md
docs/
  BACKEND_MODES_AND_NAMING.md
  VALIDATION.md
  CROSS_DEVICE_BENCHMARKS.md
  ROCM_TUNING_HISTORY.md
  NUMERICAL_BEHAVIOR_GREENBEA.md
  CUDA_TO_ROCM_MIGRATION_CASE_STUDY.md
```

## Practical commands

### CPU build

```bash
cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

### ROCm/HIP build

```bash
cmake -S . -B build-rocm-plc \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

### CUDA build

```bash
cmake -S . -B build-cuda \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=ON \
  -DBUILD_ROCM=OFF

cmake --build build-cuda --target plc -j"$(nproc)"
```

Use machine-specific CUDA and HiGHS environment variables as needed.

## What remains to improve

The project is functional, but not finished.

Remaining work:

1. Add more trajectory-level diagnostics for `greenbea`.
2. Compare CPU/CUDA/ROCm feasibility and gap curves at fixed checkpoints.
3. Continue ROCm profiling of launch overhead, SpMV, and vector update kernels.
4. Expand the LP test set beyond the current Netlib subset.
5. Keep CUDA smoke validation in CI-like scripts.
6. Reduce internal CUDA-style naming only when compatibility is protected.
7. Add clearer instructions for new contributors who want to reproduce the benchmark matrix.

## Summary

The most important lesson is:

> A robust CUDA-to-ROCm migration is not just a mechanical API translation. It is a staged engineering process involving backend boundaries, build-system design, validation, performance evidence, and numerical-behavior documentation.

For this repository, the successful path was:

1. keep CPU and CUDA baselines,
2. add ROCm/HIP as a third backend,
3. build compatibility aliases,
4. validate broadly,
5. benchmark across devices,
6. document tuning and numerical behavior,
7. avoid hiding difficult convergence-sensitive cases.
