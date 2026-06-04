#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

CASES_FILE="${1:-validation/cases.txt}"
RESULT_ROOT="${RESULT_ROOT:-validation/results/latest}"
ROCM_ARCH="${ROCM_ARCH:-gfx1150}"

CPU_BUILD_DIR="build-cpu"
ROCM_BUILD_DIR="build-rocm-plc"

rm -rf "$RESULT_ROOT"
mkdir -p "$RESULT_ROOT"

echo "== cuPDLP-C-ROCm validation =="
echo "root       : $ROOT_DIR"
echo "cases      : $CASES_FILE"
echo "results    : $RESULT_ROOT"
echo "rocm arch  : $ROCM_ARCH"
echo ""

echo "== configure CPU build =="
cmake -S . -B "$CPU_BUILD_DIR" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_HIP=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

echo "== build CPU plc =="
cmake --build "$CPU_BUILD_DIR" --target plc -j"$(nproc)"

echo "== configure ROCm build =="
cmake -S . -B "$ROCM_BUILD_DIR" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES="$ROCM_ARCH"

echo "== build ROCm plc =="
cmake --build "$ROCM_BUILD_DIR" --target plc -j"$(nproc)"

echo ""
echo "== run validation cases =="

PASS_COUNT=0
INCOMPLETE_COUNT=0
FAIL_COUNT=0

while IFS=, read -r name mps_path n_iter_lim; do
  if [[ -z "${name:-}" ]] || [[ "$name" =~ ^# ]]; then
    continue
  fi

  case_dir="$RESULT_ROOT/$name"
  mkdir -p "$case_dir"

  cpu_json="$case_dir/${name}_cpu.json"
  rocm_json="$case_dir/${name}_rocm.json"
  cpu_log="$case_dir/${name}_cpu.log"
  rocm_log="$case_dir/${name}_rocm.log"
  report_md="$case_dir/${name}_compare.md"

  echo ""
  echo "== case: $name =="
  echo "mps       : $mps_path"
  echo "nIterLim  : $n_iter_lim"

  echo "-- CPU run"
  "./$CPU_BUILD_DIR/bin/plc" \
    -fname "$mps_path" \
    -out "$cpu_json" \
    -nIterLim "$n_iter_lim" \
    2>&1 | tee "$cpu_log"

  echo "-- ROCm run"
  "./$ROCM_BUILD_DIR/bin/plc" \
    -fname "$mps_path" \
    -out "$rocm_json" \
    -nIterLim "$n_iter_lim" \
    2>&1 | tee "$rocm_log"

echo "-- compare"
set +e
scripts/compare_cpu_rocm.py \
  --case "$name" \
  --cpu "$cpu_json" \
  --rocm "$rocm_json" \
  --out "$report_md"
compare_status=$?
set -e

overall_result="$(grep -E '^Overall result:' "$report_md" | sed -E 's/.*\*\*([^*]+)\*\*.*/\1/')"

case "$overall_result" in
  PASS)
    echo "case $name: PASS"
    PASS_COUNT=$((PASS_COUNT + 1))
    ;;
  INCOMPLETE)
    echo "case $name: INCOMPLETE"
    INCOMPLETE_COUNT=$((INCOMPLETE_COUNT + 1))
    ;;
  FAIL|*)
    echo "case $name: FAIL"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    ;;
esac

done < "$CASES_FILE"

echo ""
echo "== validation summary =="
echo "PASS: $PASS_COUNT"
echo "INCOMPLETE: $INCOMPLETE_COUNT"
echo "FAIL: $FAIL_COUNT"
echo "results: $RESULT_ROOT"

if [[ "$FAIL_COUNT" -ne 0 ]]; then
  exit 1
fi
