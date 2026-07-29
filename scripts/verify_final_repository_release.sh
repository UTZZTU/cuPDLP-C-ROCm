#!/usr/bin/env bash
set -Eeuo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO}"

FORMAL_BRANCH="rocm-w7900-gfx1100"
SOLVER_BASELINE="735764807d8698ff30811d1a6fcc45d4a3fd4817"
HARNESS_COMMIT="b5b9a6ffc1a041a48a0e051568d0134a3822556c"

echo "repo=${REPO}"
echo "branch=$(git branch --show-current 2>/dev/null || true)"
echo "head=$(git rev-parse HEAD 2>/dev/null || true)"

python3 -m py_compile \
  scripts/analysis/generate_final_w7900_release.py \
  scripts/docs/check_markdown_links.py

bash -n scripts/verify_final_repository_release.sh

python3 scripts/analysis/generate_final_w7900_release.py --check-only
python3 scripts/docs/check_markdown_links.py

for file in \
  validation/final_w7900_20260729/files.sha256 \
  validation/final_w7900_20260729/formal_experiment_identity.json \
  docs/W7900_FINAL_RESULTS_20260729.zh-CN.md \
  docs/FINAL_REPRODUCTION_GUIDE.zh-CN.md \
  RELEASE_NOTES_FINAL_20260729.md
do
  test -s "${file}" || {
    echo "[ERROR] missing/empty ${file}" >&2
    exit 1
  }
done

(
  cd validation/final_w7900_20260729
  sha256sum -c files.sha256
)

(
  cd docs/assets/w7900/final20260729
  sha256sum -c files.sha256
)

git diff --check

if git cat-file -e "${SOLVER_BASELINE}^{commit}" 2>/dev/null; then
  git diff --quiet "${SOLVER_BASELINE}" -- \
    CMakeLists.txt cmake cupdlp interface || {
      echo "[ERROR] frozen solver boundary differs from ${SOLVER_BASELINE}" >&2
      git diff --stat "${SOLVER_BASELINE}" -- \
        CMakeLists.txt cmake cupdlp interface >&2
      exit 1
    }
else
  echo "[WARN] frozen solver commit not available locally; caller must fetch it"
fi

echo "formal_branch=${FORMAL_BRANCH}"
echo "formal_harness_commit=${HARNESS_COMMIT}"
echo "frozen_solver_source=${SOLVER_BASELINE}"
echo "FINAL_REPOSITORY_RELEASE_PASS"
