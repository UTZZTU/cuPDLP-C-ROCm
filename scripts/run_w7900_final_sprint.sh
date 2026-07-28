#!/usr/bin/env bash
set -Eeuo pipefail

# Integrated W7900 final-sprint experiment runner, v2.
#
# Required public modes:
#   status
#   mini          - qap15 full-path validation: baseline + 3 tolerances + profile
#   pilot         - representative two-case validation
#   all           - baseline23 + precision + profile + throughput
#   baseline23    - authoritative non-hard23, repeat-major order
#   precision     - five cases x three tolerances, repeat-major order
#   profile       - five targeted rocprofv3 traces
#   throughput    - derive single-card throughput and preserve 8-card boundary
#   archive       - reparse/rearchive RUN_ROOT
#   resume [MODE] - continue an existing RUN_ROOT; reads planned mode if omitted
#
# Convenience aliases:
#   session1 -> baseline23
#   session2 -> precision followed by profile

REQUESTED_MODE="${1:-status}"
RESUME_TARGET="${2:-}"

case "${REQUESTED_MODE}" in
  status|mini|pilot|all|baseline23|precision|profile|throughput|archive|resume|session1|session2) ;;
  *)
    echo "Usage: $0 [status|mini|pilot|all|baseline23|precision|profile|throughput|archive|resume [MODE]|session1|session2]" >&2
    exit 2
    ;;
esac

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
REPO_DIR="${REPO_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
DATA_ROOT="${DATA_ROOT:-${WORK_ROOT}/datasets/large_mps_baidu/cupdlp-large-mps-benchmark}"
MPS_DIR="${MPS_DIR:-${DATA_ROOT}/mps}"
GPU_ID="${GPU_ID:-0}"
SAMPLE_INTERVAL="${SAMPLE_INTERVAL:-1}"
SOLVER_BASELINE_COMMIT="${SOLVER_BASELINE_COMMIT:-735764807d8698ff30811d1a6fcc45d4a3fd4817}"
EXPECTED_BRANCH="${EXPECTED_BRANCH:-rocm-w7900-gfx1100}"

BASELINE_REPEATS="${BASELINE_REPEATS:-2}"
PRECISION_REPEATS="${PRECISION_REPEATS:-2}"
PRECISION_LEVELS="${PRECISION_LEVELS:-1e-3 1e-4 1e-5}"

BASELINE_TIME_LIMIT="${BASELINE_TIME_LIMIT:-1800}"
BASELINE_EXTERNAL_TIMEOUT="${BASELINE_EXTERNAL_TIMEOUT:-1860}"
PRECISION_TIME_LIMIT="${PRECISION_TIME_LIMIT:-900}"
PRECISION_EXTERNAL_TIMEOUT="${PRECISION_EXTERNAL_TIMEOUT:-960}"
PROFILE_SOLVER_TIME_LIMIT="${PROFILE_SOLVER_TIME_LIMIT:-300}"
PROFILE_EXTERNAL_TIMEOUT="${PROFILE_EXTERNAL_TIMEOUT:-900}"
PROFILE_MAX_BYTES="${PROFILE_MAX_BYTES:-8589934592}"

WINDOW_MINUTES="${WINDOW_MINUTES:-180}"
RESERVE_MINUTES="${RESERVE_MINUTES:-35}"
CREATE_ARCHIVE="${CREATE_ARCHIVE:-1}"
RERUN_TIMEOUTS="${RERUN_TIMEOUTS:-0}"
PILOT_PROFILE="${PILOT_PROFILE:-1}"
OFFICIAL_REQUIRE_CLEAN="${OFFICIAL_REQUIRE_CLEAN:-1}"

[[ -n "${REPO_DIR}" && -d "${REPO_DIR}/.git" ]] || {
  echo "[ERROR] run from a cloned cuPDLP-C-ROCm repository" >&2
  exit 1
}

cd "${REPO_DIR}"
SHORT_SHA="$(git rev-parse --short=12 HEAD)"
STAMP="$(date +%Y%m%d_%H%M%S)"
HOST="$(hostname)"

PLAN_MODE="${REQUESTED_MODE}"
case "${PLAN_MODE}" in
  session1) PLAN_MODE="baseline23" ;;
  session2) PLAN_MODE="session2" ;;
esac

if [[ "${REQUESTED_MODE}" == "archive" || "${REQUESTED_MODE}" == "resume" || "${REQUESTED_MODE}" == "throughput" ]]; then
  if [[ -z "${RUN_ROOT:-}" ]]; then
    if [[ "${REQUESTED_MODE}" == "throughput" ]]; then
      echo "[ERROR] throughput mode requires RUN_ROOT=/existing/run/path" >&2
    else
      echo "[ERROR] ${REQUESTED_MODE} mode requires RUN_ROOT=/existing/run/path" >&2
    fi
    exit 2
  fi
fi

if [[ "${REQUESTED_MODE}" == "resume" ]]; then
  [[ -d "${RUN_ROOT}" ]] || {
    echo "[ERROR] RUN_ROOT does not exist: ${RUN_ROOT}" >&2
    exit 1
  }
  if [[ -n "${RESUME_TARGET}" ]]; then
    PLAN_MODE="${RESUME_TARGET}"
  else
    PLAN_MODE="$(python3 - "${RUN_ROOT}/00_manifest/run_manifest.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
if not p.exists():
    raise SystemExit(2)
print(json.loads(p.read_text()).get("planned_mode", ""))
PY
)" || true
    [[ -n "${PLAN_MODE}" ]] || {
      echo "[ERROR] cannot determine planned mode; use: resume MODE" >&2
      exit 2
    }
  fi
fi

