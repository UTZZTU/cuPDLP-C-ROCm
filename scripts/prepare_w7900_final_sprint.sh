#!/usr/bin/env bash
set -Eeuo pipefail

# Prepare a fresh W7900 machine for the final-sprint experiments.
#
# Modes:
#   network  - DNS/HTTPS/GitHub download checks only
#   setup    - packages + workspace dependencies, no project build
#   build    - CPU/ROCm build, no smoke
#   smoke    - run CPU/ROCm smoke using existing binaries
#   all      - setup + build + smoke
#   status   - inspect repository, tools, GPUs, binaries and dataset

MODE="${1:-all}"
case "${MODE}" in
  network|setup|build|smoke|all|status) ;;
  *)
    echo "Usage: $0 [network|setup|build|smoke|all|status]" >&2
    exit 2
    ;;
esac

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
REPO_DIR="${REPO_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
EXPECTED_BRANCH="${EXPECTED_BRANCH:-rocm-w7900-gfx1100}"
SOLVER_BASELINE_COMMIT="${SOLVER_BASELINE_COMMIT:-735764807d8698ff30811d1a6fcc45d4a3fd4817}"
MIN_GPU_COUNT="${MIN_GPU_COUNT:-1}"
LOG_DIR="${WORK_ROOT}/logs"
STAMP="$(date +%Y%m%d_%H%M%S)"

mkdir -p "${WORK_ROOT}" "${LOG_DIR}"

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

check_https() {
  local label="$1"
  local url="$2"
  printf '[HTTPS] %-24s ' "${label}"
  if curl -fsSL --connect-timeout 8 --max-time 25 --retry 1 \
      --range 0-0 -o /dev/null "${url}"; then
    echo "OK"
  else
    echo "FAIL"
    return 1
  fi
}

network_probe() {
  msg "External-network preflight"

  local failed=0 host
  for host in github.com raw.githubusercontent.com codeload.github.com; do
    printf '[DNS] %-26s ' "${host}"
    if timeout 10 getent ahostsv4 "${host}" >/dev/null 2>&1; then
      echo "OK"
    else
      echo "FAIL"
      failed=1
    fi
  done

  check_https "GitHub" "https://github.com/" || failed=1
  check_https "repository raw" \
    "https://raw.githubusercontent.com/UTZZTU/cuPDLP-C-ROCm/${EXPECTED_BRANCH}/README.md" || failed=1
  check_https "HiGHS v1.6.0" \
    "https://github.com/ERGO-Code/HiGHS/archive/refs/tags/v1.6.0.tar.gz" || failed=1
  check_https "BaiduPCS-Go v4.0.1" \
    "https://github.com/qjfoidnh/BaiduPCS-Go/releases/download/v4.0.1/BaiduPCS-Go-v4.0.1-linux-amd64.zip" || failed=1

  require_repo
  if GIT_TERMINAL_PROMPT=0 timeout 30 \
      git -C "${REPO_DIR}" ls-remote --exit-code --heads origin "${EXPECTED_BRANCH}" \
      >/dev/null 2>&1; then
    echo "[GIT] origin/${EXPECTED_BRANCH}: OK"
  else
    echo "[GIT] origin/${EXPECTED_BRANCH}: FAIL"
    failed=1
  fi

  (( failed == 0 )) || die "network preflight failed"
  echo "REQUIRED_NETWORK_CHECK_PASSED"
}

install_required_packages() {
  msg "Install/check required packages"

  if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      ca-certificates curl git nano unzip python3 build-essential \
      cmake ninja-build tar xz-utils openssh-client coreutils time
  fi

  local cmd
  for cmd in git curl cmake ninja gcc g++ python3 timeout sha256sum; do
    command -v "${cmd}" >/dev/null 2>&1 || die "required command missing: ${cmd}"
  done
  [[ -x /usr/bin/time ]] || die "GNU time missing: /usr/bin/time"
}

