#!/usr/bin/env bash
set -Eeuo pipefail

# Run ROCm tuning ablation across selected commits with 6 cases and repeated runs.
#
# Run from the current cuPDLP-C-ROCm repository root:
#   REPEAT_N=5 CASE_TIMEOUT_SEC=900 ./run_rocm_tuning_ablation_6cases_repeats.sh
#
# Outputs:
#   validation/results/tuning_ablation_6cases_repeats_<timestamp>/
#     raw_runs.csv
#     aggregated_summary.csv
#     aggregated_summary.md
#     <label>/{configure.log,build.log,summary_raw.csv,summary_aggregated.csv,...}

REPEAT_N="${REPEAT_N:-5}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
HIP_ARCH="${HIP_ARCH:-gfx1150}"
ROOT="$(pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_ROOT="${ROOT}/validation/results/tuning_ablation_6cases_repeats_${STAMP}"
WORKTREE_ROOT="${WORKTREE_ROOT:-/tmp/cupdlp_rocm_tuning_ablation_6cases_repeats_${USER}_${STAMP}}"
CASE_FILE_NAME="cases_tuning_ablation_6cases_repeats.txt"

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
  echo "== ROCm tuning ablation 6-case repeated run =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "report root: ${REPORT_ROOT}"
  echo "worktree root: ${WORKTREE_ROOT}"
  echo "repeat_n: ${REPEAT_N}"
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
  local build_dir="build-rocm-ablation-repeats"

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

    echo
    echo "== ${label} / ${name} (${tier}) =="
    echo "mps: ${mps_path}"
    echo "iter: ${iter}"

    if [ ! -f "${mps_path}" ]; then
      for rep in $(seq 1 "${REPEAT_N}"); do
        local log="${case_dir}/${name}_rocm_rep${rep}.log"
        echo "MISSING_MPS ${mps_path}" | tee "${log}"
        echo "127" > "${case_dir}/${name}_rocm_rep${rep}.exitcode"
      done
      continue
    fi

    for rep in $(seq 1 "${REPEAT_N}"); do
      local json="${case_dir}/${name}_rocm_rep${rep}.json"
      local log="${case_dir}/${name}_rocm_rep${rep}.log"
      local exitcode="${case_dir}/${name}_rocm_rep${rep}.exitcode"

      echo "-- repeat ${rep}/${REPEAT_N}"

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
    done
  done < "validation/${CASE_FILE_NAME}"

  popd >/dev/null

  python3 - "${out}" "${REPORT_ROOT}/${CASE_FILE_NAME}" "${label}" "${commit}" "${desc}" "${REPEAT_N}" <<'PY_SUM'
import csv, json, math, pathlib, statistics, sys

out = pathlib.Path(sys.argv[1])
case_file = pathlib.Path(sys.argv[2])
label, commit, desc = sys.argv[3], sys.argv[4], sys.argv[5]
repeat_n = int(sys.argv[6])

raw_rows = []
agg_rows = []

def safe_float(x):
    if x in ("", None):
        return None
    try:
        return float(x)
    except Exception:
        return None

def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"n": 0, "mean": "", "median": "", "std": "", "min": "", "max": "", "cv": ""}
    mean = statistics.mean(vals)
    median = statistics.median(vals)
    std = statistics.stdev(vals) if len(vals) > 1 else 0.0
    cv = (std / mean) if mean else 0.0
    return {
        "n": len(vals),
        "mean": mean,
        "median": median,
        "std": std,
        "min": min(vals),
        "max": max(vals),
        "cv": cv,
    }