case "${PLAN_MODE}" in
  mini|pilot|all|baseline23|precision|profile|session2) ;;
  status|archive|throughput) ;;
  *)
    echo "[ERROR] invalid plan mode: ${PLAN_MODE}" >&2
    exit 2
    ;;
esac

RUN_ROOT="${RUN_ROOT:-${WORK_ROOT}/results/final_sprint/${STAMP}_${SHORT_SHA}_${HOST}_${PLAN_MODE}}"
MANIFEST_DIR="${RUN_ROOT}/00_manifest"
SMOKE_DIR="${RUN_ROOT}/01_smoke"
BASELINE_DIR="${RUN_ROOT}/02_baseline23"
PRECISION_DIR="${RUN_ROOT}/03_precision"
PROFILE_DIR="${RUN_ROOT}/04_profile"
THROUGHPUT_DIR="${RUN_ROOT}/05_throughput"
RAW_DIR="${RUN_ROOT}/raw"
PARSED_DIR="${RUN_ROOT}/parsed"
LOG_DIR="${RUN_ROOT}/logs"
COMMANDS_TSV="${MANIFEST_DIR}/commands.tsv"

SESSION_START_EPOCH="$(date +%s)"
SAMPLER_PID=""
STOP_REQUESTED=0

msg() {
  echo
  echo "============================================================"
  echo "$*"
  echo "============================================================"
}

die() {
  echo "[ERROR] $*" >&2
  echo "run_root=${RUN_ROOT}" >&2
  exit 1
}

cleanup_sampler() {
  if [[ -n "${SAMPLER_PID}" ]]; then
    kill "${SAMPLER_PID}" 2>/dev/null || true
    wait "${SAMPLER_PID}" 2>/dev/null || true
    SAMPLER_PID=""
  fi
}
trap cleanup_sampler EXIT INT TERM

remaining_seconds() {
  local now elapsed total
  now="$(date +%s)"
  elapsed=$((now - SESSION_START_EPOCH))
  total=$((WINDOW_MINUTES * 60))
  echo $((total - elapsed))
}

budget_allows() {
  local estimate="$1"
  local remaining reserve
  remaining="$(remaining_seconds)"
  reserve=$((RESERVE_MINUTES * 60))
  echo "[budget] remaining=${remaining}s reserve=${reserve}s next_estimate=${estimate}s"
  (( remaining > reserve + estimate ))
}

request_stop() {
  STOP_REQUESTED=1
  echo "[stop] $*"
}

require_budget_or_stop() {
  local estimate="$1"
  local label="$2"
  if ! budget_allows "${estimate}"; then
    request_stop "insufficient safe time before ${label}; preserve reserve for parse/archive/export"
    return 1
  fi
  return 0
}

verify_solver_state() {
  local official="$1"
  cd "${REPO_DIR}"

  [[ "$(git branch --show-current)" == "${EXPECTED_BRANCH}" ]] \
    || die "expected branch ${EXPECTED_BRANCH}"

  if ! git cat-file -e "${SOLVER_BASELINE_COMMIT}^{commit}" 2>/dev/null; then
    git fetch --no-tags origin "${SOLVER_BASELINE_COMMIT}"
  fi

  local solver_paths=(CMakeLists.txt cmake cupdlp interface)
  git diff --quiet "${SOLVER_BASELINE_COMMIT}" HEAD -- "${solver_paths[@]}" \
    || die "committed solver source differs from frozen baseline"
  git diff --quiet -- "${solver_paths[@]}" \
    || die "working-tree solver source differs from frozen baseline"
  git diff --cached --quiet -- "${solver_paths[@]}" \
    || die "staged solver source differs from frozen baseline"

  if [[ "${official}" == "1" && "${OFFICIAL_REQUIRE_CLEAN}" == "1" ]]; then
    [[ -z "$(git status --porcelain=v1)" ]] \
      || die "official experiment requires a clean committed working tree"
  fi
}

source_environment() {
  [[ -f "${WORK_ROOT}/activate_w7900.sh" ]] \
    || die "activation script missing; run prepare script"
  # shellcheck disable=SC1090
  source "${WORK_ROOT}/activate_w7900.sh"

  PLC="${REPO_DIR}/build-rocm-w7900/bin/plc"
  [[ -x "${PLC}" ]] || die "ROCm plc missing: ${PLC}"
  [[ -x /usr/bin/time ]] || die "/usr/bin/time missing"
  command -v rocm-smi >/dev/null 2>&1 || die "rocm-smi missing"
}

create_directories() {
  mkdir -p \
    "${MANIFEST_DIR}" \
    "${SMOKE_DIR}" \
    "${BASELINE_DIR}" \
    "${PRECISION_DIR}" \
    "${PROFILE_DIR}" \
    "${THROUGHPUT_DIR}" \
    "${RAW_DIR}" \
    "${PARSED_DIR}" \
    "${LOG_DIR}"

  if [[ ! -f "${COMMANDS_TSV}" ]]; then
    printf 'timestamp\tgroup\tcase\ttolerance\trepeat\tgpu_id\tcommand_file\tstatus_file\n' \
      > "${COMMANDS_TSV}"
  fi
}

copy_smoke_evidence() {
  if find "${SMOKE_DIR}" -type f -print -quit 2>/dev/null | grep -q .; then
    return 0
  fi

  local latest_smoke
  latest_smoke="$(
    find "${WORK_ROOT}/results" -maxdepth 1 -type d -name 'w7900_smoke_*' \
      -printf '%T@ %p\n' 2>/dev/null \
      | sort -nr \
      | awk 'NR==1 {$1=""; sub(/^ /,""); print}'
  )"

  if [[ -n "${latest_smoke}" && -d "${latest_smoke}" ]]; then
    cp -a "${latest_smoke}/." "${SMOKE_DIR}/"
    echo "[manifest] copied smoke evidence from ${latest_smoke}"
  else
    echo "[manifest] no standalone smoke result directory found"
  fi

  find "${WORK_ROOT}/logs" -maxdepth 1 -type f \
    \( -name 'final_sprint_smoke_*.log' -o -name 'bootstrap_run_w7900_smoke.log' \) \
    -exec cp -a {} "${SMOKE_DIR}/" \; 2>/dev/null || true
}

