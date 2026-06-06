#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BASE_URL="${NETLIB_LP_DATA_URL:-https://www.netlib.org/lp/data}"
COMPRESSED_DIR="validation/netlib_compressed"
MPS_DIR="validation/netlib"

CASES=(
  sc105
  sc205
  scagr7
  kb2
  lotfi
  recipe
  stocfor1
  share1b
)

mkdir -p "$COMPRESSED_DIR" "$MPS_DIR" tools

download_one() {
  local url="$1"
  local out="$2"

  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 --connect-timeout 20 -o "$out" "$url"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$out" "$url"
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
    download_one "$BASE_URL/emps.c" "tools/emps.c"
  fi

  echo "== build tools/emps =="
  cc -O2 -o tools/emps tools/emps.c
}

ensure_emps

echo "== prepare medium Netlib LP cases =="
for case_name in "${CASES[@]}"; do
  compressed="$COMPRESSED_DIR/$case_name"
  mps="$MPS_DIR/$case_name.mps"

  echo "-- $case_name"

  if [[ ! -s "$compressed" ]]; then
    download_one "$BASE_URL/$case_name" "$compressed"
  else
    echo "   compressed file already exists: $compressed"
  fi

  tools/emps < "$compressed" > "$mps.tmp"
  mv "$mps.tmp" "$mps"

  if ! grep -q '^NAME' "$mps"; then
    echo "error: expanded file does not look like MPS: $mps" >&2
    exit 1
  fi
done

echo "== medium Netlib cases ready =="
find "$MPS_DIR" -maxdepth 1 -name '*.mps' -printf '%f\n' | sort