for line in case_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, path, iter_lim, tier = [x.strip() for x in line.split(",", 3)]

    solve_times = []
    matvec_times = []
    statuses = []
    niters = []
    rel_pf = []
    rel_df = []
    rel_gap = []
    exitcodes = []

    for rep in range(1, repeat_n + 1):
        case_dir = out / name
        json_path = case_dir / f"{name}_rocm_rep{rep}.json"
        exit_path = case_dir / f"{name}_rocm_rep{rep}.exitcode"
        log_path = case_dir / f"{name}_rocm_rep{rep}.log"

        data = {}
        if json_path.exists() and json_path.stat().st_size > 0:
            try:
                data = json.loads(json_path.read_text())
            except Exception as exc:
                data = {"parse_error": str(exc)}

        exitcode = exit_path.read_text().strip() if exit_path.exists() else ""
        status = data.get("terminationCode", "")
        niter = data.get("nIter", "")
        solve = data.get("dSolvingTime", "")
        matvec = data.get("DeviceMatVecProdTime", "")

        raw_rows.append({
            "label": label,
            "commit": commit,
            "desc": desc,
            "case": name,
            "tier": tier,
            "repeat": rep,
            "exitcode": exitcode,
            "status": status,
            "nIter": niter,
            "solve_time_sec": solve,
            "DeviceMatVecProdTime": matvec,
            "dRelPrimalFeas": data.get("dRelPrimalFeas", ""),
            "dRelDualFeas": data.get("dRelDualFeas", ""),
            "dRelDualityGap": data.get("dRelDualityGap", ""),
            "json": str(json_path) if json_path.exists() else "",
            "log": str(log_path) if log_path.exists() else "",
        })

        exitcodes.append(exitcode)
        statuses.append(status)
        niters.append(str(niter))
        solve_times.append(safe_float(solve))
        matvec_times.append(safe_float(matvec))
        rel_pf.append(safe_float(data.get("dRelPrimalFeas", "")))
        rel_df.append(safe_float(data.get("dRelDualFeas", "")))
        rel_gap.append(safe_float(data.get("dRelDualityGap", "")))

    s_solve = stats(solve_times)
    s_matvec = stats(matvec_times)

    agg_rows.append({
        "label": label,
        "commit": commit,
        "desc": desc,
        "case": name,
        "tier": tier,
        "repeat_n": repeat_n,
        "valid_n": s_solve["n"],
        "all_statuses": ";".join(statuses),
        "all_exitcodes": ";".join(exitcodes),
        "all_nIter": ";".join(niters),
        "median_solve_time_sec": s_solve["median"],
        "mean_solve_time_sec": s_solve["mean"],
        "std_solve_time_sec": s_solve["std"],
        "min_solve_time_sec": s_solve["min"],
        "max_solve_time_sec": s_solve["max"],
        "cv_solve_time": s_solve["cv"],
        "median_DeviceMatVecProdTime": s_matvec["median"],
        "mean_DeviceMatVecProdTime": s_matvec["mean"],
        "std_DeviceMatVecProdTime": s_matvec["std"],
        "min_DeviceMatVecProdTime": s_matvec["min"],
        "max_DeviceMatVecProdTime": s_matvec["max"],
        "cv_DeviceMatVecProdTime": s_matvec["cv"],
        "median_dRelPrimalFeas": stats(rel_pf)["median"],
        "median_dRelDualFeas": stats(rel_df)["median"],
        "median_dRelDualityGap": stats(rel_gap)["median"],
    })

raw_fields = [
    "label","commit","desc","case","tier","repeat","exitcode","status","nIter",
    "solve_time_sec","DeviceMatVecProdTime","dRelPrimalFeas","dRelDualFeas",
    "dRelDualityGap","json","log"
]
agg_fields = [
    "label","commit","desc","case","tier","repeat_n","valid_n","all_statuses",
    "all_exitcodes","all_nIter","median_solve_time_sec","mean_solve_time_sec",
    "std_solve_time_sec","min_solve_time_sec","max_solve_time_sec","cv_solve_time",
    "median_DeviceMatVecProdTime","mean_DeviceMatVecProdTime","std_DeviceMatVecProdTime",
    "min_DeviceMatVecProdTime","max_DeviceMatVecProdTime","cv_DeviceMatVecProdTime",
    "median_dRelPrimalFeas","median_dRelDualFeas","median_dRelDualityGap"
]

