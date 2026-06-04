#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

echo "== cuPDLP-C-ROCm full port check =="
echo "root: $ROOT_DIR"
echo ""

echo "== 1/2: ROCm port hygiene =="
./scripts/check_rocm_port_hygiene.sh

echo ""
echo "== 2/2: CPU vs ROCm smoke validation =="
./scripts/run_validation.sh

echo ""
echo "== smoke validation reports =="
find validation/results/latest -name "*_compare.md" -print | sort
grep -R "Overall result" validation/results/latest/*/*_compare.md

echo ""
echo "== cuPDLP-C-ROCm full port check: PASS =="
