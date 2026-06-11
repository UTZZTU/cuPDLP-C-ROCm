#!/usr/bin/env bash
set -Eeuo pipefail

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
BRANCH="${BRANCH:-rocm-w7900-gfx1100}"
REPO_URL="${REPO_URL:-https://github.com/UTZZTU/cuPDLP-C-ROCm.git}"
REPO_SSH_URL="${REPO_SSH_URL:-git@github.com:UTZZTU/cuPDLP-C-ROCm.git}"

REPO_DIR="${WORK_ROOT}/src/cuPDLP-C-ROCm"
TOOLS_DIR="${WORK_ROOT}/tools"
LOG_DIR="${WORK_ROOT}/logs"
RESULT_DIR="${WORK_ROOT}/results"
DATASET_DIR="${WORK_ROOT}/datasets/large_mps_baidu"

DEPS_SRC="${WORK_ROOT}/deps/src"
DEPS_BUILD="${WORK_ROOT}/deps/build"
DEPS_INSTALL="${WORK_ROOT}/deps/install"

HIGHS_VERSION="${HIGHS_VERSION:-1.6.0}"
HIGHS_HOME="${HIGHS_HOME:-${DEPS_INSTALL}/highs-${HIGHS_VERSION}}"

ROCM_PY_HOME="${ROCM_PY_HOME:-/opt/python}"
ROCM_PY_CORE="${ROCM_PY_CORE:-/opt/python/lib/python3.12/site-packages/_rocm_sdk_core}"
ROCM_PY_DEVEL="${ROCM_PY_DEVEL:-/opt/python/lib/python3.12/site-packages/_rocm_sdk_devel}"

BAIDUPCS_VERSION="${BAIDUPCS_VERSION:-v4.0.1}"
BAIDUPCS_ZIP="BaiduPCS-Go-${BAIDUPCS_VERSION}-linux-amd64.zip"
BAIDUPCS_URL="https://github.com/qjfoidnh/BaiduPCS-Go/releases/download/${BAIDUPCS_VERSION}/${BAIDUPCS_ZIP}"

GIT_USER_NAME="${GIT_USER_NAME:-wwb}"
GIT_USER_EMAIL="${GIT_USER_EMAIL:-1599441272@qq.com}"

INSTALL_APT_PACKAGES="${INSTALL_APT_PACKAGES:-1}"
RUN_BUILD="${RUN_BUILD:-1}"
RUN_SMOKE="${RUN_SMOKE:-0}"
SETUP_GITHUB_SSH="${SETUP_GITHUB_SSH:-0}"

