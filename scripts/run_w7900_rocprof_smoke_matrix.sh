#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
DATA_ROOT="${DATA_ROOT:-/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark}"
MPS_DIR="${MPS_DIR:-${DATA_ROOT}/mps}"

CASE_LIST="${CASE_LIST:-${REPO_ROOT}/validation/cases_w7900_rocprof_starter3.txt}"
RUN_TAG="${RUN_TAG:-w7900_rocprof_starter3}"
ITER_LIMIT="${ITER_LIMIT:-1000000000}"
TIME_LIMIT="${TIME_LIMIT:-900}"
EXTERNAL_TIMEOUT="${EXTERNAL_TIMEOUT:-960}"
HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${OUT_ROOT:-${WORK_ROOT}/results/w7900_rocprof/${RUN_TAG}_${STAMP}}"
LOG_DIR="${OUT_ROOT}/logs"
JSON_DIR="${OUT_ROOT}/json"
PROF_DIR="${OUT_ROOT}/profiler"
SMI_DIR="${OUT_ROOT}/smi"

mkdir -p "${LOG_DIR}" "${JSON_DIR}" "${PROF_DIR}" "${SMI_DIR}"

cd "${REPO_ROOT}"

if [[ -f "${WORK_ROOT}/activate_w7900.sh" ]]; then
  source "${WORK_ROOT}/activate_w7900.sh"
fi

PLC="${REPO_ROOT}/build-rocm-w7900/bin/plc"

if [[ ! -x "${PLC}" ]]; then
  echo "[error] plc not found: ${PLC}" >&2
  echo "Run bootstrap/build first." >&2
  exit 1
fi

if [[ ! -f "${CASE_LIST}" ]]; then
  echo "[info] creating starter case list: ${CASE_LIST}"
  cat > "${CASE_LIST}" <<'EOF'
set-cover-model.mps
square41.mps
s100.mps
EOF
fi

echo "case,status,exit_code,wall_seconds,json,log,profiler_dir" > "${OUT_ROOT}/runtime_summary.csv"

{
  echo "repo=${REPO_ROOT}"
  echo "out_root=${OUT_ROOT}"
  echo "case_list=${CASE_LIST}"
  echo "HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES}"
  echo "ITER_LIMIT=${ITER_LIMIT}"
  echo "TIME_LIMIT=${TIME_LIMIT}"
  echo "EXTERNAL_TIMEOUT=${EXTERNAL_TIMEOUT}"
  echo
  echo "== tools =="
  command -v rocprofv3 rocprof rocm-smi amd-smi hipcc || true
  echo
  echo "== git =="
  git rev-parse HEAD || true
} | tee "${OUT_ROOT}/run_info.txt"

PROFILE_TOOL=""
if command -v rocprofv3 >/dev/null 2>&1; then
  PROFILE_TOOL="rocprofv3"
elif command -v rocprof >/dev/null 2>&1; then
  PROFILE_TOOL="rocprof"
fi

echo "[info] profiling tool: ${PROFILE_TOOL:-none}"

while IFS= read -r case_name; do
  [[ -z "${case_name}" ]] && continue
  [[ "${case_name}" =~ ^# ]] && continue

  base="${case_name%.mps}"
  mps="${MPS_DIR}/${case_name}"
  json="${JSON_DIR}/${base}.json"
  log="${LOG_DIR}/${base}.log"
  case_prof="${PROF_DIR}/${base}"

  if [[ ! -f "${mps}" ]]; then
    echo "[warn] missing ${mps}"
    echo "${case_name},MISSING,999,0,${json},${log},${case_prof}" >> "${OUT_ROOT}/runtime_summary.csv"
    continue
  fi

  mkdir -p "${case_prof}"

  echo
  echo "============================================================"
  echo "[case] ${case_name}"
  echo "============================================================"

  if command -v rocm-smi >/dev/null 2>&1; then
    rocm-smi > "${SMI_DIR}/${base}_before.txt" 2>&1 || true
  elif command -v amd-smi >/dev/null 2>&1; then
    amd-smi static > "${SMI_DIR}/${base}_before.txt" 2>&1 || true
  fi

  start="$(date +%s.%N)"
  set +e

  if [[ "${PROFILE_TOOL}" == "rocprofv3" ]]; then
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      rocprofv3 --stats --hip-trace --kernel-trace --output-format csv --output-directory "${case_prof}" -- \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee "${log}"
    rc="${PIPESTATUS[0]}"
  elif [[ "${PROFILE_TOOL}" == "rocprof" ]]; then
    echo "[warn] legacy rocprof detected. Running without rocprof command until local syntax is confirmed." | tee "${log}"
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee -a "${log}"
    rc="${PIPESTATUS[0]}"
  else
    echo "[warn] no profiler detected. Running baseline only." | tee "${log}"
    HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
      "${PLC}" -fname "${mps}" -out "${json}" -nIterLim "${ITER_LIMIT}" -dTimeLim "${TIME_LIMIT}" \
      2>&1 | tee -a "${log}"
    rc="${PIPESTATUS[0]}"
  fi

  set -e
  end="$(date +%s.%N)"

  if command -v rocm-smi >/dev/null 2>&1; then
    rocm-smi > "${SMI_DIR}/${base}_after.txt" 2>&1 || true
  elif command -v amd-smi >/dev/null 2>&1; then
    amd-smi static > "${SMI_DIR}/${base}_after.txt" 2>&1 || true
  fi

  wall="$(python3 - <<PY
start = float("${start}")
end = float("${end}")
print(f"{end - start:.6f}")
PY
)"

  if [[ "${rc}" == "0" ]]; then
    status="DONE"
  elif [[ "${rc}" == "124" ]]; then
    status="TIMEOUT"
  else
    status="ERROR"
  fi

  echo "${case_name},${status},${rc},${wall},${json},${log},${case_prof}" >> "${OUT_ROOT}/runtime_summary.csv"
  echo "[done] ${case_name}: status=${status}, rc=${rc}, wall=${wall}s"

done < "${CASE_LIST}"

echo
echo "[done] profiling matrix finished"
echo "[done] output: ${OUT_ROOT}"
echo "[done] runtime summary: ${OUT_ROOT}/runtime_summary.csv"
