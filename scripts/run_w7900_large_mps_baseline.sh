#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
DATA_ROOT="${DATA_ROOT:-/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark}"
MPS_DIR="${MPS_DIR:-${DATA_ROOT}/mps}"
CASE_LIST="${CASE_LIST:-${REPO_ROOT}/validation/cases_w7900_large_mps_initial17_safe.txt}"

ITER_LIMIT="${ITER_LIMIT:-1000000000}"
TIME_LIMIT="${TIME_LIMIT:-7200}"
EXTERNAL_TIMEOUT="${EXTERNAL_TIMEOUT:-7500}"
HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES:-0}"

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ROOT="${OUT_ROOT:-${WORK_ROOT}/results/w7900_large_mps_baseline_${STAMP}}"
LOG_DIR="${OUT_ROOT}/logs"
JSON_DIR="${OUT_ROOT}/json"

mkdir -p "${OUT_ROOT}" "${LOG_DIR}" "${JSON_DIR}" "${WORK_ROOT}/logs"

cd "${REPO_ROOT}"

if [[ -f "${WORK_ROOT}/activate_w7900.sh" ]]; then
  source "${WORK_ROOT}/activate_w7900.sh"
fi

PLC="${REPO_ROOT}/build-rocm-w7900/bin/plc"

if [[ ! -x "${PLC}" ]]; then
  echo "[error] ROCm plc not found: ${PLC}" >&2
  echo "Run bootstrap or ./scripts/build_w7900_rocm.sh first." >&2
  exit 1
fi

if [[ ! -f "${CASE_LIST}" ]]; then
  echo "[error] case list not found: ${CASE_LIST}" >&2
  exit 1
fi

if [[ ! -d "${MPS_DIR}" ]]; then
  echo "[error] MPS dir not found: ${MPS_DIR}" >&2
  exit 1
fi

COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
SUMMARY="${OUT_ROOT}/runtime_summary.csv"

cat > "${OUT_ROOT}/run_info.txt" <<EOF
W7900 large-MPS baseline run
timestamp=${STAMP}
repo=${REPO_ROOT}
commit=${COMMIT}
data_root=${DATA_ROOT}
mps_dir=${MPS_DIR}
case_list=${CASE_LIST}
backend=ROCm/HIP
device=W7900/gfx1100
HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES}
ITER_LIMIT=${ITER_LIMIT}
TIME_LIMIT=${TIME_LIMIT}
EXTERNAL_TIMEOUT=${EXTERNAL_TIMEOUT}
primary_metric=solver JSON dSolvingTime plus external wall time
EOF

echo "case,status,exit_code,wall_seconds,json,log" > "${SUMMARY}"

echo "[info] output: ${OUT_ROOT}"
echo "[info] case list: ${CASE_LIST}"
echo "[info] limits: nIterLim=${ITER_LIMIT}, dTimeLim=${TIME_LIMIT}, external timeout=${EXTERNAL_TIMEOUT}"
echo "[info] HIP_VISIBLE_DEVICES=${HIP_VISIBLE_DEVICES}"

while IFS= read -r case_name; do
  [[ -z "${case_name}" ]] && continue
  [[ "${case_name}" =~ ^# ]] && continue

  mps="${MPS_DIR}/${case_name}"
  base="${case_name%.mps}"
  json="${JSON_DIR}/${base}.json"
  log="${LOG_DIR}/${base}.log"

  if [[ ! -f "${mps}" ]]; then
    echo "[warn] missing ${mps}"
    echo "${case_name},MISSING,999,0,${json},${log}" >> "${SUMMARY}"
    continue
  fi

  echo
  echo "============================================================"
  echo "[case] ${case_name}"
  echo "============================================================"

  start="$(date +%s.%N)"
  set +e
  HIP_VISIBLE_DEVICES="${HIP_VISIBLE_DEVICES}" timeout --foreground "${EXTERNAL_TIMEOUT}s" \
    "${PLC}" \
      -fname "${mps}" \
      -out "${json}" \
      -nIterLim "${ITER_LIMIT}" \
      -dTimeLim "${TIME_LIMIT}" \
    2>&1 | tee "${log}"
  rc="${PIPESTATUS[0]}"
  set -e
  end="$(date +%s.%N)"

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

  echo "${case_name},${status},${rc},${wall},${json},${log}" >> "${SUMMARY}"
  echo "[done] ${case_name}: status=${status}, rc=${rc}, wall=${wall}s"

done < "${CASE_LIST}"

echo
echo "[done] W7900 large-MPS baseline finished"
echo "[done] output: ${OUT_ROOT}"
echo "[done] summary: ${SUMMARY}"
