# cuPDLP-C-ROCm

A ROCm/HIP port of **cuPDLP-C**, currently verified on **AMD Radeon 890M / gfx1150**.

This repository is based on the original CUDA-oriented cuPDLP-C project. The goal of this fork is to provide a ROCm-focused version with two main build paths:

* CPU-only PDLP
* ROCm/HIP accelerated PDLP

The first working ROCm milestone has been validated on `example/afiro.mps`.

## Current status

This project is currently an experimental ROCm/HIP port.

Verified so far:

* Builds successfully with ROCm 7.2.1.
* Builds a ROCm/HIP backend library.
* Links against HIP runtime, hipBLAS, hipSPARSE, rocBLAS, and rocSPARSE.
* Builds the `plc` executable.
* Runs `example/afiro.mps` successfully on AMD Radeon 890M / gfx1150.
* Produces `terminationCode = OPTIMAL` for the validated `afiro.mps` run.

Not yet complete:

* Only `example/afiro.mps` has been validated so far.
* Larger LP instances still need to be tested.
* Some internal names still use legacy CUDA-style naming.
* User-visible logs may still contain some legacy CUDA wording.
* No broad CPU-vs-ROCm validation matrix has been added yet.
* No ROCm CI workflow has been added yet.
* No performance tuning has been performed for gfx1150 yet.

## Tested environment

The first working ROCm/HIP milestone was tested with:

* OS: Ubuntu 24.04.4
* ROCm: 7.2.1
* HIP compiler: ROCm Clang 22.0.0
* GPU/APU: AMD Radeon 890M
* GPU architecture: `gfx1150`
* HiGHS: 1.6.0
* Build system: CMake + Ninja

## Repository layout

Important ROCm-related files and directories:

```text
cupdlp/hip/                 ROCm/HIP backend source files
CMakeLists.txt              Top-level build options, including BUILD_HIP
cupdlp/CMakeLists.txt       cuPDLP core library build logic
interface/CMakeLists.txt    plc executable and HiGHS wrapper build logic
README_UPSTREAM.md          Original upstream README backup
docs/                       ROCm porting, validation, and tuning notes
```

## Build ROCm/HIP version

For the currently verified AMD Radeon 890M / gfx1150 target:

```bash
cmake -S . -B build-hip-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_HIP=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-hip-plc --target plc -j"$(nproc)"
```

The generated executable is:

```text
build-hip-plc/bin/plc
```

## Run the verified example

```bash
./build-hip-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_hip_sum.json \
  -nIterLim 200
```

A verified ROCm/HIP run on AMD Radeon 890M / gfx1150 produced:

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

## Build CPU-only version

The CPU-only version remains useful as a correctness baseline.

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
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

## Adapting to other ROCm GPUs

This repository is currently verified on `gfx1150`.

For other ROCm-supported AMD GPUs or APUs, first identify the target architecture:

```bash
rocminfo | grep -E "Name:|Marketing Name|gfx"
rocm_agent_enumerator
```

Then replace:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

with your target architecture, for example:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1030
-DCMAKE_HIP_ARCHITECTURES=gfx1100
-DCMAKE_HIP_ARCHITECTURES=gfx1103
-DCMAKE_HIP_ARCHITECTURES=gfx1150
```

Actual support depends on your ROCm version, Linux distribution, kernel, and AMD GPU/APU support status.

## Porting notes

The current ROCm/HIP port followed this staged approach:

1. Verify ROCm can detect the target GPU.
2. Run a minimal HIP smoke test.
3. Build the CPU baseline first.
4. Use `hipify-clang` only for CUDA `.cu` / `.cuh` backend files.
5. Manually adapt CMake and host-side C/C++ code.
6. Replace CUDA runtime calls with HIP runtime calls.
7. Replace cuBLAS calls with hipBLAS calls.
8. Replace cuSPARSE calls with hipSPARSE calls.
9. Build the HIP backend as a standalone library.
10. Link the full `plc` executable.
11. Validate numerical results against the CPU baseline.

A more detailed migration guide will be maintained under:

```text
docs/PORTING_GUIDE_ROCM_HIP.md
```

## Roadmap

Planned next steps:

* Rewrite user-facing logs to use ROCm/HIP wording instead of legacy CUDA wording.
* Replace visible `CudaPrepare`, `Cuda device`, and `cuSparse` labels with ROCm/HIP labels.
* Add CPU-vs-ROCm validation scripts.
* Test more MPS examples beyond `afiro.mps`.
* Add a validation result table.
* Add ROCm tuning notes for gfx1150.
* Add guidance for other ROCm-supported AMD GPU/APU targets.
* Gradually clean internal CUDA-style names once tests are stable.

## Relationship to upstream cuPDLP-C

This repository is a ROCm-focused port based on the original cuPDLP-C project.

The original upstream README is preserved as:

```text
README_UPSTREAM.md
```

## License

This repository preserves the original project license.

See:

```text
LICENSE
```

