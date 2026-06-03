# cuPDLP-C ROCm/HIP port for AMD Radeon 890M gfx1150

This repository contains an experimental ROCm/HIP port of cuPDLP-C targeting AMD Radeon 890M / gfx1150.

## Tested environment

- OS: Ubuntu 24.04.4
- ROCm: 7.2.1
- GPU: AMD Radeon 890M, gfx1150
- HiGHS: 1.6.0
- CMake: 3.28
- HIP compiler: ROCm Clang 22.0.0

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

Run

./build-hip-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_hip_sum.json \
  -nIterLim 200

Verified result

The example/afiro.mps test runs successfully on AMD Radeon 890M / gfx1150.

Known verified output:

terminationCode: OPTIMAL
nIter: 199
Linked ROCm libraries include libamdhip64, libhipblas, libhipsparse, librocblas, and librocsparse.

Notes

This is a work-in-progress ROCm/HIP port. Some internal symbols still retain CUDA-style names for compatibility with the original cuPDLP-C code structure.

