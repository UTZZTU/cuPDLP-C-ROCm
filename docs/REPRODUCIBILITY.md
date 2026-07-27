# Reproducibility guide

> 中文: [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md)

This guide explains how to inspect committed evidence without a W7900 and how to recover the environment, build, validate, and rerun key workflows on Radeon PRO W7900 / `gfx1100`.

## 1. Reproducibility levels

| Level | Work that can be completed | Hardware |
|---|---|---|
| Documentation and data inspection | Check CSV, Markdown, SVG, Git history, and scripts | Any Linux host |
| CPU/CUDA engineering check | Build CPU or CUDA paths and validate generic commands | Matching toolchain; CUDA requires NVIDIA GPU/toolkit |
| W7900 ROCm validation | build, smoke, large-MPS, profiling, and tuning repeats | W7900 / `gfx1100` with a matching ROCm environment |

Documentation work on a non-W7900 host is valid, but it must not be described as a fresh reproduction of W7900 performance.

## 2. Clone the fixed branch

```bash
git clone --recurse-submodules \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd cuPDLP-C-ROCm
git pull --ff-only origin rocm-w7900-gfx1100
git submodule update --init --recursive
```

Record the baseline:

```bash
git branch --show-current
git rev-parse HEAD
git status
```

## 3. Inspect committed results without W7900

### 3.1 non-hard23

```bash
python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_large_mps_nonhard23_20260613.csv")
rows = list(csv.DictReader(p.open()))
print("rows:", len(rows))
print("termination:", sorted({r["terminationCode"] for r in rows}))
print("runtime:", sorted({r["runtime_status"] for r in rows}))
print("groups:", sorted({r["source_group"] for r in rows}))
print("total wall:", sum(float(r["wall_seconds"]) for r in rows))
print("total solve:", sum(float(r["dSolvingTime"]) for r in rows))
PY
```

Expected:

```text
rows: 23
termination: ['OPTIMAL']
runtime: ['DONE']
total wall: approximately 2960.171
total solve: approximately 2742.940
```

### 3.2 P14-A1 quick6

```bash
python3 - <<'PY'
import csv
from pathlib import Path

p = Path("validation/w7900_p14a1_quick6_current_vs_pretuning_repeats_20260618_comparison.csv")
rows = list(csv.DictReader(p.open()))
speedups = [float(r["median_speedup_pre_over_current"]) for r in rows]
print("rows:", len(rows))
print("current wins:", sum(x > 1 for x in speedups), "/", len(speedups))
print("min:", min(speedups))
print("max:", max(speedups))
PY
```

The expected result is six rows and 6/6 current wins. The summary reports geometric mean `1.18889` and median `1.19502`.

## 4. Recover a fresh W7900 environment

The maintained scripts assume the established W7900 workspace layout. On a fresh machine:

```bash
mkdir -p /app/cupdlp_w7900/src
cd /app/cupdlp_w7900/src

git clone \
  --depth 1 \
  --single-branch \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git

cd cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh
```

Check the recovered environment:

```bash
git status
git log --oneline --decorate -8
command -v hipcc rocprofv3 rocprof rocm-smi amd-smi || true
rocminfo | grep -E "Name:|Marketing Name|gfx" || true
```

If local paths differ from the historical layout, inspect:

```text
scripts/env/w7900_python_rocm_env.sh
scripts/build_w7900_cpu.sh
scripts/build_w7900_rocm.sh
```

Adapt through environment variables or local configuration rather than writing machine-private absolute paths into general documentation.

## 5. Large-MPS data policy

Raw MPS data stays outside Git. The historical W7900 data root is:

```text
/app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark
```

Expected files:

```text
mps/
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

Run SHA256 from the `mps` directory:

```bash
cd /app/cupdlp_w7900/datasets/large_mps_baidu/cupdlp-large-mps-benchmark/mps

sha256sum -c ../h100_large_mps_manifest.sha256 \
  2>&1 | tee /app/cupdlp_w7900/logs/large_mps_sha256_check.log

grep -c ": OK$" /app/cupdlp_w7900/logs/large_mps_sha256_check.log
```

The historical manifest contains 26 files. Only verified inputs may be benchmarked.

## 6. Build and smoke

Use the maintained scripts:

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

Expected binaries:

```text
build-cpu/bin/plc
build-rocm-w7900/bin/plc
```

The bootstrap can also build and run smoke:

```bash
RUN_BUILD=1 RUN_SMOKE=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

CPU and ROCm/W7900 termination, primal, and dual statuses should match. A mismatch requires JSON and log inspection and must not be reported as PASS.

## 7. Rerun and parse non-hard23

Case list:

```text
validation/cases_w7900_large_mps_before_after_nonhard23.txt
```

Relevant entry points:

```text
scripts/run_w7900_large_mps_baseline.sh
scripts/parse_w7900_large_mps_results.py
```

Parse a local result directory:

```bash
python3 scripts/parse_w7900_large_mps_results.py \
  /app/cupdlp_w7900/results/<result-directory>
```

Authoritative committed compact artifacts:

