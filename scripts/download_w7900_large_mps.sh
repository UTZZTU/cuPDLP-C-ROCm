#!/usr/bin/env bash
set -Eeuo pipefail

# Download and verify the private large-MPS dataset with BaiduPCS-Go.
#
# Modes:
#   login       - hidden interactive cookies login
#   status      - account, remote tree and local status
#   metadata    - inventory + SHA256 manifest
#   mini        - smallest real case: qap15.mps
#   pilot       - set-cover-model.mps + square41.mps
#   nonhard23   - authoritative 23-case main set
#   precision5  - five cases used by the precision experiment
#   profile5    - five cases used by targeted rocprofv3
#   hard3       - optional diagnostic cases only
#   all26       - complete manifest set (not required by the sprint)
#   verify SCOPE
#
# Each case is downloaded and SHA256-verified independently. Re-running the
# same scope skips already verified files and resumes only missing/bad files.

MODE="${1:-status}"
VERIFY_SCOPE="${2:-}"

case "${MODE}" in
  login|status|metadata|mini|pilot|nonhard23|precision5|profile5|hard3|all26|verify) ;;
  *)
    echo "Usage: $0 [login|status|metadata|mini|pilot|nonhard23|precision5|profile5|hard3|all26|verify SCOPE]" >&2
    exit 2
    ;;
esac

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
REPO_DIR="${REPO_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
TOOLS_DIR="${WORK_ROOT}/tools"
PCS="${TOOLS_DIR}/BaiduPCS-Go"
export BAIDUPCS_GO_CONFIG_DIR="${BAIDUPCS_GO_CONFIG_DIR:-${WORK_ROOT}/baidupcs_config}"

REMOTE_ROOT="${REMOTE_ROOT:-/cupdlp-large-mps-benchmark}"
REMOTE_MPS="${REMOTE_ROOT}/mps"
DATA_ROOT="${DATA_ROOT:-${WORK_ROOT}/datasets/large_mps_baidu/cupdlp-large-mps-benchmark}"
MPS_DIR="${MPS_DIR:-${DATA_ROOT}/mps}"
MANIFEST="${DATA_ROOT}/h100_large_mps_manifest.sha256"
INVENTORY="${DATA_ROOT}/h100_large_mps_inventory.csv"
NONHARD_LIST="${NONHARD_LIST:-${REPO_DIR}/validation/cases_w7900_large_mps_before_after_nonhard23.txt}"
LOG_DIR="${WORK_ROOT}/logs/large_mps_download"
VERIFY_DIR="${WORK_ROOT}/results/dataset_verification"

mkdir -p \
  "${BAIDUPCS_GO_CONFIG_DIR}" \
  "${DATA_ROOT}" \
  "${MPS_DIR}" \
  "${LOG_DIR}" \
  "${VERIFY_DIR}"

msg() {
  echo
  echo "============================================================"
  echo "$*"
  echo "============================================================"
}

die() {
  echo "[ERROR] $*" >&2
  exit 1
}

require_repo() {
  [[ -n "${REPO_DIR}" && -d "${REPO_DIR}/.git" ]] \
    || die "run this script from a cloned cuPDLP-C-ROCm repository"
}

require_pcs() {
  [[ -x "${PCS}" ]] || die "BaiduPCS-Go missing: ${PCS}; run prepare script setup/all"
}

secure_login() {
  require_pcs
  local cookies=""
  read -rsp "Paste Baidu cookies (input hidden): " cookies
  echo
  [[ -n "${cookies}" ]] || die "empty cookies"
  "${PCS}" login -cookies="${cookies}"
  unset cookies
  "${PCS}" who
}

check_login() {
  require_pcs
  "${PCS}" who
}

download_paths() {
  local save_to="$1"
  shift
  mkdir -p "${save_to}"

  local stamp log time_log rc
  stamp="$(date +%Y%m%d_%H%M%S_%N)"
  log="${LOG_DIR}/baidupcs_${stamp}.log"
  time_log="${LOG_DIR}/baidupcs_${stamp}.time.txt"

  echo "[download] save_to=${save_to}"
  printf '[download] remote='
  printf ' %q' "$@"
  echo

  set +e
  if [[ -x /usr/bin/time ]]; then
    /usr/bin/time -v -o "${time_log}" \
      "${PCS}" d --saveto "${save_to}" "$@" \
      2>&1 | tee "${log}"
    rc="${PIPESTATUS[0]}"
  else
    "${PCS}" d --saveto "${save_to}" "$@" \
      2>&1 | tee "${log}"
    rc="${PIPESTATUS[0]}"
  fi
  set -e

  [[ "${rc}" -eq 0 ]] || die "BaiduPCS-Go download failed: rc=${rc}, log=${log}"
}

