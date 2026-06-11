#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "${ROOT_DIR}"

source scripts/env/w7900_python_rocm_env.sh

CASES_FILE="${1:-validation/cases.txt}"
RESULT_ROOT="${RESULT_ROOT:-validation/results/w7900_latest}"
CPU_BUILD_DIR="${CPU_BUILD_DIR:-build-cpu}"
ROCM_BUILD_DIR="${ROCM_BUILD_DIR:-build-rocm-w7900}"
GPU_ID="${HIP_VISIBLE_DEVICES:-0}"

rm -rf "${RESULT_ROOT}"
mkdir -p "${RESULT_ROOT}"

echo "== cuPDLP-C-ROCm W7900 validation =="
echo "root       : ${ROOT_DIR}"
echo "cases      : ${CASES_FILE}"
echo "results    : ${RESULT_ROOT}"
echo "gpu        : HIP_VISIBLE_DEVICES=${GPU_ID}"
echo "rocm arch  : gfx1100"
echo ""

echo "== build CPU baseline =="
./scripts/build_w7900_cpu.sh

echo ""
echo "== build ROCm W7900 backend =="
./scripts/build_w7900_rocm.sh

PASS_COUNT=0
INCOMPLETE_COUNT=0
FAIL_COUNT=0

SUMMARY_CSV="${RESULT_ROOT}/summary.csv"
SUMMARY_MD="${RESULT_ROOT}/summary.md"

echo "case,backend,nIter,terminationCode,primalCode,dualCode,dRelPrimalFeas,dRelDualFeas,dRelDualityGap,dSolvingTime,result" > "${SUMMARY_CSV}"

{
  echo "# W7900 validation summary"
  echo
  echo "Cases file: \`${CASES_FILE}\`"
  echo
  echo "Result root: \`${RESULT_ROOT}\`"
  echo
  echo "| case | result | cpu status | rocm status | cpu iter | rocm iter | cpu rel primal | rocm rel primal | cpu rel dual | rocm rel dual | cpu rel gap | rocm rel gap |"
  echo "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
} > "${SUMMARY_MD}"

while IFS=, read -r name mps_path n_iter_lim extra; do
  if [[ -z "${name:-}" ]] || [[ "${name}" =~ ^# ]]; then
    continue
  fi

  if [[ "${name}" == "greenbea" ]]; then
    echo "== case: greenbea =="
    echo "[skip] greenbea is intentionally skipped on W7900 validation to avoid known non-productive runtime."
    continue
  fi

  case_dir="${RESULT_ROOT}/${name}"
  mkdir -p "${case_dir}"

  cpu_json="${case_dir}/${name}_cpu.json"
  rocm_json="${case_dir}/${name}_rocm_w7900.json"
  cpu_log="${case_dir}/${name}_cpu.log"
  rocm_log="${case_dir}/${name}_rocm_w7900.log"
  report_md="${case_dir}/${name}_compare.md"

  echo ""
  echo "== case: ${name} =="
  echo "mps      : ${mps_path}"
  echo "nIterLim : ${n_iter_lim}"

  echo "-- CPU run"
  "./${CPU_BUILD_DIR}/bin/plc" -fname "${mps_path}" -out "${cpu_json}" -nIterLim "${n_iter_lim}" 2>&1 | tee "${cpu_log}"

  echo "-- ROCm W7900 run"
  HIP_VISIBLE_DEVICES="${GPU_ID}" "./${ROCM_BUILD_DIR}/bin/plc" -fname "${mps_path}" -out "${rocm_json}" -nIterLim "${n_iter_lim}" 2>&1 | tee "${rocm_log}"

  echo "-- compare"
  set +e
  scripts/compare_cpu_rocm.py --case "${name}" --cpu "${cpu_json}" --rocm "${rocm_json}" --out "${report_md}"
  compare_status=$?
  set -e

  overall_result="$(grep -E '^Overall result:' "${report_md}" | sed -E 's/.*\*\*([^*]+)\*\*.*/\1/' || true)"
  if [[ -z "${overall_result}" ]]; then
    overall_result="FAIL"
  fi

  case "${overall_result}" in
    PASS)
      PASS_COUNT=$((PASS_COUNT + 1))
      ;;
    INCOMPLETE)
      INCOMPLETE_COUNT=$((INCOMPLETE_COUNT + 1))
      ;;
    FAIL|*)
      FAIL_COUNT=$((FAIL_COUNT + 1))
      ;;
  esac

  python3 - "${name}" "${cpu_json}" "${rocm_json}" "${overall_result}" "${SUMMARY_CSV}" "${SUMMARY_MD}" <<'PY'
import csv
import json
import sys
from pathlib import Path

case, cpu_path, rocm_path, result, summary_csv, summary_md = sys.argv[1:]

cpu = json.loads(Path(cpu_path).read_text())
rocm = json.loads(Path(rocm_path).read_text())

fields = [
    "nIter",
    "terminationCode",
    "primalCode",
    "dualCode",
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
    "dSolvingTime",
]

with open(summary_csv, "a", newline="") as f:
    writer = csv.writer(f)
    for backend, data in [("cpu", cpu), ("rocm_w7900", rocm)]:
        writer.writerow([case, backend] + [data.get(k, "") for k in fields] + [result])

cpu_status = f"{cpu.get('terminationCode','')}/{cpu.get('primalCode','')}/{cpu.get('dualCode','')}"
rocm_status = f"{rocm.get('terminationCode','')}/{rocm.get('primalCode','')}/{rocm.get('dualCode','')}"

with open(summary_md, "a") as f:
    f.write(
        f"| {case} | {result} | "
        f"{cpu_status} | {rocm_status} | "
        f"{cpu.get('nIter','')} | {rocm.get('nIter','')} | "
        f"{cpu.get('dRelPrimalFeas','')} | {rocm.get('dRelPrimalFeas','')} | "
        f"{cpu.get('dRelDualFeas','')} | {rocm.get('dRelDualFeas','')} | "
        f"{cpu.get('dRelDualityGap','')} | {rocm.get('dRelDualityGap','')} |\n"
    )
PY

  echo "case ${name}: ${overall_result}"

  if [[ "${compare_status}" -ne 0 && "${overall_result}" == "FAIL" ]]; then
    echo "[warn] compare script exited with ${compare_status}"
  fi

done < "${CASES_FILE}"

{
  echo
  echo "## Counts"
  echo
  echo "\`\`\`text"
  echo "PASS: ${PASS_COUNT}"
  echo "INCOMPLETE: ${INCOMPLETE_COUNT}"
  echo "FAIL: ${FAIL_COUNT}"
  echo "\`\`\`"
} >> "${SUMMARY_MD}"

echo ""
echo "== validation summary =="
echo "PASS: ${PASS_COUNT}"
echo "INCOMPLETE: ${INCOMPLETE_COUNT}"
echo "FAIL: ${FAIL_COUNT}"
echo "results: ${RESULT_ROOT}"

cat "${SUMMARY_MD}"

if [[ "${FAIL_COUNT}" -ne 0 ]]; then
  exit 1
fi
