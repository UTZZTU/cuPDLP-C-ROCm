#!/usr/bin/env bash
set -Eeuo pipefail

# Validate the v2.1 harness, require a successful qap15 mini run, commit only the
# whitelisted harness files, and push the current branch.

WORK_ROOT="${WORK_ROOT:-/app/cupdlp_w7900}"
REPO_DIR="${REPO_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"
SOLVER_BASELINE_COMMIT="${SOLVER_BASELINE_COMMIT:-735764807d8698ff30811d1a6fcc45d4a3fd4817}"
EXPECTED_BRANCH="${EXPECTED_BRANCH:-rocm-w7900-gfx1100}"
COMMIT_MESSAGE="${COMMIT_MESSAGE:-scripts: harden W7900 final sprint harness v2.1}"
PUSH_REMOTE="${PUSH_REMOTE:-origin}"
PUSH="${PUSH:-1}"

[[ -n "${REPO_DIR}" && -d "${REPO_DIR}/.git" ]] || {
  echo "[ERROR] run from a cloned cuPDLP-C-ROCm repository" >&2
  exit 1
}
cd "${REPO_DIR}"

allowed=(
  scripts/prepare_w7900_final_sprint.sh
  scripts/download_w7900_large_mps.sh
  scripts/run_w7900_final_sprint.sh
  scripts/w7900_final_sprint_results.py
  scripts/publish_w7900_final_sprint.sh
  docs/W7900_FINAL_SPRINT_RUNBOOK.zh-CN.md
)

msg() {
  echo
  echo "============================================================"
  echo "$*"
  echo "============================================================"
}

die() {
  echo "[ERROR] $*" >&2
  exit 1
}

msg "Static validation"
for file in "${allowed[@]}"; do
  [[ -f "${file}" ]] || die "missing ${file}"
  case "${file}" in
    *.sh)
      bash -n "${file}"
      echo "[OK] bash -n ${file}"
      ;;
    *.py)
      python3 - "${file}" <<'PY'
from pathlib import Path
import sys
compile(Path(sys.argv[1]).read_text(encoding="utf-8"), sys.argv[1], "exec")
PY
      python3 "${file}" self-test
      echo "[OK] python validation ${file}"
      ;;
  esac
done

[[ "$(git branch --show-current)" == "${EXPECTED_BRANCH}" ]] \
  || die "expected branch ${EXPECTED_BRANCH}"

if ! git cat-file -e "${SOLVER_BASELINE_COMMIT}^{commit}" 2>/dev/null; then
  git fetch --no-tags origin "${SOLVER_BASELINE_COMMIT}"
fi

solver_paths=(CMakeLists.txt cmake cupdlp interface)
git diff --quiet "${SOLVER_BASELINE_COMMIT}" HEAD -- "${solver_paths[@]}" \
  || die "committed solver source differs from frozen baseline"
git diff --quiet -- "${solver_paths[@]}" \
  || die "working-tree solver source differs from frozen baseline"
git diff --cached --quiet -- "${solver_paths[@]}" \
  || die "staged solver source differs from frozen baseline"

msg "Check that only harness files will be committed"
mapfile -t changed < <(git status --porcelain=v1 --untracked-files=all | sed -E 's/^.. //' | sed -E 's#^"|"$##')
for path in "${changed[@]}"; do
  [[ -n "${path}" ]] || continue
  ok=0
  for allowed_path in "${allowed[@]}"; do
    if [[ "${path}" == "${allowed_path}" ]]; then
      ok=1
      break
    fi
  done
  (( ok == 1 )) || die "unexpected working-tree change: ${path}"
done

msg "Validate latest mini run"
MINI_RUN_ROOT="${MINI_RUN_ROOT:-}"
if [[ -z "${MINI_RUN_ROOT}" ]]; then
  MINI_RUN_ROOT="$(
    find "${WORK_ROOT}/results/final_sprint" -mindepth 1 -maxdepth 1 -type d -name '*_mini' \
      -printf '%T@ %p\n' 2>/dev/null \
      | sort -nr \
      | awk 'NR==1 {$1=""; sub(/^ /,""); print}'
  )"
fi
[[ -n "${MINI_RUN_ROOT}" && -d "${MINI_RUN_ROOT}" ]] \
  || die "successful mini run directory not found"

python3 - "${MINI_RUN_ROOT}" <<'PY'
import csv, json, sys
from pathlib import Path

root = Path(sys.argv[1])
manifest = root / "00_manifest/run_manifest.json"
summary = root / "parsed/final_sprint_summary.csv"
archive_hint = root.parent.parent / f"{root.name}.tar.gz"
profile_exit = root / "04_profile/current/qap15/qap15_rocm.exitcode"
profile_validation = root / "04_profile/current/qap15/qap15_rocm.profile.status.env"

if not manifest.exists() or json.loads(manifest.read_text()).get("planned_mode") != "mini":
    raise SystemExit("mini manifest missing or invalid")
if not summary.exists():
    raise SystemExit("mini parsed summary missing")

rows = list(csv.DictReader(summary.open(newline="")))
qap = [r for r in rows if r.get("case") == "qap15"]
done_optimal = [
    r for r in qap
    if r.get("runtime_status") == "DONE"
    and r.get("terminationCode") == "OPTIMAL"
    and r.get("solver_validation_status") == "PASS"
]
tols = {r.get("tolerance") for r in done_optimal if r.get("group") == "mini_precision"}
if len(done_optimal) < 4:
    raise SystemExit(f"expected at least 4 DONE+OPTIMAL qap15 rows, got {len(done_optimal)}")
if not {"1e-3", "1e-4", "1e-5"}.issubset(tols):
    raise SystemExit(f"mini precision levels incomplete: {sorted(tols)}")
if not profile_exit.exists() or profile_exit.read_text().strip() != "0":
    raise SystemExit("qap15 mini profile did not exit 0")
if not profile_validation.exists() or "profile_validation_status=PASS" not in profile_validation.read_text():
    raise SystemExit("qap15 mini profile validation did not pass")
if not archive_hint.exists() or not Path(str(archive_hint) + ".sha256").exists():
    raise SystemExit("mini archive or SHA256 sidecar missing")
print(f"[OK] mini run: {root}")
print(f"[OK] qap15 DONE+OPTIMAL rows: {len(done_optimal)}")
print(f"[OK] archive: {archive_hint}")
PY

msg "Commit harness v2.1"
git add -- "${allowed[@]}"

git diff --cached --check
if git diff --cached --quiet; then
  echo "[INFO] no staged changes; commit may already exist"
else
  git commit -m "${COMMIT_MESSAGE}"
fi

msg "Post-commit solver baseline check"
git diff --quiet "${SOLVER_BASELINE_COMMIT}" HEAD -- "${solver_paths[@]}" \
  || die "post-commit solver source differs from frozen baseline"
git status --short

if [[ "${PUSH}" == "1" ]]; then
  msg "Push current branch"
  branch="$(git branch --show-current)"
  git push "${PUSH_REMOTE}" "${branch}"
  echo "[OK] pushed ${PUSH_REMOTE}/${branch}"
else
  echo "[INFO] PUSH=${PUSH}; commit created but not pushed"
fi