download_metadata() {
  msg "Download metadata"
  check_login

  local remotes=()
  [[ -s "${MANIFEST}" ]] || remotes+=("${REMOTE_ROOT}/h100_large_mps_manifest.sha256")
  [[ -s "${INVENTORY}" ]] || remotes+=("${REMOTE_ROOT}/h100_large_mps_inventory.csv")

  if ((${#remotes[@]})); then
    download_paths "${DATA_ROOT}" "${remotes[@]}"
  else
    echo "[skip] metadata already exists"
  fi

  [[ -s "${MANIFEST}" ]] || die "manifest missing after download"
  [[ -s "${INVENTORY}" ]] || die "inventory missing after download"
  echo "[OK] ${MANIFEST}"
  echo "[OK] ${INVENTORY}"
}

ensure_metadata() {
  if [[ -s "${MANIFEST}" && -s "${INVENTORY}" ]]; then
    echo "[skip] local metadata already exists"
  else
    download_metadata
  fi
}

manifest_hash_for_case() {
  local case_name="$1"
  awk -v target="${case_name}" '
    {
      path=$2
      sub(/^\*/, "", path)
      sub(/^\.\//, "", path)
      sub(/^mps\//, "", path)
      if (path == target) {
        print $1
        exit
      }
    }
  ' "${MANIFEST}"
}

verify_case_quiet() {
  local case_name="$1"
  local file="${MPS_DIR}/${case_name}"
  [[ -s "${file}" ]] || return 1

  local expected actual
  expected="$(manifest_hash_for_case "${case_name}")"
  [[ -n "${expected}" ]] || return 1
  actual="$(sha256sum "${file}" | awk '{print $1}')"
  [[ "${actual}" == "${expected}" ]]
}

verify_case() {
  local case_name="$1"
  local file="${MPS_DIR}/${case_name}"
  if [[ ! -s "${file}" ]]; then
    echo "[MISSING] ${case_name}"
    return 1
  fi

  local expected actual
  expected="$(manifest_hash_for_case "${case_name}")"
  if [[ -z "${expected}" ]]; then
    echo "[NO_MANIFEST_ENTRY] ${case_name}"
    return 1
  fi

  actual="$(sha256sum "${file}" | awk '{print $1}')"
  if [[ "${actual}" == "${expected}" ]]; then
    echo "[OK] ${case_name}"
    return 0
  fi

  echo "[BAD] ${case_name}: expected=${expected}, actual=${actual}"
  return 1
}

download_case() {
  local case_name="$1"

  if verify_case_quiet "${case_name}"; then
    echo "[skip verified] ${case_name}"
    return 0
  fi

  if [[ -e "${MPS_DIR}/${case_name}" ]]; then
    local bad="${MPS_DIR}/${case_name}.bad.$(date +%Y%m%d_%H%M%S)"
    echo "[warn] move invalid/partial file to ${bad}"
    mv "${MPS_DIR}/${case_name}" "${bad}"
  fi

  download_paths "${MPS_DIR}" "${REMOTE_MPS}/${case_name}"
  verify_case "${case_name}" || die "checksum failed after download: ${case_name}"
}

mini_cases() {
  printf '%s\n' qap15.mps
}

pilot_cases() {
  printf '%s\n' set-cover-model.mps square41.mps
}

nonhard23_cases() {
  require_repo
  [[ -f "${NONHARD_LIST}" ]] || die "case list missing: ${NONHARD_LIST}"
  awk 'NF && $1 !~ /^#/ {print $1}' "${NONHARD_LIST}"
}

precision5_cases() {
  printf '%s\n' \
    L2CTA3D.mps \
    set-cover-model.mps \
    thk_48.mps \
    square41.mps \
    tpl-tub-ws1617.mps
}

profile5_cases() {
  precision5_cases
}

hard3_cases() {
  printf '%s\n' dlr1.mps Dual2_5000.mps fhnw-binschedule1.mps
}

all26_cases() {
  [[ -s "${MANIFEST}" ]] || die "manifest missing"
  awk '
    {
      path=$2
      sub(/^\*/, "", path)
      sub(/^\.\//, "", path)
      sub(/^mps\//, "", path)
      if (path ~ /\.mps$/) print path
    }
  ' "${MANIFEST}" | sort -u
}

cases_for_scope() {
  local scope="$1"
  case "${scope}" in
    mini) mini_cases ;;
    pilot) pilot_cases ;;
    nonhard23) nonhard23_cases ;;
    precision5) precision5_cases ;;
    profile5) profile5_cases ;;
    hard3) hard3_cases ;;
    all26) all26_cases ;;
    *) die "unknown dataset scope: ${scope}" ;;
  esac
}

