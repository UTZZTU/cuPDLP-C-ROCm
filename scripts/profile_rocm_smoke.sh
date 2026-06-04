#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

ROCM_ARCH="${ROCM_ARCH:-gfx1150}"
RESULT_ROOT="${RESULT_ROOT:-profiling/results/latest}"

mkdir -p "$RESULT_ROOT"

echo "== cuPDLP-C-ROCm profiling smoke =="
echo "root      : $ROOT_DIR"
echo "rocm arch : $ROCM_ARCH"
echo "results   : $RESULT_ROOT"

echo ""
echo "== ensure ROCm build exists =="
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES="$ROCM_ARCH"

cmake --build build-rocm-plc --target plc -j"$(nproc)"

echo ""
echo "== baseline: afiro =="
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out "$RESULT_ROOT/afiro_rocm_baseline.json" \
  -nIterLim 200 \
  2>&1 | tee "$RESULT_ROOT/afiro_rocm_baseline.log"

echo ""
echo "== baseline: sc50b =="
./build-rocm-plc/bin/plc \
  -fname ./validation/netlib/sc50b.mps \
  -out "$RESULT_ROOT/sc50b_rocm_baseline.json" \
  -nIterLim 5000 \
  2>&1 | tee "$RESULT_ROOT/sc50b_rocm_baseline.log"

if ! command -v rocprofv3 >/dev/null 2>&1; then
  echo ""
  echo "rocprofv3 not found; baseline profiling complete."
  exit 0
fi

echo ""
echo "== rocprofv3 version =="
rocprofv3 --version || true

echo ""
echo "== rocprofv3 trace: afiro =="
mkdir -p "$RESULT_ROOT/afiro_rocprofv3"

rocprofv3 \
  --runtime-trace \
  --summary \
  --summary-per-domain \
  --output-directory "$RESULT_ROOT/afiro_rocprofv3" \
  --output-file afiro \
  --output-format csv \
  -- ./build-rocm-plc/bin/plc \
      -fname ./example/afiro.mps \
      -out "$RESULT_ROOT/afiro_rocm_profiled.json" \
      -nIterLim 200 \
  2>&1 | tee "$RESULT_ROOT/afiro_rocprofv3.log"

echo ""
echo "== rocprofv3 trace: sc50b =="
mkdir -p "$RESULT_ROOT/sc50b_rocprofv3"

rocprofv3 \
  --runtime-trace \
  --summary \
  --summary-per-domain \
  --output-directory "$RESULT_ROOT/sc50b_rocprofv3" \
  --output-file sc50b \
  --output-format csv \
  -- ./build-rocm-plc/bin/plc \
      -fname ./validation/netlib/sc50b.mps \
      -out "$RESULT_ROOT/sc50b_rocm_profiled.json" \
      -nIterLim 5000 \
  2>&1 | tee "$RESULT_ROOT/sc50b_rocprofv3.log"

echo ""
echo "== generated profiling files =="
find "$RESULT_ROOT" -maxdepth 3 -type f | sort

echo ""
echo "== profiling smoke complete =="
