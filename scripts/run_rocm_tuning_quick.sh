#!/usr/bin/env bash
set -Eeuo pipefail

LABEL="${1:-$(git rev-parse --short HEAD 2>/dev/null || echo run)}"
CASE_FILE="${CASE_FILE:-validation/cases_tuning_quick.txt}"
CASE_TIMEOUT_SEC="${CASE_TIMEOUT_SEC:-900}"
HIP_ARCH="${HIP_ARCH:-gfx1150}"
BUILD_DIR="${BUILD_DIR:-build-rocm-tuning-quick}"
RUN_ROOT="validation/results/tuning_quick_${LABEL}_$(date +%Y%m%d_%H%M%S)"

echo "== cuPDLP-C-ROCm ROCm tuning quick run =="
echo "label: ${LABEL}"
echo "case file: ${CASE_FILE}"
echo "timeout per case: ${CASE_TIMEOUT_SEC}s"
echo "HIP arch: ${HIP_ARCH}"
echo "build dir: ${BUILD_DIR}"
echo "run dir: ${RUN_ROOT}"

if [ ! -f "${CASE_FILE}" ]; then
  echo "ERROR: missing case file: ${CASE_FILE}" >&2
  exit 1
fi

mkdir -p "${RUN_ROOT}"

{
  echo "== date =="
  date
  echo
  echo "== pwd =="
  pwd
  echo
  echo "== git =="
  git rev-parse HEAD 2>/dev/null || true
  git log --oneline -n 5 2>/dev/null || true
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
  echo "== case file =="
  cat "${CASE_FILE}"
} > "${RUN_ROOT}/run_env.txt" 2>&1

rm -rf "${BUILD_DIR}"

CMAKE_BACKEND_ARGS=()
if grep -q "BUILD_ROCM" CMakeLists.txt; then
  CMAKE_BACKEND_ARGS+=("-DBUILD_CUDA=OFF" "-DBUILD_ROCM=ON")
else
  CMAKE_BACKEND_ARGS+=("-DBUILD_CUDA=OFF" "-DBUILD_HIP=ON")
fi

cmake -S . -B "${BUILD_DIR}" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  "${CMAKE_BACKEND_ARGS[@]}" \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES="${HIP_ARCH}" \
  2>&1 | tee "${RUN_ROOT}/configure.log"

cmake --build "${BUILD_DIR}" --target plc -j"$(nproc)" \
  2>&1 | tee "${RUN_ROOT}/build.log"

PLC="${BUILD_DIR}/bin/plc"
if [ ! -x "${PLC}" ]; then
  echo "ERROR: plc binary not found: ${PLC}" >&2
  exit 1
fi

echo "${RUN_ROOT}" > validation/results/latest_tuning_quick.txt

while IFS=, read -r name mps_path iter tier; do
  [ -z "${name// }" ] && continue
  [[ "${name}" =~ ^# ]] && continue

  case_dir="${RUN_ROOT}/${name}"
  mkdir -p "${case_dir}"

  json="${case_dir}/${name}_rocm.json"
  log="${case_dir}/${name}_rocm.log"
  exitcode="${case_dir}/${name}_rocm.exitcode"

  echo
  echo "== ${name} (${tier}) =="
  echo "mps: ${mps_path}"
  echo "iter: ${iter}"

  if [ ! -f "${mps_path}" ]; then
    echo "MISSING_MPS ${mps_path}" | tee "${log}"
    echo "127" > "${exitcode}"
    continue
  fi

  set +e
  timeout "${CASE_TIMEOUT_SEC}" "${PLC}" \
    -fname "${mps_path}" \
    -out "${json}" \
    -nIterLim "${iter}" \
    2>&1 | tee "${log}"
  code=${PIPESTATUS[0]}
  set -e

  echo "${code}" > "${exitcode}"
  echo "exit=${code}"
done < "${CASE_FILE}"

python3 - "${RUN_ROOT}" "${CASE_FILE}" "${LABEL}" <<'PY'
import csv, json, pathlib, sys

run = pathlib.Path(sys.argv[1])
case_file = pathlib.Path(sys.argv[2])
label = sys.argv[3]
rows = []

for line in case_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, path, iter_lim, tier = [x.strip() for x in line.split(",", 3)]
    case_dir = run / name
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
        "case": name,
        "tier": tier,
        "mps": path,
        "iter_limit": iter_lim,
        "exitcode": exit_path.read_text().strip() if exit_path.exists() else "",
        "status": data.get("terminationCode", ""),
        "termination_iterate": data.get("terminationIterate", ""),
        "nIter": data.get("nIter", ""),
        "solve_time_sec": data.get("dSolvingTime", ""),
        "dRelPrimalFeas": data.get("dRelPrimalFeas", ""),
        "dRelDualFeas": data.get("dRelDualFeas", ""),
        "dRelDualityGap": data.get("dRelDualityGap", ""),
        "DeviceMatVecProdTime": data.get("DeviceMatVecProdTime", ""),
        "AllocMem_CopyMatToDeviceTime": data.get("AllocMem_CopyMatToDeviceTime", ""),
        "CopyVecToDeviceTime": data.get("CopyVecToDeviceTime", ""),
        "CopyVecToHostTime": data.get("CopyVecToHostTime", ""),
        "json": str(json_path) if json_path.exists() else "",
        "log": str(log_path) if log_path.exists() else "",
    })

fields = list(rows[0].keys()) if rows else [
    "label","case","tier","mps","iter_limit","exitcode","status","termination_iterate",
    "nIter","solve_time_sec","dRelPrimalFeas","dRelDualFeas","dRelDualityGap",
    "DeviceMatVecProdTime","AllocMem_CopyMatToDeviceTime","CopyVecToDeviceTime",
    "CopyVecToHostTime","json","log"
]

csv_path = run / "summary.csv"
with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

md_path = run / "summary.md"
with md_path.open("w") as f:
    f.write("# ROCm tuning quick summary\n\n")
    f.write(f"Label: `{label}`\n\n")
    f.write(f"Run dir: `{run}`\n\n")
    f.write("| case | status | exit | iter | time | matvec | rel primal | rel dual | rel gap |\n")
    f.write("|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
    for r in rows:
        f.write(
            f"| {r['case']} | {r['status']} | {r['exitcode']} | {r['nIter']} | "
            f"{r['solve_time_sec']} | {r['DeviceMatVecProdTime']} | "
            f"{r['dRelPrimalFeas']} | {r['dRelDualFeas']} | {r['dRelDualityGap']} |\n"
        )

print(f"summary csv: {csv_path}")
print(f"summary md:  {md_path}")
PY

echo
echo "== summary =="
cat "${RUN_ROOT}/summary.md"
echo
echo "Run finished: ${RUN_ROOT}"
