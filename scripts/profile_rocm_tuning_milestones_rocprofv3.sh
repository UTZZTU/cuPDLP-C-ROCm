#!/usr/bin/env bash
set -Eeuo pipefail

# Profile multiple ROCm tuning milestones with rocprofv3.
#
# Run from repository root:
#   CASE_TIMEOUT_SEC=900 PROFILE_CASES="lotfi scfxm1 pilot87" ./scripts/profile_rocm_tuning_milestones_rocprofv3.sh
#
# Defaults:
#   milestones: pre_tuning, remove_sync, cache_attrs, fused_average, reduce_scalar_copies, current
#   cases: lotfi scfxm1 pilot87
#
# Outputs:
#   validation/results/rocprof_tuning_milestones_<timestamp>/
#
# Notes:
#   Uses rocprofv3 --runtime-trace --output-format csv. This collects HIP API,
#   kernel dispatch, memory copy, memory allocation, scratch memory, and marker
#   trace CSVs while avoiding a very verbose full HSA trace.

CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
HIP_ARCH="${HIP_ARCH:-gfx1150}"
PROFILE_CASES="${PROFILE_CASES:-lotfi scfxm1 pilot87}"
TRACE_MODE="${TRACE_MODE:-runtime}"   # runtime or sys
ROOT="$(pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_ROOT="${ROOT}/validation/results/rocprof_tuning_milestones_${STAMP}"
WORKTREE_ROOT="${WORKTREE_ROOT:-/tmp/cupdlp_rocm_rocprof_tuning_milestones_${USER}_${STAMP}}"
CASE_SOURCE="${CASE_SOURCE:-validation/cases_benchmark_200m.txt}"
CURRENT_SHA="$(git rev-parse HEAD)"

if [ ! -f "${ROOT}/CMakeLists.txt" ] || [ ! -d "${ROOT}/cupdlp" ]; then
  echo "ERROR: run this script from the cuPDLP-C-ROCm repository root." >&2
  exit 1
fi

if ! command -v rocprofv3 >/dev/null 2>&1; then
  echo "ERROR: rocprofv3 not found in PATH." >&2
  exit 1
fi

if [ ! -f "${CASE_SOURCE}" ]; then
  echo "ERROR: missing case source: ${CASE_SOURCE}" >&2
  exit 1
fi

mkdir -p "${REPORT_ROOT}"
mkdir -p "${WORKTREE_ROOT}"

case_list="${REPORT_ROOT}/profile_cases.txt"
: > "${case_list}"
for name in ${PROFILE_CASES}; do
  line="$(awk -F, -v target="$name" '
    $1 == target { print; found=1; exit }
    END { if (!found) exit 1 }
  ' "${CASE_SOURCE}" || true)"
  if [ -z "${line}" ]; then
    echo "ERROR: case '${name}' not found in ${CASE_SOURCE}" >&2
    exit 1
  fi
  echo "${line}" >> "${case_list}"
done

labels=(
  "pre_tuning"
  "remove_sync"
  "cache_attrs"
  "fused_average"
  "reduce_scalar_copies"
  "current"
)

commits=(
  "ae3b683"
  "f9d7f0d"
  "8fed073"
  "fa7e860"
  "b44c7ab"
  "${CURRENT_SHA}"
)

descs=(
  "pre-tuning baseline"
  "remove redundant HIP device synchronize"
  "cache HIP device attributes"
  "fuse ROCm average iterate axpy updates"
  "reduce movement interaction scalar copies"
  "current HEAD"
)

{
  echo "== rocprof tuning milestone run =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "report root: ${REPORT_ROOT}"
  echo "worktree root: ${WORKTREE_ROOT}"
  echo "case source: ${CASE_SOURCE}"
  echo "profile cases: ${PROFILE_CASES}"
  echo "case timeout: ${CASE_TIMEOUT_SEC}"
  echo "HIP arch: ${HIP_ARCH}"
  echo "trace mode: ${TRACE_MODE}"
  echo "current sha: ${CURRENT_SHA}"
  echo
  echo "== milestones =="
  for i in "${!labels[@]}"; do
    echo "${labels[$i]},${commits[$i]},${descs[$i]}"
  done
  echo
  echo "== tools =="
  which rocprofv3 || true
  rocprofv3 --version || true
  which hipcc || true
  hipcc --version || true
  echo
  echo "== GPU =="
  rocminfo | grep -E "Name:|gfx" | head -n 80 || true
  rocm-smi || true
  echo
  echo "== cases =="
  cat "${case_list}"
} > "${REPORT_ROOT}/run_env.txt" 2>&1

trace_flag="--runtime-trace"
if [ "${TRACE_MODE}" = "sys" ]; then
  trace_flag="--sys-trace"
fi

