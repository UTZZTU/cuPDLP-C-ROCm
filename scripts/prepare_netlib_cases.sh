#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

BASE_URL="https://www.netlib.org/lp/data"
RAW_DIR="validation/netlib_compressed"
MPS_DIR="validation/netlib"
TOOLS_DIR="tools"

mkdir -p "$RAW_DIR" "$MPS_DIR" "$TOOLS_DIR"

cases=(
  afiro
  adlittle
  blend
  sc50a
  sc50b
  share2b
)

if [[ ! -x "$TOOLS_DIR/emps" ]]; then
  echo "== download and build emps =="
  curl -L "$BASE_URL/emps.c" -o "$TOOLS_DIR/emps.c"
  gcc -O2 "$TOOLS_DIR/emps.c" -o "$TOOLS_DIR/emps"
fi

echo "== prepare Netlib LP cases =="

for name in "${cases[@]}"; do
  raw="$RAW_DIR/$name"
  out="$MPS_DIR/$name.mps"

  echo "-- $name"

  curl -L "$BASE_URL/$name" -o "$raw"
  "$TOOLS_DIR/emps" "$raw" > "$out"

  if ! grep -q '^ROWS' "$out" || ! grep -q '^COLUMNS' "$out" || ! grep -q '^ENDATA' "$out"; then
    echo "ERROR: expanded file does not look like normal MPS: $out" >&2
    exit 1
  fi
done

echo "== generated MPS files =="
ls -lh "$MPS_DIR"
