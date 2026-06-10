#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

source scripts/env/w7900_python_rocm_env.sh

rm -rf build-rocm-w7900

cmake -S . -B build-rocm-w7900 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH="${ROCM_PY_DEVEL}" \
  -DCMAKE_HIP_ARCHITECTURES=gfx1100 \
  -DCMAKE_C_FLAGS="-I${ROCM_PY_DEVEL}/include" \
  -DCMAKE_CXX_FLAGS="-I${ROCM_PY_DEVEL}/include" \
  -DCMAKE_HIP_FLAGS="-I${ROCM_PY_DEVEL}/include"

cmake --build build-rocm-w7900 --target plc -j"$(nproc)"
