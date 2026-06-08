#!/usr/bin/env bash
set -Eeuo pipefail

# Compare current HEAD against the reduce_scalar_copies milestone on the full
# non-greenbea benchmark set, with repeated ROCm/HIP runs.
#
# Run from the current cuPDLP-C-ROCm repository root:
#   REPEAT_N=3 CASE_TIMEOUT_SEC=900 ./scripts/run_rocm_current_vs_reduce_27cases_repeats.sh
#
# Inputs:
#   validation/cases_benchmark_200m.txt
#
# Excludes:
#   greenbea
#
# Outputs:
#   validation/results/current_vs_reduce_27cases_repeats_<timestamp>/
#     raw_runs.csv
#     aggregated_summary.csv
#     comparison_summary.csv
#     comparison_summary.md

REPEAT_N="${REPEAT_N:-3}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
HIP_ARCH="${HIP_ARCH:-gfx1150}"
ROOT="$(pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_ROOT="${ROOT}/validation/results/current_vs_reduce_27cases_repeats_${STAMP}"
WORKTREE_ROOT="${WORKTREE_ROOT:-/tmp/cupdlp_rocm_current_vs_reduce_27cases_${USER}_${STAMP}}"
CASE_SOURCE="${CASE_SOURCE:-validation/cases_benchmark_200m.txt}"
CASE_FILE_NAME="cases_current_vs_reduce_27cases.txt"

if [ ! -f "${ROOT}/CMakeLists.txt" ] || [ ! -d "${ROOT}/cupdlp" ]; then
  echo "ERROR: run this script from the cuPDLP-C-ROCm repository root." >&2
  exit 1
fi

if [ ! -f "${CASE_SOURCE}" ]; then
  echo "ERROR: missing case source: ${CASE_SOURCE}" >&2
  exit 1
fi

mkdir -p "${REPORT_ROOT}"
mkdir -p "${WORKTREE_ROOT}"

CURRENT_SHA="$(git rev-parse HEAD)"
BASE_SHA="b44c7ab"

# Filter out greenbea and comments/blank lines.
awk -F, '
  BEGIN { OFS="," }
  /^[[:space:]]*#/ { next }
  /^[[:space:]]*$/ { next }
  {
    name=$1
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", name)
    if (name == "greenbea") next
    print $0
  }
' "${CASE_SOURCE}" > "${REPORT_ROOT}/${CASE_FILE_NAME}"

CASE_COUNT="$(wc -l < "${REPORT_ROOT}/${CASE_FILE_NAME}" | tr -d ' ')"

if [ "${CASE_COUNT}" -lt 1 ]; then
  echo "ERROR: no cases after filtering ${CASE_SOURCE}" >&2
  exit 1
fi

LABELS=(
  "reduce_scalar_copies"
  "current"
)

COMMITS=(
  "${BASE_SHA}"
  "${CURRENT_SHA}"
)

DESCS=(
  "fastest observed ROCm tuning milestone from prior ablation"
  "current HEAD with CPU/CUDA/ROCm engineering changes"
)