msg() {
  echo
  echo "== $* =="
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

make_dirs() {
  msg "Create workspace directories"
  mkdir -p \
    "${WORK_ROOT}/src" \
    "${DEPS_SRC}" \
    "${DEPS_BUILD}" \
    "${DEPS_INSTALL}" \
    "${TOOLS_DIR}" \
    "${LOG_DIR}" \
    "${RESULT_DIR}" \
    "${DATASET_DIR}"
}

install_base_packages() {
  if [[ "${INSTALL_APT_PACKAGES}" != "1" ]]; then
    msg "Skip apt package install"
    return 0
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    msg "apt-get not found, skip apt package install"
    return 0
  fi

  msg "Install base packages"
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates \
    curl \
    git \
    nano \
    unzip \
    python3 \
    build-essential \
    cmake \
    ninja-build \
    tar \
    xz-utils \
    openssh-client
}

install_baidupcs_go() {
  msg "Install BaiduPCS-Go"

  mkdir -p "${TOOLS_DIR}"
  cd "${TOOLS_DIR}"

  if [[ -x "${TOOLS_DIR}/BaiduPCS-Go" ]]; then
    echo "[skip] ${TOOLS_DIR}/BaiduPCS-Go already exists"
    return 0
  fi

  curl -L --retry 5 --retry-delay 3 -o "${BAIDUPCS_ZIP}" "${BAIDUPCS_URL}"

  rm -rf "BaiduPCS-Go-${BAIDUPCS_VERSION}-linux-amd64"

  if command -v unzip >/dev/null 2>&1; then
    unzip -o "${BAIDUPCS_ZIP}" -d "BaiduPCS-Go-${BAIDUPCS_VERSION}-linux-amd64"
  else
    python3 - <<PY
from pathlib import Path
from zipfile import ZipFile

zip_path = Path("${BAIDUPCS_ZIP}")
out_dir = Path("BaiduPCS-Go-${BAIDUPCS_VERSION}-linux-amd64")
out_dir.mkdir(parents=True, exist_ok=True)

with ZipFile(zip_path) as z:
    z.extractall(out_dir)

print("[done] extracted", zip_path)
PY
  fi

  local bin
  bin="$(find "BaiduPCS-Go-${BAIDUPCS_VERSION}-linux-amd64" -type f -name 'BaiduPCS-Go' | head -1)"
  [[ -n "${bin}" ]] || die "BaiduPCS-Go binary not found"

  cp "${bin}" "${TOOLS_DIR}/BaiduPCS-Go"
  chmod +x "${TOOLS_DIR}/BaiduPCS-Go"

  echo "[ok] ${TOOLS_DIR}/BaiduPCS-Go"
}

clone_or_update_repo() {
  msg "Clone or update repository"

  if [[ ! -d "${REPO_DIR}/.git" ]]; then
    rm -rf "${REPO_DIR}"
    cd "${WORK_ROOT}/src"

    GIT_TERMINAL_PROMPT=0 git clone \
      --depth 1 \
      --single-branch \
      --branch "${BRANCH}" \
      --filter=blob:none \
      "${REPO_URL}" \
      "${REPO_DIR}"
  else
    cd "${REPO_DIR}"
    git fetch origin "${BRANCH}"
    git checkout "${BRANCH}"
    git pull --ff-only origin "${BRANCH}"
  fi

  cd "${REPO_DIR}"
  git config user.name "${GIT_USER_NAME}"
  git config user.email "${GIT_USER_EMAIL}"

  if [[ -f .gitmodules ]]; then
    git config -f .gitmodules submodule.third-party/pybind11.url https://github.com/pybind/pybind11.git || true
    git submodule sync || true
  fi

  git log --oneline --decorate -5
  git status
}

setup_github_ssh_optional() {
  if [[ "${SETUP_GITHUB_SSH}" != "1" ]]; then
    msg "Skip GitHub SSH setup"
    echo "Set SETUP_GITHUB_SSH=1 when you need push access from a fresh machine."
    return 0
  fi

  msg "Setup temporary GitHub SSH key"

  local ssh_dir="${WORK_ROOT}/.ssh"
  local key="${ssh_dir}/github_w7900_ephemeral"

  mkdir -p "${ssh_dir}"
  chmod 700 "${ssh_dir}"

  if [[ ! -f "${key}" ]]; then
    ssh-keygen -t ed25519 -C "${GIT_USER_EMAIL}" -f "${key}" -N ""
  fi

  chmod 600 "${key}"
  chmod 644 "${key}.pub"

  echo
  echo "Add this public key to GitHub SSH keys:"
  echo "----- PUBLIC KEY BEGIN -----"
  cat "${key}.pub"
  echo "----- PUBLIC KEY END -----"
  echo
  read -r -p "After adding it to GitHub, press Enter to continue..."

  cd "${REPO_DIR}"
  git remote set-url origin "${REPO_SSH_URL}"
  git config core.sshCommand "ssh -i ${key} -o IdentitiesOnly=yes"
  ssh -i "${key}" -o IdentitiesOnly=yes -T git@github.com || true
  git remote -v
}

check_rocm_python_sdk() {
  msg "Check Python ROCm SDK"

  [[ -x "${ROCM_PY_HOME}/bin/hipcc" ]] || die "missing hipcc: ${ROCM_PY_HOME}/bin/hipcc"
  [[ -d "${ROCM_PY_DEVEL}/include" ]] || die "missing ROCm include: ${ROCM_PY_DEVEL}/include"

  export PATH="${TOOLS_DIR}:${ROCM_PY_HOME}/bin:${PATH}"
  export LD_LIBRARY_PATH="${ROCM_PY_DEVEL}/lib:${ROCM_PY_CORE}/lib:${HIGHS_HOME}/lib:${HIGHS_HOME}/lib64:${LD_LIBRARY_PATH:-}"
  export CMAKE_PREFIX_PATH="${ROCM_PY_DEVEL}:${CMAKE_PREFIX_PATH:-}"

  echo "hipcc: $(which hipcc)"
  hipcc --version || true

  echo
  echo "ROCm agents:"
  rocm_agent_enumerator || true

  echo
  echo "ROCm SMI:"
  rocm-smi || true

  echo
  echo "ROCm headers:"
  find "${ROCM_PY_DEVEL}/include" -maxdepth 2 \
    \( -name 'hipblas.h' -o -name 'hipsparse.h' -o -name 'rocblas.h' \) \
    -print || true
}

install_highs() {
  msg "Install HiGHS ${HIGHS_VERSION}"

  if [[ -x "${HIGHS_HOME}/bin/highs" ]] && [[ -d "${HIGHS_HOME}/include/highs" ]]; then
    echo "[skip] HiGHS already exists: ${HIGHS_HOME}"
    "${HIGHS_HOME}/bin/highs" --version || true
    return 0
  fi

  mkdir -p "${DEPS_SRC}" "${DEPS_BUILD}" "${DEPS_INSTALL}"
  cd "${DEPS_SRC}"

  local tarball="highs-v${HIGHS_VERSION}.tar.gz"
  local src_dir="highs-${HIGHS_VERSION}"

  if [[ ! -f "${tarball}" ]]; then
    curl -L --retry 10 --retry-delay 3 \
      -o "${tarball}" \
      "https://github.com/ERGO-Code/HiGHS/archive/refs/tags/v${HIGHS_VERSION}.tar.gz"
  fi

  rm -rf "HiGHS-${HIGHS_VERSION}" "${src_dir}"
  tar -xzf "${tarball}"
  mv "HiGHS-${HIGHS_VERSION}" "${src_dir}"

  cmake -S "${DEPS_SRC}/${src_dir}" \
    -B "${DEPS_BUILD}/highs-${HIGHS_VERSION}" \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_INSTALL_PREFIX="${HIGHS_HOME}"

  cmake --build "${DEPS_BUILD}/highs-${HIGHS_VERSION}" -j"$(nproc)"
  cmake --install "${DEPS_BUILD}/highs-${HIGHS_VERSION}"

  export LD_LIBRARY_PATH="${HIGHS_HOME}/lib:${HIGHS_HOME}/lib64:${LD_LIBRARY_PATH:-}"
  "${HIGHS_HOME}/bin/highs" --version || true
}

write_activate_script() {
  msg "Write activation script"

  cat > "${WORK_ROOT}/activate_w7900.sh" <<EOF
#!/usr/bin/env bash
export WORK_ROOT="${WORK_ROOT}"
export REPO_DIR="${REPO_DIR}"
export TOOLS_DIR="${TOOLS_DIR}"
export HIGHS_HOME="${HIGHS_HOME}"
export ROCM_PY_HOME="${ROCM_PY_HOME}"
export ROCM_PY_CORE="${ROCM_PY_CORE}"
export ROCM_PY_DEVEL="${ROCM_PY_DEVEL}"
export PATH="\${TOOLS_DIR}:\${ROCM_PY_HOME}/bin:\${PATH}"
export LD_LIBRARY_PATH="\${ROCM_PY_DEVEL}/lib:\${ROCM_PY_CORE}/lib:\${HIGHS_HOME}/lib:\${HIGHS_HOME}/lib64:\${LD_LIBRARY_PATH:-}"
export CMAKE_PREFIX_PATH="\${ROCM_PY_DEVEL}:\${CMAKE_PREFIX_PATH:-}"
cd "\${REPO_DIR}"
echo "Activated W7900 workspace"
echo "repo: \${REPO_DIR}"
echo "hipcc: \$(which hipcc 2>/dev/null || true)"
EOF

  chmod +x "${WORK_ROOT}/activate_w7900.sh"

  echo "Use this after bootstrap:"
  echo "  source ${WORK_ROOT}/activate_w7900.sh"
}

build_project() {
  if [[ "${RUN_BUILD}" != "1" ]]; then
    msg "Skip CPU/ROCm build"
    return 0
  fi

  msg "Build CPU and ROCm plc"

  cd "${REPO_DIR}"
  source "${WORK_ROOT}/activate_w7900.sh"

  export HIGHS_HOME="${HIGHS_HOME}"
  export LD_LIBRARY_PATH="${HIGHS_HOME}/lib:${HIGHS_HOME}/lib64:${LD_LIBRARY_PATH:-}"

  ./scripts/build_w7900_cpu.sh 2>&1 | tee "${LOG_DIR}/bootstrap_build_w7900_cpu.log"
  ./scripts/build_w7900_rocm.sh 2>&1 | tee "${LOG_DIR}/bootstrap_build_w7900_rocm.log"
}

run_smoke_optional() {
  if [[ "${RUN_SMOKE}" != "1" ]]; then
    msg "Skip smoke"
    return 0
  fi

  msg "Run W7900 smoke validation"

  cd "${REPO_DIR}"
  source "${WORK_ROOT}/activate_w7900.sh"

  ./scripts/run_w7900_smoke.sh 2>&1 | tee "${LOG_DIR}/bootstrap_run_w7900_smoke.log"
}

print_next_steps() {
  msg "Bootstrap complete"

  cat <<EOF
Workspace:
  ${WORK_ROOT}

Repository:
  ${REPO_DIR}

Activate:
  source ${WORK_ROOT}/activate_w7900.sh

BaiduPCS-Go:
  ${TOOLS_DIR}/BaiduPCS-Go

Large MPS target directory:
  ${DATASET_DIR}

Manual Baidu login:
  BaiduPCS-Go login -cookies='YOUR_COOKIES_HERE'

After downloading large MPS:
  cd ${DATASET_DIR}
  sha256sum -c h100_large_mps_manifest.sha256 2>&1 | tee ${LOG_DIR}/large_mps_sha256_check.log

Useful modes:
  RUN_BUILD=0 bash scripts/bootstrap_w7900_workspace.sh
  RUN_SMOKE=1 bash scripts/bootstrap_w7900_workspace.sh
  SETUP_GITHUB_SSH=1 bash scripts/bootstrap_w7900_workspace.sh

Notes:
  - No credentials are stored by this script.
  - Raw large MPS files stay outside git.
  - Commit only scripts, manifests, curated CSV summaries, and Markdown summaries.
EOF
}

main() {
  make_dirs
  install_base_packages
  install_baidupcs_go
  clone_or_update_repo
  setup_github_ssh_optional
  check_rocm_python_sdk
  install_highs
  write_activate_script
  build_project
  run_smoke_optional
  print_next_steps
}

main "$@"
