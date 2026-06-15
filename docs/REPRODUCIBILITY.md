# Reproducibility guide

> 中文: [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)

This document explains how to reproduce the repository results and how to recover the working environment on temporary AMD GPU machines.

## 1. Scope

The repository has three reproducibility layers:

| Layer | Goal | Hardware needed |
|---|---|---|
| Documentation/data check | Verify committed CSV/Markdown/SVG summaries | Any machine with Git and Python |
| 890M/gfx1150 validation | Reproduce local ROCm build and small validation on the 890M development machine | Radeon 890M / `gfx1150` |
| W7900/gfx1100 validation/profiling | Reproduce W7900 smoke, large-MPS summaries, and profiling workflow | Radeon PRO W7900 / `gfx1100` |

Raw large-MPS files are not committed to Git. The repository commits scripts, case lists, manifests, curated CSV summaries, Markdown summaries, and SVG charts.

## 2. Clone the W7900 branch

Recommended full clone:

```bash
git clone --recurse-submodules git@github.com:UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm
git fetch --all --tags --prune
git switch rocm-w7900-gfx1100
git pull --ff-only origin rocm-w7900-gfx1100
git submodule update --init --recursive
```

If you already have the `rocm-gfx1150` worktree on the 890M machine, use a linked worktree instead:

```bash
cd ~/rocm_dir/pdlp/cuPDLP-C-ROCm
git fetch origin --prune

cd ~/rocm_dir/pdlp
git -C cuPDLP-C-ROCm worktree add \
  cuPDLP-C-ROCm-w7900-work \
  origin/rocm-w7900-gfx1100
```

## 3. Verify committed W7900 summaries without a W7900 machine

```bash
cd cuPDLP-C-ROCm

python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
print("rows:", len(rows))
print("termination:", sorted(set(r["terminationCode"] for r in rows)))
print("runtime:", sorted(set(r["runtime_status"] for r in rows)))
print("source groups:", sorted(set(r["source_group"] for r in rows)))
print("total wall:", sum(float(r["wall_seconds"]) for r in rows))
print("total solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

Expected output:

```text
rows: 23
termination: ['OPTIMAL']
runtime: ['DONE']
source groups: ['initial17_safe', 'near_optimal2_1800s', 'watchlist6_900s']
total wall: 2960.171115
total solve: 2742.940418
```

## 4. Fresh W7900 machine recovery

The W7900 cloud environment can be volatile. On a fresh machine:

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

GIT_TERMINAL_PROMPT=0 git clone \
  --depth 1 \
  --single-branch \
  --branch rocm-w7900-gfx1100 \
  --filter=blob:none \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh
```

After recovery, verify the branch and key files:

```bash
git log --oneline --decorate -8
git status

ls -lh \
  docs/COMPETITION_README.md \
  docs/W7900_CURRENT_STATUS.md \
  docs/W7900_ROCM_PROFILING_PLAN.md \
  validation/w7900_large_mps_nonhard23_20260613.csv
```

## 5. Large-MPS data policy

Raw MPS files stay outside Git.

Expected W7900 data root:

```text
/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark
```

Expected subdirectories/files:

```text
mps/
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

SHA256 check should be run from the `mps` directory because the manifest stores file names without the `mps/` prefix:

```bash
cd /app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps

sha256sum -c ../h100_large_mps_manifest.sha256 \
  2>&1 | tee /app/cupdlp_w7900/logs/large_mps_sha256_check.log
```

Expected successful count:

```bash
grep -c ": OK$" /app/cupdlp_w7900/logs/large_mps_sha256_check.log
# expected: 26
```

## 6. Reproduce smoke validation

On W7900:

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

RUN_BUILD=1 RUN_SMOKE=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

Expected interpretation:

```text
CPU and ROCm/W7900 smoke validation reached matching termination, primal, and dual statuses.
```

## 7. Reproduce current committed non-hard23 summary

The current committed non-hard23 CSV is a post-890M-tuning W7900 engineering baseline, not an unoptimized first-port baseline.

Check it with:

```bash
python3 scripts/parse_w7900_large_mps_results.py \
  /app/cupdlp_w7900/results/<your_result_dir>
```

Curated committed result:

```text
validation/w7900_large_mps_nonhard23_20260613.csv
validation/w7900_large_mps_nonhard23_20260613_runtime.csv
validation/w7900_large_mps_nonhard23_20260613.md
validation/w7900_large_mps_nonhard23_20260613.zh-CN.md
```

## 8. Reproduce starter profiling workflow

Starter case list:

```text
validation/cases_w7900_rocprof_starter3.txt
```

Cases:

```text
set-cover-model.mps
square41.mps
s100.mps
```

Run on W7900 after data and build are ready:

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

CASE_LIST=validation/cases_w7900_rocprof_starter3.txt \
RUN_TAG=w7900_rocprof_starter3 \
TIME_LIMIT=900 \
EXTERNAL_TIMEOUT=960 \
bash scripts/run_w7900_rocprof_smoke_matrix.sh
```

Expected output root:

```text
/app/cupdlp_w7900/results/w7900_rocprof/
```

The script detects `rocprofv3` first, then legacy `rocprof`, and falls back to baseline-only execution if no profiler exists.

## 9. Reproduce future before/current comparison

The true pre-tuning anchor is:

```text
ae3b683 / pre_tuning
```

The current W7900 non-hard23 result is:

```text
current post-890M-tuning engineering baseline
```

Core6 case list:

```text
validation/cases_w7900_large_mps_before_after_core6.txt
```

Full non-hard23 before/after case list:

```text
validation/cases_w7900_large_mps_before_after_nonhard23.txt
```

Use the core6 list before attempting a full non-hard23 before/after rerun.

## 10. Files that should not be committed

Do not commit:

- raw `.mps` files;
- raw large profiler traces;
- temporary W7900 result directories;
- machine-local build directories;
- credentials, cookies, or SSH keys.

Commit only:

- source code and scripts;
- case lists;
- manifests;
- curated CSV summaries;
- Markdown summaries;
- small SVG charts;
- compact profiler summaries.

## 11. Docker / container status

A dedicated Docker/Containerfile is not the primary reproduction path because the available W7900 environment uses a pre-installed ROCm/Python SDK layout. The current reproducible path is the documented bootstrap workflow.

This repository now provides a lightweight Docker/container skeleton:

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
docker/README_DOCKER_W7900.zh-CN.md
```

The skeleton documents the expected build-environment shape and final-submission packaging direction. It is not claimed as the source of the committed W7900 performance numbers. Raw MPS data and raw profiler traces stay outside the image.

## 12. Quick reviewer checklist

```bash
git status
git log --oneline --decorate -8

python3 -m py_compile \
  scripts/document_competition_readme_20260614.py \
  scripts/document_reproducibility_20260614.py \
  scripts/document_w7900_optimization_baselines_20260614.py

python3 - <<'PY'
import csv
from pathlib import Path
p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
assert len(rows) == 23
assert set(r["terminationCode"] for r in rows) == {"OPTIMAL"}
print("W7900 non-hard23 summary check: OK")
PY
```
