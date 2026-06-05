# cuPDLP-C-ROCm

A ROCm/HIP port of **cuPDLP-C** for AMD GPUs/APUs.

This fork keeps the original CPU path and adds a ROCm/HIP accelerated backend. The current working target is **AMD Radeon 890M / gfx1150** with **ROCm 7.2.1**.

> Status: experimental but buildable and validated on smoke cases. This is not yet a fully tuned or broadly certified ROCm solver release.

## Documentation

- [ROCm workflow guide](docs/ROCM_WORKFLOW.md) - common build, validation, profiling, and troubleshooting commands.

## What this repository provides

- CPU-only cuPDLP-C build path.
- ROCm/HIP backend built from migrated CUDA backend code.
- `plc` executable linked against the ROCm/HIP backend.
- CPU-vs-ROCm smoke validation scripts.
- Extended Netlib validation cases.
- CTest integration for ROCm port checks.
- Initial `rocprofv3` profiling workflow for gfx1150.
- Documentation for migration, validation, and tuning.

## Current status

### Working

- Builds successfully with ROCm 7.2.1.
- Builds the ROCm/HIP backend library.
- Links against HIP runtime, hipBLAS, hipSPARSE, rocBLAS, and rocSPARSE.
- Builds the `plc` executable.
- Runs CPU-vs-ROCm smoke validation.
- Registers ROCm checks through CTest.
- Runs initial `rocprofv3` profiling on smoke cases.

### Validated cases

Smoke validation currently passes:

| Case | Source | ROCm result |
|---|---|---|
| `afiro` | `example/afiro.mps` | PASS |
| `sc50b` | `validation/netlib/sc50b.mps` | PASS |

Extended Netlib validation currently reports:

| Case | Result | Notes |
|---|---|---|
| `afiro` | PASS | Baseline example |
| `adlittle` | PASS | Relative validation metrics pass |
| `blend` | PASS | Relative validation metrics pass |
| `sc50a` | PASS | Relative validation metrics pass |
| `sc50b` | PASS | Smoke + extended case |
| `share2b` | INCOMPLETE | Hits current iteration/time limit; not treated as a ROCm port failure |

See [`docs/VALIDATION.md`](docs/VALIDATION.md) for validation semantics.

### Still incomplete

- Only a small validation matrix has been exercised so far.
- Larger LP instances still need to be tested.
- No ROCm CI workflow has been added yet.
- The ROCm/HIP backend has not been performance tuned yet.
- Some internal symbols still use legacy CUDA-style names for compatibility across C and HIP/C++ boundaries.
- The legacy CUDA backend is still present for upstream reference and future cleanup.

## Tested environment

The current ROCm/HIP milestone was tested with:

| Component | Version / value |
|---|---|
| OS | Ubuntu 24.04.x |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| GPU/APU | AMD Radeon 890M |
| GPU architecture | `gfx1150` |
| HiGHS | 1.6.0 |
| Build system | CMake + Ninja |

## Repository layout

Important ROCm-related files and directories:

```text
cupdlp/hip/                         ROCm/HIP backend source files
scripts/check_rocm_port.sh           Full local ROCm port check
scripts/check_rocm_port_hygiene.sh   ROCm/HIP naming and compatibility guardrails
scripts/run_validation.sh            CPU-vs-ROCm validation runner
scripts/profile_rocm_smoke.sh        ROCm profiling smoke workflow
scripts/prepare_netlib_cases.sh      Netlib compressed MPS preparation helper
validation/cases.txt                 Default smoke validation case list
validation/cases_extended_netlib.txt Extended Netlib validation case list
docs/ROCM_PORTING_GUIDE.md       ROCm/HIP migration notes
docs/VALIDATION.md                   Validation plan and result semantics
docs/TUNING_GUIDE_ROCM.md            ROCm profiling and tuning notes
README_UPSTREAM.md                   Original upstream README backup
```

Generated outputs are intentionally ignored by Git:

```text
validation/results/
validation/netlib/
validation/netlib_compressed/
profiling/results/
tools/emps
tools/emps.c
```

## Quick start: build the ROCm/HIP version

For the currently verified AMD Radeon 890M / gfx1150 target:

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

## Run a ROCm/HIP example

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

A representative successful ROCm/HIP smoke run on `afiro` reports:

```json
{
  "solver": "cuPDLP-C",
  "nIter": 199,
  "terminationCode": "OPTIMAL",
  "primalCode": "FEASIBLE",
  "dualCode": "FEASIBLE"
}
```

## Build the CPU baseline

The CPU-only build is used as a correctness baseline for ROCm validation.

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

Example CPU run:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

## Validation

Recommended full local check:

```bash
./scripts/check_rocm_port.sh
```

This runs both:

1. ROCm port hygiene checks.
2. CPU-vs-ROCm smoke validation.

Run only the validation workflow:

```bash
./scripts/run_validation.sh
```