write_manifest_once() {
  if [[ -f "${MANIFEST_DIR}/run_manifest.json" ]]; then
    echo "[resume] existing manifest: ${MANIFEST_DIR}/run_manifest.json"
    return 0
  fi

  python3 - "${MANIFEST_DIR}/run_manifest.json" <<PY
import json
from pathlib import Path
payload = {
    "schema_version": 2,
    "planned_mode": "${PLAN_MODE}",
    "run_root": "${RUN_ROOT}",
    "created_at": "$(date -Is)",
    "hostname": "$(hostname)",
    "gpu_id": "${GPU_ID}",
    "sample_interval_seconds": float("${SAMPLE_INTERVAL}"),
    "window_minutes": int("${WINDOW_MINUTES}"),
    "reserve_minutes": int("${RESERVE_MINUTES}"),
    "baseline_repeats": int("${BASELINE_REPEATS}"),
    "precision_repeats": int("${PRECISION_REPEATS}"),
    "precision_levels": "${PRECISION_LEVELS}".split(),
    "baseline_time_limit_seconds": int("${BASELINE_TIME_LIMIT}"),
    "precision_time_limit_seconds": int("${PRECISION_TIME_LIMIT}"),
    "profile_solver_time_limit_seconds": int("${PROFILE_SOLVER_TIME_LIMIT}"),
    "solver_source_baseline": "${SOLVER_BASELINE_COMMIT}",
    "harness_commit": "$(git rev-parse HEAD)",
    "branch": "$(git branch --show-current)",
    "eight_card_boundary": "independent MPS batch throughput; not distributed single-LP solving",
}
Path("${MANIFEST_DIR}/run_manifest.json").write_text(
    json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
)
PY

  git rev-parse HEAD > "${MANIFEST_DIR}/git_head.txt"
  git branch --show-current > "${MANIFEST_DIR}/git_branch.txt"
  git status --porcelain=v1 > "${MANIFEST_DIR}/git_status.txt"
  git diff > "${MANIFEST_DIR}/git_diff.patch"
  git diff --cached > "${MANIFEST_DIR}/git_cached_diff.patch"
  git submodule status --recursive > "${MANIFEST_DIR}/submodule_status.txt" 2>&1 || true

  {
    date -Is
    uname -a
    cat /etc/os-release 2>/dev/null || true
    echo
    echo "PATH=${PATH}"
    echo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-}"
    echo "CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH:-}"
  } > "${MANIFEST_DIR}/environment.txt"

  {
    echo "hipcc"
    hipcc --version 2>&1 || true
    echo
    echo "rocprofv3"
    rocprofv3 --version 2>&1 || true
    echo
    echo "rocm-smi"
    rocm-smi --version 2>&1 || true
    echo
    echo "amd-smi"
    amd-smi version 2>&1 || true
    echo
    echo "cmake"
    cmake --version 2>&1 || true
    echo
    echo "gcc"
    gcc --version 2>&1 | head -1 || true
  } > "${MANIFEST_DIR}/tool_versions.txt"

  {
    rocm_agent_enumerator 2>&1 || true
    echo
    rocm-smi --showproductname --showmeminfo vram --showuse --showpower 2>&1 || true
    echo
    amd-smi static 2>&1 || true
  } > "${MANIFEST_DIR}/gpu_inventory.txt"

  if [[ -s "${DATA_ROOT}/h100_large_mps_manifest.sha256" ]]; then
    cp -a "${DATA_ROOT}/h100_large_mps_manifest.sha256" \
      "${MANIFEST_DIR}/dataset_sha256.txt"
  fi
  if [[ -s "${DATA_ROOT}/h100_large_mps_inventory.csv" ]]; then
    cp -a "${DATA_ROOT}/h100_large_mps_inventory.csv" "${MANIFEST_DIR}/"
  fi

  copy_smoke_evidence
}

verify_dataset() {
  local scope="$1"
  bash scripts/download_w7900_large_mps.sh verify "${scope}"
}

record_command() {
  local timestamp="$1" group="$2" case_name="$3" tolerance="$4" repeat="$5"
  local command_file="$6" status_file="$7"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "${timestamp}" "${group}" "${case_name}" "${tolerance}" "${repeat}" \
    "${GPU_ID}" "${command_file}" "${status_file}" >> "${COMMANDS_TSV}"
}

start_sampler() {
  local output="$1"
  : > "${output}"

  (
    while true; do
      echo "===== sample $(date -Is) ====="
      rocm-smi -d "${GPU_ID}" \
        --showmeminfo vram \
        --showuse \
        --showmemuse \
        --showpower \
        --showtemp \
        --showclocks \
        2>&1 || true
      sleep "${SAMPLE_INTERVAL}"
    done
  ) >> "${output}" 2>&1 &

  SAMPLER_PID=$!
}

status_is_complete() {
  local status_file="$1" json_file="$2"
  [[ -s "${status_file}" ]] || return 1

  if grep -q '^runtime_status=DONE$' "${status_file}"; then
    [[ -s "${json_file}" ]]
    return
  fi

  if grep -q '^runtime_status=TIMEOUT$' "${status_file}"; then
    [[ "${RERUN_TIMEOUTS}" != "1" ]]
    return
  fi

  return 1
}

