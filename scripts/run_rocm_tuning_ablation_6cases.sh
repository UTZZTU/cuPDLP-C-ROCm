#!/usr/bin/env bash
set -Eeuo pipefail

# Run ROCm tuning ablation across selected commits with the full 6-case quick set.
#
# Run from the current cuPDLP-C-ROCm repository root:
#   CASE_TIMEOUT_SEC=900 ./run_rocm_tuning_ablation_6cases.sh
#
# Outputs:
#   validation/results/tuning_ablation_6cases_<timestamp>/
#     ablation_summary.csv
#     ablation_summary.md
#     <label>/{configure.log,build.log,summary.csv,summary.md,...}

CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
HIP_ARCH="${HIP_ARCH:-gfx1150}"
ROOT="$(pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_ROOT="${ROOT}/validation/results/tuning_ablation_6cases_${STAMP}"
WORKTREE_ROOT="${WORKTREE_ROOT:-/tmp/cupdlp_rocm_tuning_ablation_6cases_${USER}_${STAMP}}"
CASE_FILE_NAME="cases_tuning_ablation_6cases.txt"

if [ ! -f "${ROOT}/CMakeLists.txt" ] || [ ! -d "${ROOT}/cupdlp" ]; then
  echo "ERROR: run this script from the cuPDLP-C-ROCm repository root." >&2
  exit 1
fi

mkdir -p "${REPORT_ROOT}"
mkdir -p "${WORKTREE_ROOT}"

CURRENT_SHA="$(git rev-parse HEAD)"

LABELS=(
  "pre_tuning"
  "remove_sync"
  "cache_attrs"
  "fused_average"
  "reduce_scalar_copies"
  "current"
)

COMMITS=(
  "ae3b683"
  "f9d7f0d"
  "8fed073"
  "fa7e860"
  "b44c7ab"
  "${CURRENT_SHA}"
)

DESCS=(
  "pre-tuning baseline"
  "remove redundant HIP device synchronize"
  "cache HIP device attributes"
  "fuse ROCm average iterate axpy updates"
  "reduce movement interaction scalar copies"
  "current HEAD"
)

cat > "${REPORT_ROOT}/${CASE_FILE_NAME}" <<'EOF_CASES'
afiro,example/afiro.mps,200000000,S
sc50b,validation/netlib/sc50b.mps,200000000,S
lotfi,validation/netlib/lotfi.mps,200000000,M
80bau3b,validation/netlib/80bau3b.mps,200000000,M
maros-r7,validation/netlib/maros-r7.mps,200000000,L
pilot87,validation/netlib/pilot87.mps,200000000,L
EOF_CASES

{
  echo "== ROCm tuning ablation 6-case run =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "report root: ${REPORT_ROOT}"
  echo "worktree root: ${WORKTREE_ROOT}"
  echo "case timeout: ${CASE_TIMEOUT_SEC}"
  echo "HIP arch: ${HIP_ARCH}"
  echo "current sha: ${CURRENT_SHA}"
  echo
  echo "== versions =="
  for i in "${!LABELS[@]}"; do
    echo "${LABELS[$i]},${COMMITS[$i]},${DESCS[$i]}"
  done
  echo
  echo "== ROCm/HIP =="
  which hipcc || true
  hipcc --version || true
  echo
  echo "== GPU =="
  rocm-smi || true
  echo
  echo "== CMake =="
  which cmake || true
  cmake --version || true
  echo
  echo "== cases =="
  cat "${REPORT_ROOT}/${CASE_FILE_NAME}"
} > "${REPORT_ROOT}/run_env.txt" 2>&1