Run extended Netlib validation:

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

Extended validation may report `INCOMPLETE` for cases that hit the current iteration or time limit on both CPU and ROCm. `INCOMPLETE` is tracked separately from `FAIL`.

## CTest

When configured with `BUILD_TESTING=ON`, ROCm checks are registered with CTest.

Configure:

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
```

List tests:

```bash
ctest --test-dir build-rocm-plc -N
```

Run tests:

```bash
ctest --test-dir build-rocm-plc --output-on-failure
```

Current registered tests:

| Test | Purpose |
|---|---|
| `rocm_port_hygiene` | Checks ROCm/HIP naming and compatibility guardrails |
| `rocm_smoke_validation` | Runs CPU-vs-ROCm smoke validation |

## ROCm profiling

A first profiling workflow is available through:

```bash
./scripts/profile_rocm_smoke.sh
```

This script builds the ROCm target, runs baseline smoke cases, and then runs `rocprofv3` runtime tracing when available.

Initial gfx1150 profiling on the smoke cases shows that the small-case runtime is dominated by many small operations rather than one single long-running custom kernel. The observed hot areas include:

- HIP kernel launch overhead.
- HIP memory copy activity.
- ROCclr copy buffer dispatches.
- rocSPARSE SpMV kernels.
- rocBLAS vector kernels such as AXPY, dot, norm, and scaling.
- Custom PDLP update kernels.

See [`docs/TUNING_GUIDE_ROCM.md`](docs/TUNING_GUIDE_ROCM.md) for details.

Profiling outputs are written under:

```text
profiling/results/
```

These outputs are ignored by Git.

## Adapting to other ROCm GPUs

This repository is currently verified on `gfx1150`.

For another ROCm-supported AMD GPU/APU, first identify the architecture:

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
-DCMAKE_HIP_ARCHITECTURES=gfx1030
-DCMAKE_HIP_ARCHITECTURES=gfx1100
-DCMAKE_HIP_ARCHITECTURES=gfx1103
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

Actual support depends on the ROCm version, Linux distribution, kernel, and AMD GPU/APU support status.

## Build option compatibility

Use this for the ROCm/HIP backend:

```bash
-DBUILD_ROCM=ON
```

`BUILD_HIP=ON` is kept as a legacy compatibility alias because the ROCm backend is implemented with HIP, hipBLAS, and hipSPARSE.

Do not enable both CUDA and ROCm:

```bash
-DBUILD_CUDA=ON -DBUILD_ROCM=ON
```

The top-level CMake configuration rejects that combination.

## Porting strategy

The current ROCm/HIP port followed this staged approach:

1. Verify ROCm can detect the target GPU.
2. Build and validate the CPU baseline first.
3. Use `hipify-clang` only for CUDA `.cu` / `.cuh` backend files.
4. Manually adapt CMake and host-side C/C++ code.
5. Replace CUDA runtime calls with HIP runtime calls.
6. Replace cuBLAS calls with hipBLAS calls.
7. Replace cuSPARSE calls with hipSPARSE calls.
8. Build the ROCm/HIP backend as a standalone library.
9. Link the full `plc` executable.
10. Validate ROCm results against the CPU baseline.
11. Add hygiene checks to avoid accidental regressions.
12. Add CTest-backed smoke validation.
13. Start profiling before attempting performance tuning.

See [`docs/ROCM_PORTING_GUIDE.md`](docs/ROCM_PORTING_GUIDE.md) for the detailed migration notes.

## Why some CUDA-style names still remain

Some internal names still use legacy CUDA-style spelling, especially at C/HIP boundary points such as exported function names and struct fields.

These names are currently kept intentionally because they are part of the compatibility boundary between existing C code and the migrated HIP backend. They should be cleaned only after tests are stable and with compatibility wrappers in place.

The hygiene script currently protects some of these legacy exported symbols from accidental breakage:

```bash
./scripts/check_rocm_port_hygiene.sh
```

## Roadmap

Near-term priorities:

- Keep README and documentation accurate.
- Expand smoke and extended validation cases.
- Improve validation result reporting.
- Add more documented profiling summaries.
- Reduce unnecessary synchronization, memory copy, and small kernel launch overhead.
- Gradually clean internal CUDA-style names without breaking compatibility boundaries.
- Add CI when a suitable ROCm-capable environment is available.

Longer-term goals:

- Generalize the porting workflow for more ROCm-supported AMD GPUs/APUs.
- Provide tuning guidance by architecture family.
- Remove obsolete legacy CUDA code paths if this fork becomes ROCm-only.
- Compare performance across CPU, ROCm/HIP, and upstream CUDA-oriented baselines where available.

## Relationship to upstream cuPDLP-C

This repository is a ROCm-focused port based on the original cuPDLP-C project.

The original upstream README is preserved as:

```text
README_UPSTREAM.md
```

## License

This repository preserves the original project license. See:

```text
LICENSE
```