estimate_baseline_seconds() {
  case "$1" in
    Primal2_1000|s100) echo 1250 ;;
    thk_63) echo 360 ;;
    square41|tpl-tub-ws1617|thk_48) echo 190 ;;
    L2CTA3D|set-cover-model|rmine15|neos-3025225) echo 100 ;;
    qap15) echo 20 ;;
    *) echo 75 ;;
  esac
}

estimate_precision_seconds() {
  local case_name="$1" tolerance="$2" base multiplier
  case "${case_name}" in
    qap15) base=20 ;;
    L2CTA3D) base=90 ;;
    set-cover-model) base=100 ;;
    thk_48) base=190 ;;
    square41|tpl-tub-ws1617) base=210 ;;
    *) base=150 ;;
  esac

  case "${tolerance}" in
    1e-3) multiplier=1 ;;
    1e-4) multiplier=2 ;;
    1e-5) multiplier=4 ;;
    *) multiplier=3 ;;
  esac

  local estimate=$((base * multiplier + 30))
  (( estimate > PRECISION_EXTERNAL_TIMEOUT )) && estimate="${PRECISION_EXTERNAL_TIMEOUT}"
  echo "${estimate}"
}

estimate_profile_seconds() {
  case "$1" in
    qap15) echo 90 ;;
    L2CTA3D|set-cover-model) echo 180 ;;
    thk_48) echo 300 ;;
    square41|tpl-tub-ws1617) echo 360 ;;
    *) echo 300 ;;
  esac
}

run_solver_one() {
  local group="$1" case_name="$2" tolerance="$3" repeat="$4" destination="$5"
  local time_limit="$6" external_timeout="$7"

  local mps="${MPS_DIR}/${case_name}.mps"
  [[ -s "${mps}" ]] || die "MPS missing: ${mps}"
  mkdir -p "${destination}"

  local tol_tag stem json log time_log metrics command_file status_file
  tol_tag="${tolerance//./p}"
  tol_tag="${tol_tag//-/m}"
  stem="${case_name}__tol_${tol_tag}__rep_${repeat}"
  json="${destination}/${stem}.json"
  log="${destination}/${stem}.log"
  time_log="${destination}/${stem}.time.txt"
  metrics="${destination}/${stem}.rocm_smi_raw.txt"
  command_file="${destination}/${stem}.command.txt"
  status_file="${destination}/${stem}.status.env"

  if status_is_complete "${status_file}" "${json}"; then
    echo "[resume skip] ${group} ${case_name} tol=${tolerance} rep=${repeat}"
    return 0
  fi

  local cmd=(
    "${PLC}"
    -fname "${mps}"
    -out "${json}"
    -nIterLim 1000000000
    -dTimeLim "${time_limit}"
    -dPrimalTol "${tolerance}"
    -dDualTol "${tolerance}"
    -dGapTol "${tolerance}"
  )

  printf 'HIP_VISIBLE_DEVICES=%q ROCR_VISIBLE_DEVICES=%q timeout --foreground %qs /usr/bin/time -v ' \
    "${GPU_ID}" "${GPU_ID}" "${external_timeout}" > "${command_file}"
  printf '%q ' "${cmd[@]}" >> "${command_file}"
  printf '\n' >> "${command_file}"

  local start_iso start_epoch end_iso end_epoch rc wall runtime_status
  start_iso="$(date -Is)"
  start_epoch="$(date +%s.%N)"
  record_command "${start_iso}" "${group}" "${case_name}" "${tolerance}" "${repeat}" \
    "${command_file}" "${status_file}"

  echo
  echo "[run] group=${group} case=${case_name} tol=${tolerance} rep=${repeat}"
  echo "[run] mps=${mps}"

  start_sampler "${metrics}"

  set +e
  HIP_VISIBLE_DEVICES="${GPU_ID}" \
  ROCR_VISIBLE_DEVICES="${GPU_ID}" \
    timeout --foreground "${external_timeout}s" \
    /usr/bin/time -v -o "${time_log}" \
      "${cmd[@]}" \
      2>&1 | tee "${log}"
  rc="${PIPESTATUS[0]}"
  set -e

  cleanup_sampler
  end_iso="$(date -Is)"
  end_epoch="$(date +%s.%N)"
  wall="$(python3 - <<PY
print(f"{float('${end_epoch}') - float('${start_epoch}'):.6f}")
PY
)"

  if [[ "${rc}" -eq 0 ]]; then
    runtime_status="DONE"
  elif [[ "${rc}" -eq 124 ]]; then
    runtime_status="TIMEOUT"
  else
    runtime_status="ERROR"
  fi

  {
    echo "group=${group}"
    echo "case=${case_name}"
    echo "mps=${mps}"
    echo "tolerance=${tolerance}"
    echo "repeat=${repeat}"
    echo "gpu_id=${GPU_ID}"
    echo "start=${start_iso}"
    echo "end=${end_iso}"
    echo "wall_seconds=${wall}"
    echo "exit_code=${rc}"
    echo "runtime_status=${runtime_status}"
    echo "json=${json}"
    echo "log=${log}"
    echo "time_log=${time_log}"
    echo "metrics=${metrics}"
    echo "command_file=${command_file}"
  } > "${status_file}"

  echo "[done] ${case_name}: ${runtime_status}, rc=${rc}, wall=${wall}s"
}

profile_status_is_complete() {
  local exit_file="$1"
  [[ -s "${exit_file}" ]] || return 1
  [[ "$(cat "${exit_file}")" == "0" ]]
}

