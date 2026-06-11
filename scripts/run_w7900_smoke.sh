#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

source scripts/env/w7900_python_rocm_env.sh

RESULT_ROOT="${W7900_RESULT_ROOT:-/app/cupdlp_w7900/results}"
LOG_ROOT="${W7900_LOG_ROOT:-/app/cupdlp_w7900/logs}"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="${RESULT_ROOT}/w7900_smoke_${STAMP}"

CPU_BIN="${REPO_ROOT}/build-cpu/bin/plc"
ROCM_BIN="${REPO_ROOT}/build-rocm-w7900/bin/plc"
CASE_NAME="afiro"
CASE_FILE="${REPO_ROOT}/example/afiro.mps"
ITER_LIM="${W7900_SMOKE_ITER_LIM:-200}"
GPU_ID="${HIP_VISIBLE_DEVICES:-0}"

mkdir -p "${OUT_DIR}" "${LOG_ROOT}"

echo "[info] repo: ${REPO_ROOT}"
echo "[info] output: ${OUT_DIR}"
echo "[info] case: ${CASE_FILE}"
echo "[info] iteration limit: ${ITER_LIM}"
echo "[info] HIP_VISIBLE_DEVICES: ${GPU_ID}"

if [[ ! -x "${CPU_BIN}" ]]; then
  echo "[info] CPU plc not found, building CPU baseline..."
  ./scripts/build_w7900_cpu.sh 2>&1 | tee "${LOG_ROOT}/build_w7900_cpu_for_smoke_${STAMP}.log"
fi

if [[ ! -x "${ROCM_BIN}" ]]; then
  echo "[info] ROCm plc not found, building ROCm W7900 backend..."
  ./scripts/build_w7900_rocm.sh 2>&1 | tee "${LOG_ROOT}/build_w7900_rocm_for_smoke_${STAMP}.log"
fi

echo "[info] running CPU smoke..."
"${CPU_BIN}" -fname "${CASE_FILE}" -out "${OUT_DIR}/${CASE_NAME}_cpu.json" -nIterLim "${ITER_LIM}" 2>&1 | tee "${OUT_DIR}/${CASE_NAME}_cpu.log"

echo "[info] running ROCm smoke..."
HIP_VISIBLE_DEVICES="${GPU_ID}" "${ROCM_BIN}" -fname "${CASE_FILE}" -out "${OUT_DIR}/${CASE_NAME}_rocm_w7900.json" -nIterLim "${ITER_LIM}" 2>&1 | tee "${OUT_DIR}/${CASE_NAME}_rocm_w7900.log"

python3 - "${OUT_DIR}" "${CASE_NAME}" <<'PY'
import csv
import json
import sys
from pathlib import Path

out_dir = Path(sys.argv[1])
case_name = sys.argv[2]

cpu_path = out_dir / f"{case_name}_cpu.json"
rocm_path = out_dir / f"{case_name}_rocm_w7900.json"

cpu = json.loads(cpu_path.read_text())
rocm = json.loads(rocm_path.read_text())

fields = [
    "solver",
    "nIter",
    "nAxCalls",
    "nAtyCalls",
    "dSolvingTime",
    "dScalingTime",
    "dPrimalObj",
    "dDualObj",
    "dPrimalFeas",
    "dDualFeas",
    "dRelPrimalFeas",
    "dRelDualFeas",
    "dRelDualityGap",
    "terminationCode",
    "terminationIterate",
    "primalCode",
    "dualCode",
]

summary_csv = out_dir / "summary.csv"
with summary_csv.open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["case", "backend"] + fields)
    for backend, data in [("cpu", cpu), ("rocm_w7900", rocm)]:
        writer.writerow([case_name, backend] + [data.get(k, "") for k in fields])

summary_md = out_dir / "summary.md"
with summary_md.open("w") as f:
    f.write("# W7900 smoke validation summary\n\n")
    f.write(f"Output directory: `{out_dir}`\n\n")
    f.write("| case | backend | nIter | termination | primal | dual | rel primal | rel dual | rel gap | solve time |\n")
    f.write("|---|---|---:|---|---|---|---:|---:|---:|---:|\n")

    for backend, data in [("cpu", cpu), ("rocm_w7900", rocm)]:
        f.write(
            f"| {case_name} | {backend} | "
            f"{data.get('nIter', '')} | "
            f"{data.get('terminationCode', '')} | "
            f"{data.get('primalCode', '')} | "
            f"{data.get('dualCode', '')} | "
            f"{data.get('dRelPrimalFeas', '')} | "
            f"{data.get('dRelDualFeas', '')} | "
            f"{data.get('dRelDualityGap', '')} | "
            f"{data.get('dSolvingTime', '')} |\n"
        )

    f.write("\n## Interpretation\n\n")
    if (
        cpu.get("terminationCode") == rocm.get("terminationCode")
        and cpu.get("primalCode") == rocm.get("primalCode")
        and cpu.get("dualCode") == rocm.get("dualCode")
    ):
        f.write("CPU and ROCm/W7900 smoke validation reached matching termination, primal, and dual statuses.\n")
    else:
        f.write("CPU and ROCm/W7900 statuses differ. Inspect JSON files and logs before treating this run as PASS.\n")

print(f"[done] wrote {summary_csv}")
print(f"[done] wrote {summary_md}")
PY

echo "[done] W7900 smoke validation finished"
echo "[done] summary: ${OUT_DIR}/summary.md"
cat "${OUT_DIR}/summary.md"
