#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "${ROOT}"

source scripts/env/w7900_python_rocm_env.sh

REPEAT_N="${REPEAT_N:-3}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
CASE_SOURCE="${CASE_SOURCE:-validation/cases_benchmark_200m_w7900_27.txt}"
GPU_ID="${HIP_VISIBLE_DEVICES:-0}"
STAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_ROOT="${REPORT_ROOT:-validation/results/w7900_27cases_baseline_${STAMP}}"
BUILD_DIR="${BUILD_DIR:-build-rocm-w7900}"

if [[ ! -f "${CASE_SOURCE}" ]]; then
  echo "ERROR: missing case source: ${CASE_SOURCE}" >&2
  exit 1
fi

mkdir -p "${REPORT_ROOT}"

CURRENT_SHA="$(git rev-parse HEAD)"
CURRENT_BRANCH="$(git branch --show-current || true)"

{
  echo "== W7900 27-case repeated ROCm baseline =="
  echo "date: $(date)"
  echo "root: ${ROOT}"
  echo "branch: ${CURRENT_BRANCH}"
  echo "commit: ${CURRENT_SHA}"
  echo "report root: ${REPORT_ROOT}"
  echo "case source: ${CASE_SOURCE}"
  echo "repeat_n: ${REPEAT_N}"
  echo "case_timeout_sec: ${CASE_TIMEOUT_SEC}"
  echo "HIP_VISIBLE_DEVICES: ${GPU_ID}"
  echo "ROCm arch: gfx1100"
  echo
  echo "== ROCm/HIP =="
  which hipcc || true
  hipcc --version || true
  echo
  echo "== GPU agents =="
  rocm_agent_enumerator || true
  echo
  echo "== rocm-smi =="
  rocm-smi || true
  echo
  echo "== cases =="
  cat "${CASE_SOURCE}"
} > "${REPORT_ROOT}/run_env.txt" 2>&1

echo "== build ROCm W7900 backend =="
./scripts/build_w7900_rocm.sh 2>&1 | tee "${REPORT_ROOT}/build_rocm_w7900.log"

PLC="${BUILD_DIR}/bin/plc"
if [[ ! -x "${PLC}" ]]; then
  echo "ERROR: missing executable: ${PLC}" >&2
  exit 1
fi

RAW_CSV="${REPORT_ROOT}/raw_runs.csv"
AGG_CSV="${REPORT_ROOT}/aggregated_summary.csv"
SUMMARY_MD="${REPORT_ROOT}/summary.md"

echo "case,tier,repeat,exitcode,status,nIter,solve_time_sec,DeviceMatVecProdTime,Ax,Aty,dRelPrimalFeas,dRelDualFeas,dRelDualityGap,json,log" > "${RAW_CSV}"