{
  echo "== ROCm current-vs-reduce repeated run =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "report root: ${REPORT_ROOT}"
  echo "worktree root: ${WORKTREE_ROOT}"
  echo "repeat_n: ${REPEAT_N}"
  echo "case timeout: ${CASE_TIMEOUT_SEC}"
  echo "HIP arch: ${HIP_ARCH}"
  echo "case source: ${CASE_SOURCE}"
  echo "case count after excluding greenbea: ${CASE_COUNT}"
  echo "current sha: ${CURRENT_SHA}"
  echo "base sha: ${BASE_SHA}"
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
  local build_dir="build-rocm-current-vs-reduce"

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
    git -C "${wt}" log --oneline -n 8
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
import csv, json, pathlib, statistics, sys

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
    exitcodes = []
    rel_pf = []
    rel_df = []
    rel_gap = []

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
    f.write(f"# ROCm current-vs-reduce repeated summary: {label}\n\n")
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
import csv, math, pathlib, sys

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

by_key = {(r["label"], r["case"]): r for r in agg_rows}
cases = []
for r in agg_rows:
    if r["case"] not in cases:
        cases.append(r["case"])

comp_rows = []
speedups = []
current_slower_over_2pct = []

for case in cases:
    base = by_key.get(("reduce_scalar_copies", case))
    cur = by_key.get(("current", case))
    if not base or not cur:
        continue
    try:
        base_t = float(base["median_solve_time_sec"])
        cur_t = float(cur["median_solve_time_sec"])
        speedup = base_t / cur_t if cur_t else ""
        slowdown_pct = (cur_t / base_t - 1.0) * 100.0 if base_t else ""
    except Exception:
        base_t = cur_t = speedup = slowdown_pct = ""

    try:
        base_mv = float(base["median_DeviceMatVecProdTime"])
        cur_mv = float(cur["median_DeviceMatVecProdTime"])
        mv_slowdown_pct = (cur_mv / base_mv - 1.0) * 100.0 if base_mv else ""
    except Exception:
        base_mv = cur_mv = mv_slowdown_pct = ""

    if isinstance(speedup, float) and speedup > 0:
        speedups.append(speedup)
    if isinstance(slowdown_pct, float) and slowdown_pct > 2.0:
        current_slower_over_2pct.append(case)

    comp_rows.append({
        "case": case,
        "tier": base["tier"],
        "base_median_solve_time_sec": base["median_solve_time_sec"],
        "current_median_solve_time_sec": cur["median_solve_time_sec"],
        "base_over_current_speedup": speedup,
        "current_slowdown_pct_vs_base": slowdown_pct,
        "base_cv": base["cv_solve_time"],
        "current_cv": cur["cv_solve_time"],
        "base_median_DeviceMatVecProdTime": base["median_DeviceMatVecProdTime"],
        "current_median_DeviceMatVecProdTime": cur["median_DeviceMatVecProdTime"],
        "current_matvec_slowdown_pct_vs_base": mv_slowdown_pct,
        "base_statuses": base["all_statuses"],
        "current_statuses": cur["all_statuses"],
        "base_nIter": base["all_nIter"],
        "current_nIter": cur["all_nIter"],
    })

comp_fields = [
    "case","tier","base_median_solve_time_sec","current_median_solve_time_sec",
    "base_over_current_speedup","current_slowdown_pct_vs_base","base_cv","current_cv",
    "base_median_DeviceMatVecProdTime","current_median_DeviceMatVecProdTime",
    "current_matvec_slowdown_pct_vs_base","base_statuses","current_statuses",
    "base_nIter","current_nIter"
]

comp_csv = root / "comparison_summary.csv"
with comp_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=comp_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(comp_rows)

geo = ""
if speedups:
    geo = math.exp(sum(math.log(x) for x in speedups) / len(speedups))

md = root / "comparison_summary.md"
with md.open("w") as f:
    f.write("# ROCm current vs reduce_scalar_copies repeated comparison\n\n")
    f.write(f"Run dir: `{root}`\n\n")
    f.write("Base: `reduce_scalar_copies` (`b44c7ab`).\n\n")
    f.write("Current: repository `HEAD` at run time.\n\n")
    f.write("Primary metric: median solve time across repeated runs.\n\n")
    f.write(f"Geometric mean speedup of base over current: `{geo}`.\n\n")
    if current_slower_over_2pct:
        f.write("Cases where current is slower than base by more than 2%:\n\n")
        for c in current_slower_over_2pct:
            f.write(f"- `{c}`\n")
        f.write("\n")
    else:
        f.write("No case exceeded the 2% current-slower-than-base threshold.\n\n")

    f.write("| case | tier | base median | current median | base/current speedup | current slowdown % | base CV | current CV | base matvec | current matvec | matvec slowdown % |\n")
    f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    for r in comp_rows:
        f.write(
            f"| {r['case']} | {r['tier']} | {r['base_median_solve_time_sec']} | "
            f"{r['current_median_solve_time_sec']} | {r['base_over_current_speedup']} | "
            f"{r['current_slowdown_pct_vs_base']} | {r['base_cv']} | {r['current_cv']} | "
            f"{r['base_median_DeviceMatVecProdTime']} | {r['current_median_DeviceMatVecProdTime']} | "
            f"{r['current_matvec_slowdown_pct_vs_base']} |\n"
        )

print(f"raw csv: {raw_csv}")
print(f"aggregated csv: {agg_csv}")
print(f"comparison csv: {comp_csv}")
print(f"comparison md:  {md}")
PY_ALL

echo "${REPORT_ROOT}" > "${ROOT}/validation/results/latest_current_vs_reduce_27cases_repeats.txt"

echo
echo "== final comparison summary =="
cat "${REPORT_ROOT}/comparison_summary.md"

echo
echo "Worktrees kept under: ${WORKTREE_ROOT}"
echo "To remove them after inspection:"
echo "  for d in ${WORKTREE_ROOT}/*; do git -C ${ROOT} worktree remove \"\$d\" --force 2>/dev/null || true; done"
echo "  rm -rf ${WORKTREE_ROOT}"