run_one_version() {
  local label="$1"
  local commit="$2"
  local desc="$3"
  local wt="${WORKTREE_ROOT}/${label}"
  local out="${REPORT_ROOT}/${label}"
  local build_dir="build-rocm-rocprof-milestone"

  echo
  echo "============================================================"
  echo "== ${label}: ${commit} (${desc})"
  echo "============================================================"

  mkdir -p "${out}"

  if [ -d "${wt}" ]; then
    git -C "${ROOT}" worktree remove "${wt}" --force 2>/dev/null || rm -rf "${wt}"
  fi

  git -C "${ROOT}" worktree add --detach "${wt}" "${commit}" 2>&1 | tee "${out}/worktree.log"

  mkdir -p "${wt}/validation"
  cp "${case_list}" "${wt}/validation/profile_cases.txt"

  if [ -d "${ROOT}/validation/netlib" ]; then
    rm -rf "${wt}/validation/netlib"
    cp -a "${ROOT}/validation/netlib" "${wt}/validation/netlib"
  fi

  {
    echo "label=${label}"
    echo "commit=${commit}"
    echo "desc=${desc}"
    echo "worktree=${wt}"
    git -C "${wt}" log --oneline -n 8
  } > "${out}/version.txt" 2>&1

  pushd "${wt}" >/dev/null

  rm -rf "${build_dir}"

  local cmake_backend_args=()
  if grep -q "BUILD_ROCM" CMakeLists.txt; then
    cmake_backend_args+=("-DBUILD_CUDA=OFF" "-DBUILD_ROCM=ON")
  else
    cmake_backend_args+=("-DBUILD_CUDA=OFF" "-DBUILD_HIP=ON")
  fi

  set +e
  cmake -S . -B "${build_dir}" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    "${cmake_backend_args[@]}" \
    -DBUILD_APPS=OFF \
    -DBUILD_PYTHON=OFF \
    -DBUILD_TESTING=ON \
    -DCMAKE_PREFIX_PATH=/opt/rocm \
    -DCMAKE_HIP_ARCHITECTURES="${HIP_ARCH}" \
    > "${out}/configure.log" 2>&1
  local configure_code=$?
  set -e

  if [ "${configure_code}" -ne 0 ]; then
    echo "CONFIGURE_FAILED ${label} exit=${configure_code}"
    echo "${configure_code}" > "${out}/configure.exitcode"
    popd >/dev/null
    return 0
  fi
  echo "0" > "${out}/configure.exitcode"

  set +e
  cmake --build "${build_dir}" --target plc -j"$(nproc)" \
    > "${out}/build.log" 2>&1
  local build_code=$?
  set -e

  if [ "${build_code}" -ne 0 ]; then
    echo "BUILD_FAILED ${label} exit=${build_code}"
    echo "${build_code}" > "${out}/build.exitcode"
    popd >/dev/null
    return 0
  fi
  echo "0" > "${out}/build.exitcode"

  local plc="${build_dir}/bin/plc"
  if [ ! -x "${plc}" ]; then
    echo "MISSING_PLC ${plc}"
    echo "127" > "${out}/build.exitcode"
    popd >/dev/null
    return 0
  fi

  while IFS=, read -r name mps_path iter tier; do
    [ -z "${name// }" ] && continue
    [[ "${name}" =~ ^# ]] && continue

    local case_dir="${out}/${name}"
    local trace_dir="${case_dir}/trace"
    mkdir -p "${trace_dir}"

    echo
    echo "== ${label} / ${name} (${tier}) =="
    echo "mps: ${mps_path}"
    echo "iter: ${iter}"
    echo "trace dir: ${trace_dir}"

    local json="${case_dir}/${name}_rocm.json"
    local log="${case_dir}/${name}_rocm.log"
    local exitcode="${case_dir}/${name}_rocm.exitcode"

    if [ ! -f "${mps_path}" ]; then
      echo "MISSING_MPS ${mps_path}" | tee "${log}"
      echo "127" > "${exitcode}"
      continue
    fi

    set +e
    timeout "${CASE_TIMEOUT_SEC}" rocprofv3 "${trace_flag}" \
      --output-format csv \
      --output-directory "${trace_dir}" \
      --output-file "trace" \
      -- "${plc}" \
        -fname "${mps_path}" \
        -out "${json}" \
        -nIterLim "${iter}" \
      > "${log}" 2>&1
    local code=$?
    set -e

    echo "${code}" > "${exitcode}"
    echo "exit=${code}"
    find "${trace_dir}" -maxdepth 3 -type f | sort > "${case_dir}/trace_files.txt" || true
  done < "validation/profile_cases.txt"

  popd >/dev/null
}

for i in "${!labels[@]}"; do
  run_one_version "${labels[$i]}" "${commits[$i]}" "${descs[$i]}"
done

summarizer="${ROOT}/scripts/summarize_rocprofv3_milestones.py"
if [ ! -x "${summarizer}" ]; then
  echo "ERROR: missing executable summarizer: ${summarizer}" >&2
  echo "Copy summarize_rocprofv3_milestones.py into scripts/ and chmod +x it." >&2
  exit 1
fi

python3 "${summarizer}" "${REPORT_ROOT}"

echo "${REPORT_ROOT}" > "${ROOT}/validation/results/latest_rocprof_tuning_milestones.txt"

echo
echo "== final milestone trace summary =="
cat "${REPORT_ROOT}/trace_milestone_summary.md"

echo
echo "Worktrees kept under: ${WORKTREE_ROOT}"
echo "To remove them after inspection:"
echo "  for d in ${WORKTREE_ROOT}/*; do git -C ${ROOT} worktree remove \"\$d\" --force 2>/dev/null || true; done"
echo "  rm -rf ${WORKTREE_ROOT}"