while IFS=, read -r name mps_path iter_lim tier rest; do
  name="$(echo "${name:-}" | xargs)"
  mps_path="$(echo "${mps_path:-}" | xargs)"
  iter_lim="$(echo "${iter_lim:-}" | xargs)"
  tier="$(echo "${tier:-unknown}" | xargs)"

  if [[ -z "${name}" ]] || [[ "${name}" =~ ^# ]]; then
    continue
  fi

  if [[ "${name}" == "greenbea" ]]; then
    echo "[skip] greenbea"
    continue
  fi

  case_dir="${REPORT_ROOT}/${name}"
  mkdir -p "${case_dir}"

  echo
  echo "== case: ${name} =="
  echo "mps      : ${mps_path}"
  echo "nIterLim : ${iter_lim}"
  echo "tier     : ${tier}"

  if [[ ! -f "${mps_path}" ]]; then
    echo "[missing] ${mps_path}"
    for rep in $(seq 1 "${REPEAT_N}"); do
      log="${case_dir}/${name}_rocm_rep${rep}.log"
      echo "MISSING_MPS ${mps_path}" > "${log}"
      echo "${name},${tier},${rep},127,MISSING_MPS,,,,,,,,,," >> "${RAW_CSV}"
    done
    continue
  fi

  for rep in $(seq 1 "${REPEAT_N}"); do
    json="${case_dir}/${name}_rocm_rep${rep}.json"
    log="${case_dir}/${name}_rocm_rep${rep}.log"

    echo "-- repeat ${rep}/${REPEAT_N}"

    set +e
    HIP_VISIBLE_DEVICES="${GPU_ID}" timeout "${CASE_TIMEOUT_SEC}" "${PLC}" -fname "${mps_path}" -out "${json}" -nIterLim "${iter_lim}" > "${log}" 2>&1
    code=$?
    set -e

    python3 - "${name}" "${tier}" "${rep}" "${code}" "${json}" "${log}" "${RAW_CSV}" <<'PY'
import csv
import json
import sys
from pathlib import Path

case, tier, rep, code, json_path, log_path, raw_csv = sys.argv[1:]
json_file = Path(json_path)
data = {}

if json_file.exists() and json_file.stat().st_size > 0:
    try:
        data = json.loads(json_file.read_text())
    except Exception as exc:
        data = {"terminationCode": f"JSON_PARSE_ERROR:{exc}"}

row = {
    "case": case,
    "tier": tier,
    "repeat": rep,
    "exitcode": code,
    "status": data.get("terminationCode", ""),
    "nIter": data.get("nIter", ""),
    "solve_time_sec": data.get("dSolvingTime", ""),
    "DeviceMatVecProdTime": data.get("DeviceMatVecProdTime", ""),
    "Ax": data.get("Ax", ""),
    "Aty": data.get("Aty", ""),
    "dRelPrimalFeas": data.get("dRelPrimalFeas", ""),
    "dRelDualFeas": data.get("dRelDualFeas", ""),
    "dRelDualityGap": data.get("dRelDualityGap", ""),
    "json": json_path if json_file.exists() else "",
    "log": log_path,
}

fields = [
    "case",
    "tier",
    "repeat",
    "exitcode",
    "status",
    "nIter",
    "solve_time_sec",
    "DeviceMatVecProdTime",
    "Ax",
    "Aty",
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
    "json",
    "log",
]

with open(raw_csv, "a", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writerow(row)
PY

    echo "exit=${code}"
  done
done < "${CASE_SOURCE}"

python3 - "${RAW_CSV}" "${AGG_CSV}" "${SUMMARY_MD}" "${REPORT_ROOT}" "${CURRENT_SHA}" "${REPEAT_N}" "${CASE_TIMEOUT_SEC}" <<'PY'
import csv
import math
import statistics
import sys
from pathlib import Path

raw_csv, agg_csv, summary_md, report_root, commit, repeat_n, timeout_sec = sys.argv[1:]
raw_csv = Path(raw_csv)
agg_csv = Path(agg_csv)
summary_md = Path(summary_md)

rows = list(csv.DictReader(raw_csv.open()))

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
    cv = std / mean if mean else 0.0
    return {
        "n": len(vals),
        "mean": mean,
        "median": median,
        "std": std,
        "min": min(vals),
        "max": max(vals),
        "cv": cv,
    }

by_case = {}
for r in rows:
    by_case.setdefault(r["case"], []).append(r)

agg_rows = []
for case, case_rows in by_case.items():
    tier = case_rows[0].get("tier", "")
    solve = [safe_float(r.get("solve_time_sec")) for r in case_rows]
    matvec = [safe_float(r.get("DeviceMatVecProdTime")) for r in case_rows]
    rel_pf = [safe_float(r.get("dRelPrimalFeas")) for r in case_rows]
    rel_df = [safe_float(r.get("dRelDualFeas")) for r in case_rows]
    rel_gap = [safe_float(r.get("dRelDualityGap")) for r in case_rows]

    s_solve = stats(solve)
    s_matvec = stats(matvec)
    s_pf = stats(rel_pf)
    s_df = stats(rel_df)
    s_gap = stats(rel_gap)

    agg_rows.append({
        "case": case,
        "tier": tier,
        "repeat_n": repeat_n,
        "valid_n": s_solve["n"],
        "all_exitcodes": ";".join(r.get("exitcode", "") for r in case_rows),
        "all_statuses": ";".join(r.get("status", "") for r in case_rows),
        "all_nIter": ";".join(r.get("nIter", "") for r in case_rows),
        "median_solve_time_sec": s_solve["median"],
        "mean_solve_time_sec": s_solve["mean"],
        "std_solve_time_sec": s_solve["std"],
        "min_solve_time_sec": s_solve["min"],
        "max_solve_time_sec": s_solve["max"],
        "cv_solve_time": s_solve["cv"],
        "median_DeviceMatVecProdTime": s_matvec["median"],
        "mean_DeviceMatVecProdTime": s_matvec["mean"],
        "cv_DeviceMatVecProdTime": s_matvec["cv"],
        "median_dRelPrimalFeas": s_pf["median"],
        "median_dRelDualFeas": s_df["median"],
        "median_dRelDualityGap": s_gap["median"],
    })

agg_fields = [
    "case",
    "tier",
    "repeat_n",
    "valid_n",
    "all_exitcodes",
    "all_statuses",
    "all_nIter",
    "median_solve_time_sec",
    "mean_solve_time_sec",
    "std_solve_time_sec",
    "min_solve_time_sec",
    "max_solve_time_sec",
    "cv_solve_time",
    "median_DeviceMatVecProdTime",
    "mean_DeviceMatVecProdTime",
    "cv_DeviceMatVecProdTime",
    "median_dRelPrimalFeas",
    "median_dRelDualFeas",
    "median_dRelDualityGap",
]

with agg_csv.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=agg_fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(agg_rows)

status_counts = {}
for r in agg_rows:
    statuses = r["all_statuses"].split(";")
    key = ";".join(sorted(set(s for s in statuses if s)))
    status_counts[key] = status_counts.get(key, 0) + 1

with summary_md.open("w") as f:
    f.write("# W7900 27-case repeated ROCm baseline\n\n")
    f.write(f"Run directory: `{report_root}`\n\n")
    f.write(f"Commit: `{commit}`\n\n")
    f.write(f"Repeats per case: `{repeat_n}`\n\n")
    f.write(f"Timeout per repeat: `{timeout_sec}` seconds\n\n")
    f.write("Primary metric: median solve time across repeated ROCm/W7900 runs.\n\n")
    f.write(f"Raw CSV: [raw_runs.csv](raw_runs.csv)\n\n")
    f.write(f"Aggregated CSV: [aggregated_summary.csv](aggregated_summary.csv)\n\n")

    f.write("## Status counts\n\n")
    f.write("| status set | cases |\n")
    f.write("|---|---:|\n")
    for key, count in sorted(status_counts.items()):
        f.write(f"| {key} | {count} |\n")

    f.write("\n## Per-case aggregated results\n\n")
    f.write("| case | tier | valid n | median solve | mean solve | CV | median matvec | statuses | nIter |\n")
    f.write("|---|---|---:|---:|---:|---:|---:|---|---|\n")
    for r in agg_rows:
        f.write(
            f"| {r['case']} | {r['tier']} | {r['valid_n']} | "
            f"{r['median_solve_time_sec']} | {r['mean_solve_time_sec']} | "
            f"{r['cv_solve_time']} | {r['median_DeviceMatVecProdTime']} | "
            f"{r['all_statuses']} | {r['all_nIter']} |\n"
        )

print(f"[done] wrote {agg_csv}")
print(f"[done] wrote {summary_md}")
PY

echo
echo "== W7900 27-case baseline summary =="
cat "${SUMMARY_MD}"