run_profile_one() {
  local case_name="$1"
  local case_dir="${PROFILE_DIR}/current/${case_name}"
  local trace_dir="${case_dir}/trace"
  local mps="${MPS_DIR}/${case_name}.mps"
  local json="${case_dir}/${case_name}_rocm.json"
  local log="${case_dir}/${case_name}_rocm.log"
  local exit_file="${case_dir}/${case_name}_rocm.exitcode"
  local command_file="${case_dir}/${case_name}_rocm.command.txt"
  local status_file="${case_dir}/${case_name}_rocm.profile.status.env"
  local time_log="${case_dir}/${case_name}_rocm.time.txt"
  local metrics="${case_dir}/${case_name}_rocm.rocm_smi_raw.txt"

  [[ -s "${mps}" ]] || die "profile MPS missing: ${mps}"
  mkdir -p "${trace_dir}"

  if profile_status_is_complete "${exit_file}"; then
    echo "[resume skip profile] ${case_name}"
    return 0
  fi

  printf 'HIP_VISIBLE_DEVICES=%q ROCR_VISIBLE_DEVICES=%q timeout --foreground %qs /usr/bin/time -v -o %q ' \
    "${GPU_ID}" "${GPU_ID}" "${PROFILE_EXTERNAL_TIMEOUT}" "${time_log}" > "${command_file}"
  printf 'rocprofv3 --runtime-trace --output-format csv --output-directory %q --output-file trace -- ' \
    "${trace_dir}" >> "${command_file}"
  printf '%q ' "${PLC}" -fname "${mps}" -out "${json}" \
    -nIterLim 1000000000 -dTimeLim "${PROFILE_SOLVER_TIME_LIMIT}" >> "${command_file}"
  printf '\n' >> "${command_file}"

  local start_iso start_epoch end_iso end_epoch rc wall
  start_iso="$(date -Is)"
  start_epoch="$(date +%s.%N)"
  record_command "${start_iso}" "targeted_profile" "${case_name}" "default" "1" \
    "${command_file}" "${status_file}"

  echo
  echo "[profile] ${case_name}"
  start_sampler "${metrics}"
  set +e
  HIP_VISIBLE_DEVICES="${GPU_ID}" \
  ROCR_VISIBLE_DEVICES="${GPU_ID}" \
    timeout --foreground "${PROFILE_EXTERNAL_TIMEOUT}s" \
    /usr/bin/time -v -o "${time_log}" \
    rocprofv3 \
      --runtime-trace \
      --output-format csv \
      --output-directory "${trace_dir}" \
      --output-file trace \
      -- "${PLC}" \
        -fname "${mps}" \
        -out "${json}" \
        -nIterLim 1000000000 \
        -dTimeLim "${PROFILE_SOLVER_TIME_LIMIT}" \
      > "${log}" 2>&1
  rc=$?
  set -e
  cleanup_sampler

  end_iso="$(date -Is)"
  end_epoch="$(date +%s.%N)"
  wall="$(python3 - <<PY
print(f"{float('${end_epoch}') - float('${start_epoch}'):.6f}")
PY
)"

  echo "${rc}" > "${exit_file}"
  find "${trace_dir}" -maxdepth 3 -type f | sort > "${case_dir}/trace_files.txt" || true
  {
    echo "group=targeted_profile"
    echo "case=${case_name}"
    echo "mps=${mps}"
    echo "gpu_id=${GPU_ID}"
    echo "start=${start_iso}"
    echo "end=${end_iso}"
    echo "wall_seconds=${wall}"
    echo "exit_code=${rc}"
    echo "runtime_status=$([[ ${rc} -eq 0 ]] && echo DONE || echo ERROR)"
    echo "json=${json}"
    echo "log=${log}"
    echo "trace_dir=${trace_dir}"
    echo "time_log=${time_log}"
    echo "metrics=${metrics}"
    echo "command_file=${command_file}"
  } > "${status_file}"

  local profile_bytes
  profile_bytes="$(du -sb "${PROFILE_DIR}" 2>/dev/null | awk '{print $1}' || echo 0)"
  echo "[profile done] ${case_name}: rc=${rc}, wall=${wall}s, profile_bytes=${profile_bytes}"
  if (( profile_bytes > PROFILE_MAX_BYTES )); then
    request_stop "profile directory exceeded PROFILE_MAX_BYTES=${PROFILE_MAX_BYTES}"
  fi
}