verify_scope() {
  local scope="$1"
  ensure_metadata

  local stamp report json_report total=0 verified=0 failed=0 case_name
  stamp="$(date +%Y%m%d_%H%M%S)"
  report="${VERIFY_DIR}/${stamp}_${scope}.tsv"
  json_report="${VERIFY_DIR}/${stamp}_${scope}.json"
  printf 'case\tstatus\texpected_sha256\tactual_sha256\tbytes\tpath\n' > "${report}"

  while IFS= read -r case_name; do
    [[ -n "${case_name}" ]] || continue
    total=$((total + 1))

    local file expected actual bytes status
    file="${MPS_DIR}/${case_name}"
    expected="$(manifest_hash_for_case "${case_name}")"
    actual=""
    bytes="0"

    if [[ -s "${file}" ]]; then
      actual="$(sha256sum "${file}" | awk '{print $1}')"
      bytes="$(stat -c '%s' "${file}")"
    fi

    if [[ -n "${expected}" && "${actual}" == "${expected}" ]]; then
      status="OK"
      verified=$((verified + 1))
      echo "[OK] ${case_name}"
    else
      status="FAIL"
      failed=$((failed + 1))
      echo "[FAIL] ${case_name}"
    fi

    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
      "${case_name}" "${status}" "${expected}" "${actual}" "${bytes}" "${file}" \
      >> "${report}"
  done < <(cases_for_scope "${scope}")

  python3 - "${json_report}" "${scope}" "${total}" "${verified}" "${failed}" "${report}" <<'PY'
import json, sys
from pathlib import Path
out, scope, total, verified, failed, report = sys.argv[1:]
Path(out).write_text(json.dumps({
    "scope": scope,
    "total": int(total),
    "verified": int(verified),
    "failed": int(failed),
    "report_tsv": report,
}, indent=2, ensure_ascii=False) + "\n")
PY

  echo
  echo "scope=${scope}"
  echo "total=${total}"
  echo "verified=${verified}"
  echo "failed=${failed}"
  echo "report=${report}"
  echo "json_report=${json_report}"

  (( failed == 0 ))
}

download_scope() {
  local scope="$1"
  ensure_metadata

  msg "Download and verify scope: ${scope}"
  local case_name
  while IFS= read -r case_name; do
    [[ -n "${case_name}" ]] || continue
    download_case "${case_name}"
  done < <(cases_for_scope "${scope}")

  verify_scope "${scope}"
}

show_status() {
  require_pcs
  msg "Baidu account and remote dataset"
  "${PCS}" who || true
  "${PCS}" ls "${REMOTE_ROOT}" || true

  msg "Local dataset"
  echo "data_root=${DATA_ROOT}"
  echo "manifest=$([[ -s "${MANIFEST}" ]] && echo READY || echo MISSING)"
  echo "inventory=$([[ -s "${INVENTORY}" ]] && echo READY || echo MISSING)"
  echo "mps_count=$(find "${MPS_DIR}" -maxdepth 1 -type f -name '*.mps' 2>/dev/null | wc -l)"
  du -sh "${DATA_ROOT}" 2>/dev/null || true
  find "${MPS_DIR}" -maxdepth 1 -type f -name '*.mps' -printf '%f\n' 2>/dev/null | sort || true
}

case "${MODE}" in
  login)
    secure_login
    ;;
  status)
    show_status
    ;;
  metadata)
    download_metadata
    ;;
  mini|pilot|nonhard23|precision5|profile5|hard3|all26)
    download_scope "${MODE}"
    ;;
  verify)
    [[ -n "${VERIFY_SCOPE}" ]] || die "verify mode requires a scope"
    verify_scope "${VERIFY_SCOPE}"
    ;;
esac
