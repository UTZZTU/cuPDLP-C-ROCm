#!/usr/bin/env bash
set -euo pipefail

ROOT="$HOME/rocm_dir/pdlp/cuPDLP-C-ROCm"
CASES="$ROOT/validation/cases_benchmark_200m.txt"

CPU_BIN="$ROOT/build-cpu/bin/plc"
GPU_BIN="$ROOT/build-rocm-plc/bin/plc"

RUN_ID="ryzen_ai_890m_full_200m_$(date +%Y%m%d_%H%M%S)"
OUT="$ROOT/validation/results/runs/$RUN_ID"

CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-3600}"

mkdir -p "$OUT"

echo "RUN_ID=$RUN_ID"
echo "OUT=$OUT"
echo "CASE_TIMEOUT_SEC=$CASE_TIMEOUT_SEC"
echo

{
  echo "== date =="
  date
  echo
  echo "== hostname =="
  hostname
  echo
  echo "== ROCm/HIP =="
  which hipcc || true
  hipcc --version || true
  echo
  echo "== GPU =="
  rocminfo | grep -E "Name:|gfx" | head -n 40 || true
  rocm-smi || true
  echo
  echo "== binaries =="
  ls -lh "$CPU_BIN" "$GPU_BIN"
  echo
  echo "== linked ROCm libs =="
  ldd "$GPU_BIN" | grep -Ei "hip|roc|amd|hsa|highs|blas|sparse" || true
  echo
  echo "== git =="
  git -C "$ROOT" rev-parse HEAD
  git -C "$ROOT" status --short
} | tee "$OUT/run_env.txt"

run_one() {
  local label="$1"
  local bin="$2"
  local name="$3"
  local mps_abs="$4"
  local iter="$5"
  local case_out="$6"

  local json="$case_out/${name}_${label}.json"
  local log="$case_out/${name}_${label}.log"
  local exitcode_file="$case_out/${name}_${label}.exitcode"

  echo "--- ${label^^} $name"

  set +e
  timeout "$CASE_TIMEOUT_SEC" "$bin" \
    -fname "$mps_abs" \
    -out "$json" \
    -nIterLim "$iter" \
    2>&1 | tee "$log"
  local code=${PIPESTATUS[0]}
  set -e

  echo "$code" > "$exitcode_file"

  if [ "$code" -eq 0 ]; then
    echo "OK ${label^^} $name"
  elif [ "$code" -eq 124 ]; then
    echo "TIMEOUT ${label^^} $name after ${CASE_TIMEOUT_SEC}s"
  else
    echo "FAILED ${label^^} $name exit_code=$code"
  fi

  echo
}

while IFS=, read -r name mps iter tier; do
  [[ -z "${name// }" ]] && continue
  [[ "$name" =~ ^# ]] && continue

  case_out="$OUT/$name"
  mkdir -p "$case_out"

  mps_abs="$ROOT/$mps"

  echo "=============================="
  echo "case=$name"
  echo "tier=$tier"
  echo "mps=$mps_abs"
  echo "nIterLim=$iter"
  echo "=============================="

  {
    echo "case=$name"
    echo "tier=$tier"
    echo "mps=$mps_abs"
    echo "nIterLim=$iter"
    echo "start=$(date)"
  } > "$case_out/meta.txt"

  if [[ ! -f "$mps_abs" ]]; then
    echo "MISSING: $mps_abs" | tee "$case_out/MISSING.txt"
    continue
  fi

  run_one "cpu" "$CPU_BIN" "$name" "$mps_abs" "$iter" "$case_out"
  run_one "rocm" "$GPU_BIN" "$name" "$mps_abs" "$iter" "$case_out"

  echo "end=$(date)" >> "$case_out/meta.txt"
done < "$CASES"

{
  echo "== rocm-smi after =="
  rocm-smi || true
} | tee "$OUT/rocm_smi_after.txt"

echo "$OUT" > "$ROOT/validation/results/latest_run.txt"
echo "Saved latest run path to $ROOT/validation/results/latest_run.txt"