parse_results() {
  msg "Parse solver/resource results"

  python3 - "${RUN_ROOT}" "${PARSED_DIR}/final_sprint_summary.csv" <<'PY'
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from statistics import mean

root = Path(sys.argv[1])
out = Path(sys.argv[2])

def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            found = find_key(value, key)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_key(value, key)
            if found is not None:
                return found
    return None

def read_env(path: Path):
    data = {}
    for line in path.read_text(errors="replace").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            data[k] = v
    return data

def floats(patterns, text):
    values = []
    for pattern in patterns:
        values.extend(float(x) for x in re.findall(pattern, text, flags=re.I))
    return values

solver_keys = [
    "terminationCode", "terminationIterate", "primalCode", "dualCode",
    "nIter", "nAxCalls", "nAtyCalls", "dSolvingTime", "dScalingTime",
    "DeviceMatVecProdTime", "dPrimalObj", "dDualObj",
    "dRelPrimalFeas", "dRelDualFeas", "dRelDualityGap",
]

rows = []
for status_path in sorted(root.rglob("*.status.env")):
    if ".profile.status.env" in status_path.name:
        continue
    status = read_env(status_path)
    json_path = Path(status.get("json", ""))
    payload = {}
    if json_path.exists() and json_path.stat().st_size:
        try:
            payload = json.loads(json_path.read_text())
        except Exception as exc:
            status["json_parse_error"] = repr(exc)

    row = dict(status)
    for key in solver_keys:
        row[key] = find_key(payload, key)

    metrics_path = Path(status.get("metrics", ""))
    if metrics_path.exists():
        text = metrics_path.read_text(errors="replace")
        vram = floats([
            r"VRAM Total Used Memory \(B\):\s*([0-9.]+)",
            r"VRAM.*Used.*?([0-9]+)\s*$",
        ], text)
        gpu = floats([
            r"GPU use \(%\):\s*([0-9.]+)",
            r"GPU use:\s*([0-9.]+)%",
        ], text)
        memuse = floats([
            r"GPU Memory Allocated \(%\):\s*([0-9.]+)",
            r"Memory use \(%\):\s*([0-9.]+)",
        ], text)
        power = floats([
            r"Average Graphics Package Power \(W\):\s*([0-9.]+)",
            r"Average Graphics Package Power:\s*([0-9.]+)\s*W",
        ], text)
        temp = floats([
            r"Temperature.*?\(C\):\s*([0-9.]+)",
            r"Temperature.*?:\s*([0-9.]+)c",
        ], text)

        row["resource_samples"] = max(len(vram), len(gpu), len(power), len(temp))
        row["peak_vram_used_bytes"] = max(vram) if vram else None
        row["min_vram_used_bytes"] = min(vram) if vram else None
        row["peak_vram_delta_bytes"] = (max(vram) - min(vram)) if vram else None
        row["avg_gpu_use_pct"] = mean(gpu) if gpu else None
        row["max_gpu_use_pct"] = max(gpu) if gpu else None
        row["avg_memory_use_pct"] = mean(memuse) if memuse else None
        row["max_memory_use_pct"] = max(memuse) if memuse else None
        row["avg_power_w"] = mean(power) if power else None
        row["max_power_w"] = max(power) if power else None
        row["max_temperature_c"] = max(temp) if temp else None

    time_path = Path(status.get("time_log", ""))
    if time_path.exists():
        time_text = time_path.read_text(errors="replace")
        rss = re.search(r"Maximum resident set size \(kbytes\):\s*([0-9]+)", time_text)
        row["max_rss_kbytes"] = int(rss.group(1)) if rss else None

    rows.append(row)

fields = [
    "group", "case", "tolerance", "repeat", "gpu_id",
    "start", "end", "runtime_status", "exit_code", "wall_seconds",
    *solver_keys,
    "resource_samples", "peak_vram_used_bytes", "min_vram_used_bytes",
    "peak_vram_delta_bytes", "avg_gpu_use_pct", "max_gpu_use_pct",
    "avg_memory_use_pct", "max_memory_use_pct", "avg_power_w", "max_power_w",
    "max_temperature_c", "max_rss_kbytes",
    "mps", "json", "log", "time_log", "metrics", "command_file",
]

out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] parsed_rows={len(rows)}")
print(f"[OK] summary={out}")
print("case,tol,rep,status,termination,nIter,wall,solve,peak_vram_delta,max_gpu,avg_power")
for row in rows:
    print(
        row.get("case", ""), row.get("tolerance", ""), row.get("repeat", ""),
        row.get("runtime_status", ""), row.get("terminationCode", ""),
        row.get("nIter", ""), row.get("wall_seconds", ""),
        row.get("dSolvingTime", ""), row.get("peak_vram_delta_bytes", ""),
        row.get("max_gpu_use_pct", ""), row.get("avg_power_w", ""), sep=","
    )
PY
}

summarize_profiles() {
  if find "${PROFILE_DIR}" -type f -name '*_kernel_trace.csv' -print -quit 2>/dev/null | grep -q .; then
    python3 scripts/summarize_rocprofv3_milestones.py "${PROFILE_DIR}" \
      2>&1 | tee "${LOG_DIR}/profile_summary.log" || true
  else
    echo "[profile] no trace CSV found to summarize"
  fi
}

generate_throughput() {
  msg "Generate throughput evidence"
  mkdir -p "${THROUGHPUT_DIR}"
  local summary="${PARSED_DIR}/final_sprint_summary.csv"

  if [[ -s "${summary}" ]]; then
    python3 - "${summary}" "${THROUGHPUT_DIR}/single_card_throughput.csv" <<'PY'
import csv, sys
from collections import defaultdict
from pathlib import Path

src, out = map(Path, sys.argv[1:])
groups = defaultdict(list)
with src.open(newline="") as f:
    for row in csv.DictReader(f):
        if row.get("group") not in {"nonhard23_baseline", "mini_baseline", "large_mps_pilot_baseline"}:
            continue
        if row.get("runtime_status") != "DONE":
            continue
        groups[(row.get("group", ""), row.get("repeat", ""))].append(row)

fields = [
    "group", "repeat", "completed_cases", "wall_seconds_sum", "solve_seconds_sum",
    "cases_per_hour", "solve_seconds_per_elapsed_hour",
]
rows = []
for (group, repeat), items in sorted(groups.items()):
    wall = sum(float(x.get("wall_seconds") or 0) for x in items)
    solve = sum(float(x.get("dSolvingTime") or 0) for x in items)
    rows.append({
        "group": group,
        "repeat": repeat,
        "completed_cases": len(items),
        "wall_seconds_sum": wall,
        "solve_seconds_sum": solve,
        "cases_per_hour": (len(items) * 3600 / wall) if wall else "",
        "solve_seconds_per_elapsed_hour": (solve * 3600 / wall) if wall else "",
    })

with out.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(out)
PY
  else
    echo "[throughput] parsed solver summary is absent"
  fi

  local legacy_md="${REPO_DIR}/validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md"
  local legacy_runtime="${REPO_DIR}/validation/w7900_8card_batch_fast8_concurrent_runtime_20260616.csv"
  local legacy_solver="${REPO_DIR}/validation/w7900_8card_batch_fast8_concurrent_solver_20260616.csv"
  if [[ -f "${legacy_md}" ]]; then
    mkdir -p "${THROUGHPUT_DIR}/legacy_8card_fast8"
    cp -a "${legacy_md}" "${THROUGHPUT_DIR}/legacy_8card_fast8/"
    [[ -f "${legacy_runtime}" ]] && cp -a "${legacy_runtime}" "${THROUGHPUT_DIR}/legacy_8card_fast8/"
    [[ -f "${legacy_solver}" ]] && cp -a "${legacy_solver}" "${THROUGHPUT_DIR}/legacy_8card_fast8/"
    cat > "${THROUGHPUT_DIR}/legacy_8card_fast8/BOUNDARY.txt" <<'TXT'
This is reused historical evidence for eight independent MPS jobs running concurrently.
It is NOT distributed multi-GPU solving of one LP.
No new 8-card experiment is launched by the v2 final-sprint runner.
TXT
  fi
}

