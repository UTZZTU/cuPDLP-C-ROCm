# cuPDLP-C ROCm/HIP Port for AMD Radeon 890M / gfx1150

This repository contains an experimental ROCm/HIP port of **cuPDLP-C**, targeting **AMD Radeon 890M / gfx1150** on Ubuntu Linux.

The original cuPDLP-C project is CUDA-based. This fork adds a HIP backend, CMake support for ROCm builds, and validates a minimal working run on AMD integrated graphics.

## Current status

Working milestone:

* Builds successfully with ROCm/HIP.
* Links against HIP runtime, hipBLAS, hipSPARSE, rocBLAS, and rocSPARSE.
* Runs `example/afiro.mps` successfully.
* Produces an `OPTIMAL` result on AMD Radeon 890M / gfx1150.
* Tested with `BUILD_HIP=ON`.

This is still a work-in-progress port. Some internal symbols may still use CUDA-style names for compatibility with the original project structure.

## Tested environment

* OS: Ubuntu 24.04.4
* ROCm: 7.2.1
* HIP compiler: ROCm Clang 22.0.0
* GPU: AMD Radeon 890M
* GPU target: `gfx1150`
* HiGHS: 1.6.0
* Build system: CMake + Ninja

## Build

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

## Run

```bash
./build-hip-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_hip_sum.json \
  -nIterLim 200
```

## Verified `afiro.mps` result

A verified HIP run on AMD Radeon 890M / gfx1150 produced:

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

## ROCm libraries observed at runtime

The generated `plc` executable links against ROCm libraries including:

* `libamdhip64`
* `libhipblas`
* `libhipsparse`
* `librocblas`
* `librocsparse`
* `libhsa-runtime64`

It also links against the project HIP backend library:

* `libhiplin.so`

## What changed in this port

Main changes include:

* Added HIP backend source files under `cupdlp/hip/`.
* Added `BUILD_HIP` CMake option.
* Added CMake integration for HIP language builds.
* Replaced CUDA runtime calls with HIP runtime calls in the ROCm build path.
* Replaced cuBLAS calls with hipBLAS calls.
* Replaced cuSPARSE calls with hipSPARSE calls.
* Validated the `afiro.mps` example on AMD Radeon 890M / gfx1150.

## Known limitations

* This port has currently been validated only on `example/afiro.mps`.
* Some internal function names and structure fields still use CUDA-style names.
* Log messages and timer names may still contain legacy CUDA wording in some places.
* Performance tuning has not yet been performed.
* This is not yet a polished upstream-quality port.

## Original project

This project is based on cuPDLP-C. The original project files and license are preserved in this repository. See `README_UPSTREAM.md` for the original upstream README.

## License

This repository preserves the original project license. See `LICENSE`.

