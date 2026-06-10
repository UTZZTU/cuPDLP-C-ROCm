#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

export HIGHS_HOME="${HIGHS_HOME:-/root/cupdlp_w7900/deps/install/highs-1.6.0}"
export LD_LIBRARY_PATH="${HIGHS_HOME}/lib:${LD_LIBRARY_PATH:-}"

rm -rf build-cpu

cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_HIP=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