with (out / "summary_raw.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=raw_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(raw_rows)

with (out / "summary_aggregated.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=agg_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(agg_rows)

with (out / "summary_aggregated.md").open("w") as f:
    f.write(f"# ROCm tuning ablation repeated summary: {label}\n\n")
    f.write(f"Commit: `{commit}`\n\n")
    f.write(f"Description: {desc}\n\n")
    f.write(f"Repeats per case: `{repeat_n}`\n\n")
    f.write("| case | valid n | median time | mean time | std | CV | min | max | median matvec | statuses |\n")
    f.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
    for r in agg_rows:
        f.write(
            f"| {r['case']} | {r['valid_n']} | {r['median_solve_time_sec']} | "
            f"{r['mean_solve_time_sec']} | {r['std_solve_time_sec']} | "
            f"{r['cv_solve_time']} | {r['min_solve_time_sec']} | {r['max_solve_time_sec']} | "
            f"{r['median_DeviceMatVecProdTime']} | {r['all_statuses']} |\n"
        )
PY_SUM

  cat "${out}/summary_aggregated.md"
}

for i in "${!LABELS[@]}"; do
  run_one_version "${LABELS[$i]}" "${COMMITS[$i]}" "${DESCS[$i]}"
done

python3 - "${REPORT_ROOT}" <<'PY_ALL'
import csv, pathlib, sys

root = pathlib.Path(sys.argv[1])
raw_rows = []
agg_rows = []

for csv_path in sorted(root.glob("*/summary_raw.csv")):
    with csv_path.open() as f:
        raw_rows.extend(csv.DictReader(f))

for csv_path in sorted(root.glob("*/summary_aggregated.csv")):
    with csv_path.open() as f:
        agg_rows.extend(csv.DictReader(f))

raw_fields = [
    "label","commit","desc","case","tier","repeat","exitcode","status","nIter",
    "solve_time_sec","DeviceMatVecProdTime","dRelPrimalFeas","dRelDualFeas",
    "dRelDualityGap","json","log"
]
agg_fields = [
    "label","commit","desc","case","tier","repeat_n","valid_n","all_statuses",
    "all_exitcodes","all_nIter","median_solve_time_sec","mean_solve_time_sec",
    "std_solve_time_sec","min_solve_time_sec","max_solve_time_sec","cv_solve_time",
    "median_DeviceMatVecProdTime","mean_DeviceMatVecProdTime","std_DeviceMatVecProdTime",
    "min_DeviceMatVecProdTime","max_DeviceMatVecProdTime","cv_DeviceMatVecProdTime",
    "median_dRelPrimalFeas","median_dRelDualFeas","median_dRelDualityGap"
]

raw_csv = root / "raw_runs.csv"
with raw_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=raw_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(raw_rows)

agg_csv = root / "aggregated_summary.csv"
with agg_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=agg_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(agg_rows)

labels = []
cases = []
descs = {}
commits = {}
for r in agg_rows:
    if r["label"] not in labels:
        labels.append(r["label"])
        descs[r["label"]] = r["desc"]
        commits[r["label"]] = r["commit"]
    if r["case"] not in cases:
        cases.append(r["case"])

median_time = {(r["label"], r["case"]): r["median_solve_time_sec"] for r in agg_rows}
mean_time = {(r["label"], r["case"]): r["mean_solve_time_sec"] for r in agg_rows}
cv_time = {(r["label"], r["case"]): r["cv_solve_time"] for r in agg_rows}
median_matvec = {(r["label"], r["case"]): r["median_DeviceMatVecProdTime"] for r in agg_rows}

md = root / "aggregated_summary.md"
with md.open("w") as f:
    f.write("# ROCm tuning ablation 6-case repeated summary\n\n")
    f.write(f"Run dir: `{root}`\n\n")
    f.write("Primary metric: median solve time across repeated runs.\n\n")

    f.write("## Milestones\n\n")
    f.write("| milestone | commit | meaning |\n")
    f.write("|---|---|---|\n")
    for label in labels:
        f.write(f"| {label} | `{commits.get(label, '')}` | {descs.get(label, '')} |\n")

    f.write("\n## Median solve time by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(median_time.get((label, c), "") for c in cases) + " |\n")

    f.write("\n## Mean solve time by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(mean_time.get((label, c), "") for c in cases) + " |\n")

    f.write("\n## CV of solve time by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(cv_time.get((label, c), "") for c in cases) + " |\n")

    f.write("\n## Median DeviceMatVecProdTime by tuning milestone\n\n")
    f.write("| milestone | " + " | ".join(cases) + " |\n")
    f.write("|---" + "|---:" * len(cases) + "|\n")
    for label in labels:
        f.write("| " + label + " | " + " | ".join(median_matvec.get((label, c), "") for c in cases) + " |\n")

print(f"raw csv: {raw_csv}")
print(f"aggregated csv: {agg_csv}")
print(f"aggregated md:  {md}")
PY_ALL

echo "${REPORT_ROOT}" > "${ROOT}/validation/results/latest_tuning_ablation_6cases_repeats.txt"

echo
echo "== final repeated ablation summary =="
cat "${REPORT_ROOT}/aggregated_summary.md"

echo
echo "Worktrees kept under: ${WORKTREE_ROOT}"
echo "To remove them after inspection:"
echo "  for d in ${WORKTREE_ROOT}/*; do git -C ${ROOT} worktree remove \"\$d\" --force 2>/dev/null || true; done"
echo "  rm -rf ${WORKTREE_ROOT}"
