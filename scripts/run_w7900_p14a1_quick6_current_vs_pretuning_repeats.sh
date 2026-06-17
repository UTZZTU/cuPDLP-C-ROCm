#!/usr/bin/env bash
set -euo pipefail

SRC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
BASE_ROOT="${BASE_ROOT:-/app/cupdlp_w7900/results/w7900_p14a1_quick6_current_vs_pretuning_${STAMP}}"
WORK_ROOT="${BASE_ROOT}/worktrees"
RESULT_ROOT="${BASE_ROOT}/runs"
MPS_CACHE="${BASE_ROOT}/mps_cache"
LOG_ROOT="${BASE_ROOT}/logs"

CASES=(afiro sc50b lotfi 80bau3b maros-r7 pilot87)
REPEATS="${REPEATS:-3}"
GPU_ID="${GPU_ID:-0}"
NITER="${NITER:-200000000}"
DTIMELIM="${DTIMELIM:-600}"
TIMEOUT_SEC="${TIMEOUT_SEC:-720}"

CURRENT_REF="${CURRENT_REF:-HEAD}"
PRE_REF="${PRE_REF:-ae3b683}"

mkdir -p "${WORK_ROOT}" "${RESULT_ROOT}" "${MPS_CACHE}" "${LOG_ROOT}"

echo "[INFO] SRC_ROOT=${SRC_ROOT}"
echo "[INFO] BASE_ROOT=${BASE_ROOT}"
echo "[INFO] CURRENT_REF=${CURRENT_REF}"
echo "[INFO] PRE_REF=${PRE_REF}"
echo "[INFO] REPEATS=${REPEATS}"
echo "[INFO] GPU_ID=${GPU_ID}"

if [[ -f /app/cupdlp_w7900/activate_w7900.sh ]]; then
  # shellcheck disable=SC1091
  source /app/cupdlp_w7900/activate_w7900.sh
fi

if [[ -z "${HIGHS_HOME:-}" ]]; then
  for p in \
    /app/cupdlp_w7900/deps/install/highs-1.6.0 \
    /root/cupdlp_w7900/deps/install/highs-1.6.0
  do
    if [[ -d "$p" ]]; then
      export HIGHS_HOME="$p"
      break
    fi
  done
fi

if [[ -z "${HIGHS_HOME:-}" || ! -d "${HIGHS_HOME}" ]]; then
  echo "[ERR] HIGHS_HOME is not set or invalid: ${HIGHS_HOME:-<unset>}" >&2
  exit 2
fi

echo "[INFO] HIGHS_HOME=${HIGHS_HOME}"
echo "[INFO] hipcc=$(command -v hipcc || true)"

ROCM_INCLUDE="${ROCM_INCLUDE:-}"
if [[ -z "${ROCM_INCLUDE}" ]]; then
  for inc in \
    /opt/python/lib/python3.12/site-packages/_rocm_sdk_devel/include \
    /opt/python/include \
    /opt/rocm/include
  do
    if [[ -f "${inc}/hipblas/hipblas.h" ]]; then
      ROCM_INCLUDE="${inc}"
      break
    fi
  done
fi

if [[ -z "${ROCM_INCLUDE}" || ! -f "${ROCM_INCLUDE}/hipblas/hipblas.h" ]]; then
  echo "[ERR] cannot find hipblas/hipblas.h; set ROCM_INCLUDE manually" >&2
  find /opt/python /opt/rocm -path "*/hipblas/hipblas.h" -print 2>/dev/null | head -20 >&2 || true
  exit 5
fi

export CPATH="${ROCM_INCLUDE}:${CPATH:-}"
COMMON_ROCM_INCLUDE_FLAG="-I${ROCM_INCLUDE}"
echo "[INFO] ROCM_INCLUDE=${ROCM_INCLUDE}"

git -C "${SRC_ROOT}" rev-parse --verify "${CURRENT_REF}^{commit}" >/dev/null
git -C "${SRC_ROOT}" rev-parse --verify "${PRE_REF}^{commit}" >/dev/null

echo "[INFO] current commit: $(git -C "${SRC_ROOT}" rev-parse "${CURRENT_REF}^{commit}")"
echo "[INFO] pre_tuning commit: $(git -C "${SRC_ROOT}" rev-parse "${PRE_REF}^{commit}")"

git -C "${SRC_ROOT}" worktree add --detach "${WORK_ROOT}/current" "${CURRENT_REF}"
git -C "${SRC_ROOT}" worktree add --detach "${WORK_ROOT}/pre_tuning" "${PRE_REF}"

find_mps() {
  local case_name="$1"
  local roots=(
    "/app/cupdlp_w7900/datasets/netlib_quick6_mps"
    "${SRC_ROOT}"
    "/app/cupdlp_w7900/datasets"
    "/app/cupdlp_w7900"
    "/root/cupdlp_w7900/datasets"
    "/root/cupdlp_w7900"
  )

  for r in "${roots[@]}"; do
    [[ -e "$r" ]] || continue
    local hit
    hit="$(find "$r" -type f \( -iname "${case_name}.mps" -o -iname "${case_name}.mps.gz" \) 2>/dev/null | head -1 || true)"
    if [[ -n "$hit" ]]; then
      echo "$hit"
      return 0
    fi
  done

  return 1
}