archive_run() {
  msg "Parse, checksum and archive"
  parse_results
  summarize_profiles
  generate_throughput

  (
    cd "${RUN_ROOT}"
    find . -type f ! -path './00_manifest/files_sha256.txt' -print0 \
      | sort -z \
      | xargs -0 sha256sum > "${MANIFEST_DIR}/files_sha256.txt"
  )

  if [[ "${CREATE_ARCHIVE}" != "1" ]]; then
    echo "[skip] CREATE_ARCHIVE=${CREATE_ARCHIVE}"
    return 0
  fi

  local run_name archive
  run_name="$(basename "${RUN_ROOT}")"
  archive="${WORK_ROOT}/results/${run_name}.tar.gz"
  tar -C "$(dirname "${RUN_ROOT}")" -czf "${archive}" "${run_name}"
  sha256sum "${archive}" > "${archive}.sha256"

  echo "archive=${archive}"
  echo "sha256_file=${archive}.sha256"
  cat "${archive}.sha256"
}

baseline_cases() {
  # Historical-long-first order reduces the risk of leaving expensive cases
  # until the end, while repeat-major scheduling still completes repeat 1 first.
  printf '%s\n' \
    Primal2_1000 s100 thk_63 square41 tpl-tub-ws1617 thk_48 \
    L2CTA3D set-cover-model rmine15 neos-3025225 a2864 \
    irish-electricity s250r10 neos-5052403-cygnet scpm1 \
    supportcase10 woodlands09 neos-5251015 savsched1 datt256_lp \
    graph40-40 ex10 qap15
}

precision_cases() {
  printf '%s\n' L2CTA3D set-cover-model thk_48 square41 tpl-tub-ws1617
}

profile_cases() {
  printf '%s\n' thk_48 square41 L2CTA3D set-cover-model tpl-tub-ws1617
}

run_mini() {
  verify_dataset mini
  write_manifest_once

  require_budget_or_stop 30 "mini qap15 baseline" || return 0
  run_solver_one "mini_baseline" qap15 1e-4 1 \
    "${BASELINE_DIR}/mini/rep_1" \
    "${BASELINE_TIME_LIMIT}" "${BASELINE_EXTERNAL_TIMEOUT}"

  local tol
  for tol in ${PRECISION_LEVELS}; do
    (( STOP_REQUESTED == 0 )) || return 0
    require_budget_or_stop 45 "mini qap15 precision ${tol}" || return 0
    run_solver_one "mini_precision" qap15 "${tol}" 1 \
      "${PRECISION_DIR}/mini/qap15/tol_${tol}/rep_1" \
      "${PRECISION_TIME_LIMIT}" "${PRECISION_EXTERNAL_TIMEOUT}"
  done

  if [[ "${PILOT_PROFILE}" == "1" && "${STOP_REQUESTED}" == "0" ]]; then
    command -v rocprofv3 >/dev/null 2>&1 || die "rocprofv3 missing"
    require_budget_or_stop 90 "mini qap15 profile" || return 0
    run_profile_one qap15
  fi
}

run_pilot() {
  verify_dataset pilot
  write_manifest_once

  local case_name
  for case_name in set-cover-model square41; do
    (( STOP_REQUESTED == 0 )) || return 0
    require_budget_or_stop "$(estimate_baseline_seconds "${case_name}")" \
      "pilot baseline ${case_name}" || return 0
    run_solver_one "large_mps_pilot_baseline" "${case_name}" 1e-4 1 \
      "${BASELINE_DIR}/pilot/rep_1" \
      "${BASELINE_TIME_LIMIT}" "${BASELINE_EXTERNAL_TIMEOUT}"
  done

  local tol
  for tol in ${PRECISION_LEVELS}; do
    (( STOP_REQUESTED == 0 )) || return 0
    require_budget_or_stop "$(estimate_precision_seconds set-cover-model "${tol}")" \
      "pilot precision set-cover-model ${tol}" || return 0
    run_solver_one "large_mps_pilot_precision" set-cover-model "${tol}" 1 \
      "${PRECISION_DIR}/pilot/set-cover-model/tol_${tol}/rep_1" \
      "${PRECISION_TIME_LIMIT}" "${PRECISION_EXTERNAL_TIMEOUT}"
  done

  if [[ "${PILOT_PROFILE}" == "1" && "${STOP_REQUESTED}" == "0" ]]; then
    require_budget_or_stop "$(estimate_profile_seconds set-cover-model)" \
      "pilot profile set-cover-model" || return 0
    run_profile_one set-cover-model
  fi
}

