#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

if [ -f /app/cupdlp_w7900/activate_w7900.sh ]; then
  # shellcheck disable=SC1091
  source /app/cupdlp_w7900/activate_w7900.sh
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
RESULT_ROOT="${RESULT_ROOT:-/app/cupdlp_w7900/results/w7900_p11_spmv_alg_sweep_${STAMP}}"
GPU_ID="${GPU_ID:-0}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
SOLVER_TIME_LIMIT="${SOLVER_TIME_LIMIT:-300}"
NITER_LIM="${NITER_LIM:-1000000000}"

PLC="${PLC:-build-rocm-w7900/bin/plc}"

if [ ! -x "${PLC}" ]; then
  echo "ERROR: missing executable ${PLC}" >&2
  echo "Run: bash scripts/build_w7900_rocm.sh" >&2
  exit 1
fi

MPS_ROOT="${MPS_ROOT:-}"
if [ -z "${MPS_ROOT}" ]; then
  FOUND="$(find /app/cupdlp_w7900/datasets -type f -name 'set-cover-model.mps' | head -1 || true)"
  if [ -z "${FOUND}" ]; then
    echo "ERROR: cannot find set-cover-model.mps under /app/cupdlp_w7900/datasets" >&2
    exit 1
  fi
  MPS_ROOT="$(dirname "${FOUND}")"
fi

CASES=(
  "L2CTA3D"
  "set-cover-model"
  "square41"
  "thk_48"
  "tpl-tub-ws1617"
)

MODES=(
  "csr_alg2"
  "env_default"
  "csr_alg1"
)

mkdir -p "${RESULT_ROOT}"

{
  echo "== W7900 P11 SpMV algorithm sweep =="
  echo "date: $(date)"
  echo "repo: ${ROOT}"
  echo "commit: $(git rev-parse --short HEAD)"
  echo "result root: ${RESULT_ROOT}"
  echo "mps root: ${MPS_ROOT}"
  echo "plc: ${PLC}"
  echo "gpu: ROCR_VISIBLE_DEVICES=${GPU_ID}"
  echo "case timeout sec: ${CASE_TIMEOUT_SEC}"
  echo "solver dTimeLim: ${SOLVER_TIME_LIMIT}"
  echo "nIterLim: ${NITER_LIM}"
  echo
  echo "== cases =="
  printf "%s\n" "${CASES[@]}"
  echo
  echo "== modes =="
  printf "%s\n" "${MODES[@]}"
} > "${RESULT_ROOT}/run_env.txt"

for case in "${CASES[@]}"; do
  mps="${MPS_ROOT}/${case}.mps"
  if [ ! -f "${mps}" ]; then
    echo "ERROR: missing MPS ${mps}" >&2
    exit 1
  fi
done

for mode in "${MODES[@]}"; do
  for case in "${CASES[@]}"; do
    case_dir="${RESULT_ROOT}/${mode}/${case}"
    mkdir -p "${case_dir}"

    log="${case_dir}/${case}_${mode}.log"
    json="${case_dir}/${case}_${mode}.json"
    exit_file="${case_dir}/${case}_${mode}.exit"

    echo
    echo "============================================================"
    echo "mode=${mode} case=${case}"
    echo "============================================================"

    set +e
    if [ "${mode}" = "csr_alg2" ]; then
      ROCR_VISIBLE_DEVICES="${GPU_ID}" \
      timeout "${CASE_TIMEOUT_SEC}" \
      "${PLC}" \
        -fname "${MPS_ROOT}/${case}.mps" \
        -out "${json}" \
        -nIterLim "${NITER_LIM}" \
        -dTimeLim "${SOLVER_TIME_LIMIT}" \
        > "${log}" 2>&1
      code=$?
    elif [ "${mode}" = "env_default" ]; then
      ROCR_VISIBLE_DEVICES="${GPU_ID}" \
      CUPDLP_HIP_SPMV_ALG=default \
      timeout "${CASE_TIMEOUT_SEC}" \
      "${PLC}" \
        -fname "${MPS_ROOT}/${case}.mps" \
        -out "${json}" \
        -nIterLim "${NITER_LIM}" \
        -dTimeLim "${SOLVER_TIME_LIMIT}" \
        > "${log}" 2>&1
      code=$?
    elif [ "${mode}" = "csr_alg1" ]; then
      ROCR_VISIBLE_DEVICES="${GPU_ID}" \
      CUPDLP_HIP_SPMV_ALG=csr_alg1 \
      timeout "${CASE_TIMEOUT_SEC}" \
      "${PLC}" \
        -fname "${MPS_ROOT}/${case}.mps" \
        -out "${json}" \
        -nIterLim "${NITER_LIM}" \
        -dTimeLim "${SOLVER_TIME_LIMIT}" \
        > "${log}" 2>&1
      code=$?
    else
      echo "ERROR: unknown mode ${mode}" >&2
      code=125
    fi
    set -e

    echo "exit=${code}" > "${exit_file}"
    echo "exit=${code}"

    grep -Ei "Solving information|Number of iterations|Total solver time|Solve time|Primal objective|Dual objective|Primal infeas|Dual infeas|Duality gap|Iters per sec|UpdateIterates" "${log}" \
      > "${case_dir}/${case}_${mode}.summary.txt" || true
  done
done

echo "${RESULT_ROOT}" > /app/cupdlp_w7900/results/latest_w7900_p11_spmv_alg_sweep.txt

echo
echo "RESULT_ROOT=${RESULT_ROOT}"
echo "latest pointer: /app/cupdlp_w7900/results/latest_w7900_p11_spmv_alg_sweep.txt"
