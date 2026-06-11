#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

BASE_URL="${NETLIB_LP_DATA_URL:-https://www.netlib.org/lp/data}"
CASE_FILE="${CASE_FILE:-validation/cases_benchmark_200m_w7900_27.txt}"
COMPRESSED_DIR="validation/netlib_compressed"
MPS_DIR="validation/netlib"

mkdir -p "${COMPRESSED_DIR}" "${MPS_DIR}" tools

download_one() {
  local url="$1"
  local out="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 5 --retry-delay 3 --connect-timeout 30 -o "${out}" "${url}"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "${out}" "${url}"
  else
    echo "error: neither curl nor wget is available" >&2
    return 1
  fi
}

ensure_emps() {
  if [[ -x tools/emps ]]; then
    return 0
  fi

  if [[ ! -f tools/emps.c ]]; then
    echo "== download emps.c =="
    download_one "${BASE_URL}/emps.c" "tools/emps.c"
  fi

  echo "== build tools/emps =="
  cc -O2 -o tools/emps tools/emps.c
}

if [[ ! -f "${CASE_FILE}" ]]; then
  echo "error: missing case file: ${CASE_FILE}" >&2
  exit 1
fi

ensure_emps

echo "== prepare W7900 27-case Netlib benchmark set =="
echo "case file : ${CASE_FILE}"
echo "base url  : ${BASE_URL}"
echo "mps dir   : ${MPS_DIR}"
echo

while IFS=, read -r name mps_path n_iter tier rest; do
  name="$(echo "${name:-}" | xargs)"
  mps_path="$(echo "${mps_path:-}" | xargs)"

  if [[ -z "${name}" ]] || [[ "${name}" =~ ^# ]]; then
    continue
  fi

  if [[ "${name}" == "greenbea" ]]; then
    echo "[skip] greenbea"
    continue
  fi

  compressed="${COMPRESSED_DIR}/${name}"
  mps="${MPS_DIR}/${name}.mps"

  echo "-- ${name}"

  if [[ -s "${mps}" ]]; then
    echo "   mps exists: ${mps}"
    continue
  fi

  if [[ ! -s "${compressed}" ]]; then
    echo "   download ${BASE_URL}/${name}"
    download_one "${BASE_URL}/${name}" "${compressed}"
  else
    echo "   compressed exists: ${compressed}"
  fi

  echo "   expand to ${mps}"
  tools/emps < "${compressed}" > "${mps}.tmp"
  mv "${mps}.tmp" "${mps}"

  if ! grep -q '^NAME' "${mps}"; then
    echo "error: expanded file does not look like MPS: ${mps}" >&2
    exit 1
  fi
done < "${CASE_FILE}"

echo
echo "== W7900 27-case MPS availability =="
python3 - "${CASE_FILE}" <<'PY'
from pathlib import Path
import sys

case_file = Path(sys.argv[1])
missing = []
present = []

for line in case_file.read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    name, mps, *_ = [x.strip() for x in line.split(",")]
    if Path(mps).exists():
        present.append(name)
    else:
        missing.append((name, mps))

print(f"present: {len(present)}")
print(f"missing: {len(missing)}")
if missing:
    for name, mps in missing:
        print(f"[missing] {name}: {mps}")
    raise SystemExit(1)
PY

find "${MPS_DIR}" -maxdepth 1 -name '*.mps' -printf '%f\n' | sort