verify_solver_baseline() {
  msg "Verify branch and frozen solver source"
  require_repo
  cd "${REPO_DIR}"

  local branch
  branch="$(git branch --show-current)"
  echo "branch=${branch}"
  echo "head=$(git rev-parse HEAD)"
  [[ "${branch}" == "${EXPECTED_BRANCH}" ]] \
    || die "expected branch ${EXPECTED_BRANCH}, found ${branch}"

  if ! git cat-file -e "${SOLVER_BASELINE_COMMIT}^{commit}" 2>/dev/null; then
    git fetch --no-tags origin "${SOLVER_BASELINE_COMMIT}"
  fi

  local solver_paths=(CMakeLists.txt cmake cupdlp interface)

  if ! git diff --quiet "${SOLVER_BASELINE_COMMIT}" HEAD -- "${solver_paths[@]}"; then
    git diff --stat "${SOLVER_BASELINE_COMMIT}" HEAD -- "${solver_paths[@]}"
    die "committed solver source differs from the frozen baseline"
  fi

  if ! git diff --quiet -- "${solver_paths[@]}"; then
    git diff --stat -- "${solver_paths[@]}"
    die "working-tree solver source has local changes"
  fi

  if ! git diff --cached --quiet -- "${solver_paths[@]}"; then
    git diff --cached --stat -- "${solver_paths[@]}"
    die "staged solver source has local changes"
  fi

  local untracked_solver
  untracked_solver="$(git ls-files --others --exclude-standard -- "${solver_paths[@]}" || true)"
  [[ -z "${untracked_solver}" ]] || {
    echo "${untracked_solver}"
    die "untracked files exist under frozen solver paths"
  }

  echo "[OK] solver paths match ${SOLVER_BASELINE_COMMIT}"
  echo "[INFO] harness/docs changes outside solver paths are allowed during mini validation"
}

run_bootstrap_dependencies() {
  msg "Restore workspace dependencies"
  require_repo
  cd "${REPO_DIR}"

  INSTALL_APT_PACKAGES=0 \
  RUN_BUILD=0 \
  RUN_SMOKE=0 \
  SETUP_GITHUB_SSH=0 \
    bash scripts/bootstrap_w7900_workspace.sh

  verify_solver_baseline
  mkdir -p "${WORK_ROOT}/baidupcs_config"
}

run_build() {
  msg "Build CPU and ROCm targets"
  require_repo
  [[ -f "${WORK_ROOT}/activate_w7900.sh" ]] \
    || run_bootstrap_dependencies

  cd "${REPO_DIR}"
  # shellcheck disable=SC1091
  source "${WORK_ROOT}/activate_w7900.sh"

  bash scripts/build_w7900_cpu.sh \
    2>&1 | tee "${LOG_DIR}/final_sprint_build_cpu_${STAMP}.log"
  bash scripts/build_w7900_rocm.sh \
    2>&1 | tee "${LOG_DIR}/final_sprint_build_rocm_${STAMP}.log"

  [[ -x build-cpu/bin/plc ]] || die "CPU plc missing after build"
  [[ -x build-rocm-w7900/bin/plc ]] || die "ROCm plc missing after build"
}

run_smoke() {
  msg "Run CPU/ROCm smoke"
  require_repo
  [[ -x "${REPO_DIR}/build-cpu/bin/plc" ]] || die "CPU binary missing; run build"
  [[ -x "${REPO_DIR}/build-rocm-w7900/bin/plc" ]] || die "ROCm binary missing; run build"
  [[ -f "${WORK_ROOT}/activate_w7900.sh" ]] || die "activation script missing"

  cd "${REPO_DIR}"
  # shellcheck disable=SC1091
  source "${WORK_ROOT}/activate_w7900.sh"
  bash scripts/run_w7900_smoke.sh \
    2>&1 | tee "${LOG_DIR}/final_sprint_smoke_${STAMP}.log"
}

show_status() {
  require_repo
  cd "${REPO_DIR}"
  msg "W7900 final-sprint status"
  echo "repo=${REPO_DIR}"
  echo "branch=$(git branch --show-current)"
  echo "head=$(git rev-parse HEAD)"
  echo
  echo "working tree:"
  git status --short
  echo
  echo "tools:"
  command -v hipcc rocminfo rocm-smi amd-smi rocprofv3 /usr/bin/time || true
  echo
  echo "GPUs:"
  rocm_agent_enumerator 2>/dev/null | sort | uniq -c || true
  echo
  echo "binaries:"
  ls -lh build-cpu/bin/plc build-rocm-w7900/bin/plc 2>/dev/null || true
  echo
  echo "dataset:"
  local data_root="${WORK_ROOT}/datasets/large_mps_baidu/cupdlp-large-mps-benchmark"
  find "${data_root}/mps" -maxdepth 1 -type f -name '*.mps' 2>/dev/null | wc -l
  du -sh "${data_root}" 2>/dev/null || true
}

case "${MODE}" in
  network)
    network_probe
    ;;
  setup)
    network_probe
    install_required_packages
    verify_solver_baseline
    run_bootstrap_dependencies
    ;;
  build)
    install_required_packages
    verify_solver_baseline
    run_build
    ;;
  smoke)
    verify_solver_baseline
    run_smoke
    ;;
  all)
    network_probe
    install_required_packages
    verify_solver_baseline
    run_bootstrap_dependencies
    run_build
    run_smoke
    ;;
  status)
    show_status
    ;;
esac

msg "Preparation mode completed"
echo "mode=${MODE}"
echo "time=$(date -Is)"