run_one_version() {
  local label="$1"
  local commit="$2"
  local desc="$3"

  local wt="${WORKTREE_ROOT}/${label}"
  local out="${REPORT_ROOT}/${label}"
  local build_dir="build-rocm-ablation"

  echo
  echo "============================================================"
  echo "== ${label}: ${commit} (${desc})"
  echo "============================================================"

  mkdir -p "${out}"

  if [ -d "${wt}" ]; then
    git -C "${ROOT}" worktree remove "${wt}" --force 2>/dev/null || rm -rf "${wt}"
  fi

  git -C "${ROOT}" worktree add --detach "${wt}" "${commit}" 2>&1 | tee "${out}/worktree.log"

  {
    echo "label=${label}"
    echo "commit=${commit}"
    echo "desc=${desc}"
    echo "worktree=${wt}"
    echo
    git -C "${wt}" rev-parse HEAD
    git -C "${wt}" log --oneline -n 5
  } > "${out}/version.txt" 2>&1

  mkdir -p "${wt}/validation"
  cp "${REPORT_ROOT}/${CASE_FILE_NAME}" "${wt}/validation/${CASE_FILE_NAME}"

  if [ -d "${ROOT}/validation/netlib" ]; then
    rm -rf "${wt}/validation/netlib"
    cp -a "${ROOT}/validation/netlib" "${wt}/validation/netlib"
  fi

  {
    echo "== pwd =="
    pwd
    echo
    echo "== version =="
    cat "${out}/version.txt"
    echo
    echo "== case file =="
    cat "${wt}/validation/${CASE_FILE_NAME}"
  } > "${out}/run_env.txt" 2>&1

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
    mkdir -p "${case_dir}"
    local json="${case_dir}/${name}_rocm.json"
    local log="${case_dir}/${name}_rocm.log"
    local exitcode="${case_dir}/${name}_rocm.exitcode"

    echo "== ${label} / ${name} =="
    echo "mps: ${mps_path}"
    echo "iter: ${iter}"

    if [ ! -f "${mps_path}" ]; then
      echo "MISSING_MPS ${mps_path}" | tee "${log}"
      echo "127" > "${exitcode}"
      continue
    fi

    set +e
    timeout "${CASE_TIMEOUT_SEC}" "${plc}" \
      -fname "${mps_path}" \
      -out "${json}" \
      -nIterLim "${iter}" \
      > "${log}" 2>&1
    local code=$?
    set -e

    echo "${code}" > "${exitcode}"
    echo "exit=${code}"
  done < "validation/${CASE_FILE_NAME}"

  popd >/dev/null

  python3 - "${out}" "${REPORT_ROOT}/${CASE_FILE_NAME}" "${label}" "${commit}" "${desc}" <<'PY_SUM'
import csv, json, pathlib, sys

out = pathlib.Path(sys.argv[1])
case_file = pathlib.Path(sys.argv[2])
label, commit, desc = sys.argv[3], sys.argv[4], sys.argv[5]

rows = []
for line in case_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, path, iter_lim, tier = [x.strip() for x in line.split(",", 3)]
    case_dir = out / name
    json_path = case_dir / f"{name}_rocm.json"
    exit_path = case_dir / f"{name}_rocm.exitcode"
    log_path = case_dir / f"{name}_rocm.log"

    data = {}
    if json_path.exists() and json_path.stat().st_size > 0:
        try:
            data = json.loads(json_path.read_text())
        except Exception as exc:
            data = {"parse_error": str(exc)}

    rows.append({
        "label": label,
        "commit": commit,
        "desc": desc,
        "case": name,
        "tier": tier,
        "exitcode": exit_path.read_text().strip() if exit_path.exists() else "",
        "status": data.get("terminationCode", ""),
        "nIter": data.get("nIter", ""),
        "solve_time_sec": data.get("dSolvingTime", ""),
        "DeviceMatVecProdTime": data.get("DeviceMatVecProdTime", ""),
        "dRelPrimalFeas": data.get("dRelPrimalFeas", ""),
        "dRelDualFeas": data.get("dRelDualFeas", ""),
        "dRelDualityGap": data.get("dRelDualityGap", ""),
        "json": str(json_path) if json_path.exists() else "",
        "log": str(log_path) if log_path.exists() else "",
    })

fields = [
    "label","commit","desc","case","tier","exitcode","status","nIter",
    "solve_time_sec","DeviceMatVecProdTime","dRelPrimalFeas",
    "dRelDualFeas","dRelDualityGap","json","log"
]
with (out / "summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

with (out / "summary.md").open("w") as f:
    f.write(f"# ROCm tuning ablation 6-case summary: {label}\n\n")
    f.write(f"Commit: `{commit}`\n\n")
    f.write(f"Description: {desc}\n\n")
    f.write("| case | status | exit | iter | time | matvec | rel primal | rel dual | rel gap |\n")
    f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for r in rows:
        f.write(
            f"| {r['case']} | {r['status']} | {r['exitcode']} | {r['nIter']} | "
            f"{r['solve_time_sec']} | {r['DeviceMatVecProdTime']} | "
            f"{r['dRelPrimalFeas']} | {r['dRelDualFeas']} | {r['dRelDualityGap']} |\n"
        )
PY_SUM

  cat "${out}/summary.md"
}

for i in "${!LABELS[@]}"; do
  run_one_version "${LABELS[$i]}" "${COMMITS[$i]}" "${DESCS[$i]}"
done

python3 - "${REPORT_ROOT}" <<'PY_ALL'
import csv, pathlib, sys

root = pathlib.Path(sys.argv[1])
rows = []
for csv_path in sorted(root.glob("*/summary.csv")):
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        rows.extend(reader)

fields = [
    "label","commit","desc","case","tier","exitcode","status","nIter",
    "solve_time_sec","DeviceMatVecProdTime","dRelPrimalFeas",
    "dRelDualFeas","dRelDualityGap","json","log"
]
summary_csv = root / "ablation_summary.csv"
with summary_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

labels = []
cases = []
descs = {}
commits = {}
for r in rows:
    if r["label"] not in labels:
        labels.append(r["label"])
        descs[r["label"]] = r["desc"]
        commits[r["label"]] = r["commit"]
    if r["case"] not in cases:
        cases.append(r["case"])

times = {(r["label"], r["case"]): r["solve_time_sec"] for r in rows}
matvec = {(r["label"], r["case"]): r["DeviceMatVecProdTime"] for r in rows}
status = {(r["label"], r["case"]): r["status"] for r in rows}

summary_md = root / "ablation_summary.md"
with summary_md.open("w") as f:
    f.write("# ROCm tuning ablation 6-case summary\n\n")
    f.write(f"Run dir: `{root}`\n\n")

    f.write("## Milestones\n\n")
    f.write("| milestone | commit | meaning |\n")
    f.write("|---|---|---|\n")
    for label in labels:
        f.write(f"| {label} | `{commits.get(label, '')}` | {descs.get(label, '')} |\n")

    f.write("\n## Solve time by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(times.get((label, c), "") for c in cases) + " |\n")

    f.write("\n## DeviceMatVecProdTime by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(matvec.get((label, c), "") for c in cases) + " |\n")

    f.write("\n## Status by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(status.get((label, c), "") for c in cases) + " |\n")

print(f"ablation csv: {summary_csv}")
print(f"ablation md:  {summary_md}")
PY_ALL

echo "${REPORT_ROOT}" > "${ROOT}/validation/results/latest_tuning_ablation_6cases.txt"

echo
echo "== final ablation summary =="
cat "${REPORT_ROOT}/ablation_summary.md"

echo
echo "Worktrees kept under: ${WORKTREE_ROOT}"
echo "To remove them after inspection:"
echo "  for d in ${WORKTREE_ROOT}/*; do git -C ${ROOT} worktree remove \"\$d\" --force 2>/dev/null || true; done"
echo "  rm -rf ${WORKTREE_ROOT}"
