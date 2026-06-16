#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

if [ -f /app/cupdlp_w7900/activate_w7900.sh ]; then
  # shellcheck disable=SC1091
  source /app/cupdlp_w7900/activate_w7900.sh
fi

STAMP="$(date +%Y%m%d_%H%M%S)"

RESULT_ROOT="${RESULT_ROOT:-/app/cupdlp_w7900/results/w7900_p10_current_targeted_rocprof_${STAMP}}"
MPS_ROOT="${MPS_ROOT:-/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps}"
ROCM_BUILD_DIR="${ROCM_BUILD_DIR:-build-rocm-w7900}"
GPU_ID="${GPU_ID:-0}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
SOLVER_TIME_LIMIT="${SOLVER_TIME_LIMIT:-300}"
NITER_LIM="${NITER_LIM:-1000000000}"

PLC="${ROCM_BUILD_DIR}/bin/plc"

if [ ! -x "${PLC}" ]; then
  echo "[INFO] missing ${PLC}; building ROCm W7900 target"
  bash scripts/build_w7900_rocm.sh
fi

if [ ! -x "${PLC}" ]; then
  echo "ERROR: plc not found after build: ${PLC}" >&2
  exit 1
fi

if ! command -v rocprofv3 >/dev/null 2>&1; then
  echo "ERROR: rocprofv3 not found in PATH" >&2
  exit 1
fi

mkdir -p "${RESULT_ROOT}/current"
mkdir -p validation/results

CASES=(
  "thk_48"
  "square41"
  "L2CTA3D"
  "set-cover-model"
  "tpl-tub-ws1617"
)

{
  echo "== W7900 P10 current targeted rocprof =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "commit: $(git rev-parse --short HEAD)"
  echo "result root: ${RESULT_ROOT}"
  echo "mps root: ${MPS_ROOT}"
  echo "plc: ${PLC}"
  echo "gpu binding: ROCR_VISIBLE_DEVICES=${GPU_ID}"
  echo "case timeout sec: ${CASE_TIMEOUT_SEC}"
  echo "solver dTimeLim: ${SOLVER_TIME_LIMIT}"
  echo "nIterLim: ${NITER_LIM}"
  echo
  echo "== tools =="
  command -v rocprofv3 || true
  rocprofv3 --version || true
  command -v hipcc || true
  hipcc --version | head -20 || true
  echo
  echo "== gpu =="
  rocm_agent_enumerator || true
  rocm-smi || true
  echo
  echo "== cases =="
  printf "%s\n" "${CASES[@]}"
} > "${RESULT_ROOT}/run_env.txt" 2>&1

for case in "${CASES[@]}"; do
  mps="${MPS_ROOT}/${case}.mps"
  case_dir="${RESULT_ROOT}/current/${case}"
  trace_dir="${case_dir}/trace"
  json="${case_dir}/${case}_rocm.json"
  log="${case_dir}/${case}_rocm.log"
  exitcode="${case_dir}/${case}_rocm.exitcode"

  mkdir -p "${trace_dir}"

  echo
  echo "============================================================"
  echo "== current / ${case}"
  echo "============================================================"
  echo "mps: ${mps}"
  echo "trace: ${trace_dir}"

  if [ ! -f "${mps}" ]; then
    echo "MISSING_MPS ${mps}" | tee "${log}"
    echo "127" > "${exitcode}"
    continue
  fi

  set +e
  ROCR_VISIBLE_DEVICES="${GPU_ID}" \
  timeout "${CASE_TIMEOUT_SEC}" \
  rocprofv3 \
    --runtime-trace \
    --output-format csv \
    --output-directory "${trace_dir}" \
    --output-file trace \
    -- "${PLC}" \
      -fname "${mps}" \
      -out "${json}" \
      -nIterLim "${NITER_LIM}" \
      -dTimeLim "${SOLVER_TIME_LIMIT}" \
    > "${log}" 2>&1
  code=$?
  set -e

  echo "${code}" > "${exitcode}"
  echo "exit=${code}"

  find "${trace_dir}" -maxdepth 3 -type f | sort > "${case_dir}/trace_files.txt" || true
done

echo
echo "== summarize compact trace outputs =="
python3 scripts/summarize_rocprofv3_milestones.py "${RESULT_ROOT}"

echo "${RESULT_ROOT}" > validation/results/latest_w7900_p10_current_targeted_rocprof.txt

echo
echo "== compact outputs =="
ls -lh \
  "${RESULT_ROOT}/trace_summary_by_run.csv" \
  "${RESULT_ROOT}/trace_kernel_top.csv" \
  "${RESULT_ROOT}/trace_hip_api_top.csv" \
  "${RESULT_ROOT}/trace_memory_copy_top.csv" \
  "${RESULT_ROOT}/trace_milestone_deltas.csv" \
  "${RESULT_ROOT}/trace_milestone_summary.md"

echo
echo "RESULT_ROOT=${RESULT_ROOT}"