run_baseline23() {
  verify_dataset nonhard23
  write_manifest_once

  local repeat case_name estimate
  for ((repeat=1; repeat<=BASELINE_REPEATS; repeat++)); do
    echo "[baseline] begin complete repeat ${repeat}/${BASELINE_REPEATS}"
    while IFS= read -r case_name; do
      (( STOP_REQUESTED == 0 )) || return 0
      estimate="$(estimate_baseline_seconds "${case_name}")"
      require_budget_or_stop "${estimate}" "baseline ${case_name} rep=${repeat}" || return 0
      run_solver_one "nonhard23_baseline" "${case_name}" 1e-4 "${repeat}" \
        "${BASELINE_DIR}/rep_${repeat}" \
        "${BASELINE_TIME_LIMIT}" "${BASELINE_EXTERNAL_TIMEOUT}"
    done < <(baseline_cases)
    echo "[baseline] complete repeat ${repeat}/${BASELINE_REPEATS}"
  done
}

run_precision() {
  verify_dataset precision5
  write_manifest_once

  local repeat tol case_name estimate
  for ((repeat=1; repeat<=PRECISION_REPEATS; repeat++)); do
    echo "[precision] begin complete matrix repeat ${repeat}/${PRECISION_REPEATS}"
    for tol in ${PRECISION_LEVELS}; do
      echo "[precision] repeat=${repeat}, tolerance=${tol}"
      while IFS= read -r case_name; do
        (( STOP_REQUESTED == 0 )) || return 0
        estimate="$(estimate_precision_seconds "${case_name}" "${tol}")"
        require_budget_or_stop "${estimate}" \
          "precision ${case_name} tol=${tol} rep=${repeat}" || return 0
        run_solver_one "precision_sensitivity" "${case_name}" "${tol}" "${repeat}" \
          "${PRECISION_DIR}/${case_name}/tol_${tol}/rep_${repeat}" \
          "${PRECISION_TIME_LIMIT}" "${PRECISION_EXTERNAL_TIMEOUT}"
      done < <(precision_cases)
    done
    echo "[precision] complete matrix repeat ${repeat}/${PRECISION_REPEATS}"
  done
}

run_profile() {
  verify_dataset profile5
  write_manifest_once
  command -v rocprofv3 >/dev/null 2>&1 || die "rocprofv3 missing"

  local case_name estimate
  while IFS= read -r case_name; do
    (( STOP_REQUESTED == 0 )) || return 0
    estimate="$(estimate_profile_seconds "${case_name}")"
    require_budget_or_stop "${estimate}" "profile ${case_name}" || return 0
    run_profile_one "${case_name}"
  done < <(profile_cases)
}

run_plan() {
  case "${PLAN_MODE}" in
    mini)
      run_mini
      ;;
    pilot)
      run_pilot
      ;;
    baseline23)
      run_baseline23
      ;;
    precision)
      run_precision
      ;;
    profile)
      run_profile
      ;;
    session2)
      run_precision
      (( STOP_REQUESTED == 0 )) && run_profile
      ;;
    all)
      run_baseline23
      (( STOP_REQUESTED == 0 )) && run_precision
      (( STOP_REQUESTED == 0 )) && run_profile
      ;;
    *)
      die "unsupported plan: ${PLAN_MODE}"
      ;;
  esac
}

show_status() {
  echo "repo=${REPO_DIR}"
  echo "branch=$(git branch --show-current)"
  echo "head=$(git rev-parse HEAD)"
  echo
  echo "working tree:"
  git status --short
  echo
  echo "binaries:"
  ls -lh build-cpu/bin/plc build-rocm-w7900/bin/plc 2>/dev/null || true
  echo
  echo "dataset:"
  echo "mps_dir=${MPS_DIR}"
  echo "mps_count=$(find "${MPS_DIR}" -maxdepth 1 -type f -name '*.mps' 2>/dev/null | wc -l)"
  du -sh "${DATA_ROOT}" 2>/dev/null || true
  echo
  echo "recent final-sprint runs:"
  find "${WORK_ROOT}/results/final_sprint" -mindepth 1 -maxdepth 1 -type d \
    -printf '%TY-%Tm-%Td %TH:%TM %p\n' 2>/dev/null | sort -r | head -20 || true
}

if [[ "${REQUESTED_MODE}" == "status" ]]; then
  show_status
  exit 0
fi

if [[ "${REQUESTED_MODE}" == "throughput" ]]; then
  [[ -d "${RUN_ROOT}" ]] || die "RUN_ROOT does not exist"
  create_directories
  parse_results
  generate_throughput
  exit 0
fi

if [[ "${REQUESTED_MODE}" == "archive" ]]; then
  [[ -d "${RUN_ROOT}" ]] || die "RUN_ROOT does not exist"
  create_directories
  source_environment
  archive_run
  exit 0
fi

create_directories
SESSION_LOG="${LOG_DIR}/${REQUESTED_MODE}_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "${SESSION_LOG}") 2>&1

msg "W7900 final-sprint runner v2"
echo "requested_mode=${REQUESTED_MODE}"
echo "planned_mode=${PLAN_MODE}"
echo "run_root=${RUN_ROOT}"
echo "window_minutes=${WINDOW_MINUTES}"
echo "reserve_minutes=${RESERVE_MINUTES}"

case "${PLAN_MODE}" in
  mini|pilot) verify_solver_state 0 ;;
  *) verify_solver_state 1 ;;
esac
source_environment
write_manifest_once
run_plan
archive_run

msg "Runner completed"
echo "planned_mode=${PLAN_MODE}"
echo "run_root=${RUN_ROOT}"
echo "stop_requested=${STOP_REQUESTED}"
echo "IMPORTANT: copy the tar.gz and .sha256 to persistent storage and verify them."