declare -A MPS_PATHS
echo "case,path" > "${BASE_ROOT}/case_paths.csv"

for c in "${CASES[@]}"; do
  p="$(find_mps "$c" || true)"
  if [[ -z "$p" ]]; then
    echo "[ERR] cannot find MPS for case=${c}" >&2
    exit 3
  fi

  if [[ "$p" == *.gz ]]; then
    out="${MPS_CACHE}/${c}.mps"
    gzip -dc "$p" > "$out"
    p="$out"
  fi

  MPS_PATHS["$c"]="$p"
  echo "${c},${p}" >> "${BASE_ROOT}/case_paths.csv"
  echo "[OK] ${c}: ${p}"
done

build_one() {
  local label="$1"
  local dir="$2"
  local build_dir="${dir}/build-rocm-w7900"

  echo "[BUILD] ${label}: ${dir}"
  (
    cd "$dir"
    # Skip submodule initialization for P14-A1.
    # This benchmark only builds/runs the C/C++ plc executable; pycupdlp/pybind11
    # is not needed and may be slow or unavailable on temporary W7900 machines.
    # Set INIT_SUBMODULES=1 only if a future workflow needs Python bindings.
    if [[ "${INIT_SUBMODULES:-0}" == "1" ]]; then
      git submodule update --init --recursive || true
    fi

    cmake -S . -B "${build_dir}" -G Ninja \
      -DBUILD_ROCM=ON \
      -DCMAKE_BUILD_TYPE=Release \
      -DHIGHS_HOME="${HIGHS_HOME}" \
      -DROCM_PATH=/opt/python \
      -DHIP_HIPCC_EXECUTABLE=/opt/python/bin/hipcc \
      -DCMAKE_HIP_ARCHITECTURES=gfx1100 \
      -DCMAKE_C_FLAGS="${COMMON_ROCM_INCLUDE_FLAG}" \
      -DCMAKE_CXX_FLAGS="${COMMON_ROCM_INCLUDE_FLAG}" \
      -DCMAKE_HIP_FLAGS="${COMMON_ROCM_INCLUDE_FLAG}" \
      2>&1 | tee "${LOG_ROOT}/build_${label}_cmake.log"

    ninja -C "${build_dir}" \
      2>&1 | tee "${LOG_ROOT}/build_${label}_ninja.log"
  )

  if [[ ! -x "${build_dir}/bin/plc" ]]; then
    echo "[ERR] missing executable: ${build_dir}/bin/plc" >&2
    exit 4
  fi

  echo "[OK] built ${label}: ${build_dir}/bin/plc"
}

build_one current "${WORK_ROOT}/current"
build_one pre_tuning "${WORK_ROOT}/pre_tuning"

run_one() {
  local label="$1"
  local bin="$2"
  local case_name="$3"
  local rep="$4"
  local mps="${MPS_PATHS[$case_name]}"
  local outdir="${RESULT_ROOT}/${label}/${case_name}/rep_${rep}"

  mkdir -p "$outdir"

  echo "[RUN] label=${label} case=${case_name} rep=${rep}"
  echo "label=${label}" > "${outdir}/meta.txt"
  echo "case=${case_name}" >> "${outdir}/meta.txt"
  echo "rep=${rep}" >> "${outdir}/meta.txt"
  echo "mps=${mps}" >> "${outdir}/meta.txt"
  echo "bin=${bin}" >> "${outdir}/meta.txt"
  echo "nIterLim=${NITER}" >> "${outdir}/meta.txt"
  echo "dTimeLim=${DTIMELIM}" >> "${outdir}/meta.txt"

  set +e
  ROCR_VISIBLE_DEVICES="${GPU_ID}" \
  timeout "${TIMEOUT_SEC}" \
  "${bin}" \
    -fname "${mps}" \
    -out "${outdir}/${case_name}_${label}_rep${rep}.json" \
    -nIterLim "${NITER}" \
    -dTimeLim "${DTIMELIM}" \
    2>&1 | tee "${outdir}/${case_name}_${label}_rep${rep}.log"

  rc="${PIPESTATUS[0]}"
  set -e

  echo "exit=${rc}" | tee "${outdir}/${case_name}_${label}_rep${rep}.exit"
}

CURRENT_BIN="${WORK_ROOT}/current/build-rocm-w7900/bin/plc"
PRE_BIN="${WORK_ROOT}/pre_tuning/build-rocm-w7900/bin/plc"

for rep in $(seq 1 "${REPEATS}"); do
  for c in "${CASES[@]}"; do
    run_one pre_tuning "${PRE_BIN}" "$c" "$rep"
    run_one current "${CURRENT_BIN}" "$c" "$rep"
  done
done

mkdir -p "${SRC_ROOT}/validation/results"
echo "${BASE_ROOT}" > "${SRC_ROOT}/validation/results/latest_w7900_p14a1_quick6_current_vs_pretuning.txt"

echo "[DONE] result root: ${BASE_ROOT}"
echo "[DONE] latest pointer: validation/results/latest_w7900_p14a1_quick6_current_vs_pretuning.txt"