```text
validation/w7900_large_mps_nonhard23_20260613.csv
validation/w7900_large_mps_nonhard23_20260613_runtime.csv
validation/w7900_large_mps_nonhard23_20260613.md
validation/w7900_large_mps_nonhard23_20260613.zh-CN.md
```

The current result is a post-890M-tuning W7900 engineering baseline, not a first-port baseline.

## 8. P10 targeted profiling

P10 uses five targeted cases:

```text
thk_48
square41
L2CTA3D
set-cover-model
tpl-tub-ws1617
```

Primary entry point:

```bash
bash scripts/run_w7900_p10_current_targeted_rocprof.sh
```

The earlier generic starter3 workflow remains available for historical comparison:

```bash
CASE_LIST=validation/cases_w7900_rocprof_starter3.txt \
RUN_TAG=w7900_rocprof_starter3 \
TIME_LIMIT=900 \
EXTERNAL_TIMEOUT=960 \
bash scripts/run_w7900_rocprof_smoke_matrix.sh
```

Do not describe starter3 as the P10 case list. The scripts prefer `rocprofv3`, then legacy `rocprof`. Without a profiler, a run is baseline execution only and must not be reported as completed profiling.

Compact P10 results:

```text
validation/w7900_p10_current_targeted_rocprof_20260617_*.csv
validation/w7900_p10_current_targeted_rocprof_20260617_summary*.md
```

Raw traces are not committed.

## 9. P11 SpMV algorithm tuning

P11 sweep entry point:

```bash
bash scripts/run_w7900_p11_spmv_alg_sweep.sh
```

Current policy:

```text
default: HIPSPARSE_SPMV_CSR_ALG1
fallback: CUPDLP_HIP_SPMV_ALG=csr_alg2
```

Test the fallback with:

```bash
CUPDLP_HIP_SPMV_ALG=csr_alg2 \
./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_csr_alg2.json \
  -nIterLim 200
```

Compare termination, feasibility, gap, `nIter`, and runtime together.

## 10. P14-A1 repeated validation

After restoring the W7900 environment and preparing quick6 MPS files:

```bash
source /app/cupdlp_w7900/activate_w7900.sh

bash scripts/run_w7900_p14a1_quick6_current_vs_pretuning_repeats.sh \
  2>&1 | tee /app/cupdlp_w7900/logs/p14a1_$(date +%Y%m%d_%H%M%S).log

python3 scripts/analysis/archive_w7900_p14a1_quick6_current_vs_pretuning_20260618.py
```

Commit compact CSV/Markdown only, not raw run directories.

## 11. hard3 and eight-card evidence

hard3 probe2 evidence is committed, but difficult cases remain separate from non-hard23:

- [hard3 notes](W7900_LARGE_MPS_HARD3_NOTES.md)
- [probe2 summary](../validation/w7900_large_mps_hard3_probe2_600s_summary_20260616.md)

The eight-card fast8 summary measures concurrent throughput for eight independent MPS jobs:

- [8-card fast8 summary](../validation/w7900_8card_batch_fast8_summary_20260616.md)

It does not reproduce distributed multi-GPU solution of one LP.

## 12. Files that must not be committed

Do not commit:

- raw `.mps` / `.mps.gz`;
- raw profiler trace directories;
- temporary W7900 result directories;
- machine-local build directories;
- credentials, cookies, or SSH keys;
- machine-private environment files.

Allowed artifacts include:

- source code and scripts;
- case lists and manifests;
- curated CSV;
- Markdown summaries;
- compact SVG;
- compact profiler summaries.

## 13. Docker status

The current Docker files are an environment-declaration skeleton:

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
docker/README_DOCKER_W7900.zh-CN.md
```

They are not the source of the committed W7900 numbers and do not replace validation on an actual ROCm host.

## 14. Checks before sharing

Run the maintained checks:

```bash
git status
git diff --check
python3 scripts/docs/scan_markdown_format_issues_20260616.py
```

The repository does not currently contain a standalone `scripts/docs/check_markdown_links.py`. For a local relative-link check, use:

```bash
python3 - <<'PY'
import re
from pathlib import Path
from urllib.parse import unquote

root = Path(".").resolve()
bad = []
pat = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")
for src in root.rglob("*.md"):
    if ".git" in src.parts:
        continue
    text = src.read_text(encoding="utf-8", errors="replace")
    for match in pat.finditer(text):
        raw = next(x for x in match.groups() if x).strip().split()[0].strip("<>")
        if raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = unquote(raw.split("#", 1)[0])
        if target and not (src.parent / target).resolve().exists():
            bad.append((src.relative_to(root), raw))
if bad:
    for src, target in bad:
        print(f"{src}: {target}")
    raise SystemExit(1)
print("[OK] repository-internal Markdown links")
PY
```

Confirm that:

- branch and commit are recorded;
- inputs passed SHA256 verification;
- comparisons use the same case list and limits;
- non-hard23, hard3, and eight-card meanings are not mixed;
- English and Chinese current documents are synchronized;
- raw data and credentials are not staged;
- a non-W7900 documentation check is not described as fresh W7900 performance reproduction.
