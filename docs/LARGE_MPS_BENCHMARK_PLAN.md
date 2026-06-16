# Large MPS benchmark plan

> 中文版: [`LARGE_MPS_BENCHMARK_PLAN.zh-CN.md`](LARGE_MPS_BENCHMARK_PLAN.zh-CN.md)

This document records the large MPS benchmark workflow for `cuPDLP-C-ROCm`.

## Goal

The Netlib benchmark matrix is useful for validation, but many cases are small enough that GPU overhead dominates. The large MPS workflow is intended to test larger LP instances where sparse matrix-vector products and vector operations can better expose GPU behavior.

The goals are:

1. Use the same large MPS dataset on all machines.
2. Verify every downloaded file with SHA256 before running solvers.
3. Compare CUDA baselines on RTX 3090, RTX 4090D, and H100.
4. Record a Radeon 890M ROCm pre-tuning baseline.
5. Rerun Radeon 890M later with the best validated tuned ROCm version.
6. Keep raw MPS files outside Git and commit only manifests and curated summaries.

## Dataset source and transfer

The source dataset is staged on the H100 server under:

```text
~/cuPDLP-C/test_data/*.mps
```

It is uploaded to Baidu Netdisk under:

```text
/cupdlp-large-mps-benchmark/
/cupdlp-large-mps-benchmark/mps/
```

Two metadata files should be stored next to the `mps/` directory:

```text
h100_large_mps_inventory.csv
h100_large_mps_manifest.sha256
```

The manifest is generated on the source machine with:

```bash
cd ~/cuPDLP-C/test_data
sha256sum *.mps > ~/h100_large_mps_manifest.sha256
```

## Local target path

Each target machine should use the same local layout:

```text
~/cuPDLP-C/test_data_large_mps/
├── h100_large_mps_inventory.csv
├── h100_large_mps_manifest.sha256
└── mps/
    ├── a2864.mps
    ├── ...
```

## Download and verification policy

After download, verify the dataset:

```bash
DATA_ROOT="$HOME/cuPDLP-C/test_data_large_mps"
cd "$DATA_ROOT/mps"
sha256sum -c "$DATA_ROOT/h100_large_mps_manifest.sha256"
```

Do not benchmark a machine until every case reports `OK`.

If a download is interrupted, regenerate a missing/bad list from the manifest and download only failed files. A file is considered present only if it passes SHA256.

## Current case count

The current H100-sourced dataset contains 26 `.mps` files and is about 22 GiB on the RTX 3090 local copy. The exact source of truth is the SHA256 manifest, not a hand-written list.

Generate the case list from the manifest:

```bash
DATA_ROOT="$HOME/cuPDLP-C/test_data_large_mps"
awk '{print $2}' "$DATA_ROOT/h100_large_mps_manifest.sha256" \
  | sed 's#^\./##' \
  | sort > ~/large_mps_all26.txt
```

## Benchmark policy by device

| Device | Backend policy | Purpose |
|---|---|---|
| RTX 3090 | upstream-compatible cuPDLP-C CUDA, one full run | CUDA baseline |
| RTX 4090D | upstream-compatible cuPDLP-C CUDA, one full run | CUDA baseline |
| H100 | upstream-compatible cuPDLP-C CUDA, one full run | high-end CUDA baseline |
| Radeon 890M | ROCm/HIP pre-tuning baseline, then later tuned rerun | ROCm baseline and tuning comparison |
| Radeon PRO W7900 | later ROCm/HIP `gfx1100` run | target competition platform |

CUDA platforms do not need repeated ROCm-style tuning runs. Radeon 890M should be measured twice: once with the pre-tuning usable ROCm commit and once with the best validated tuned version.

## Recommended per-run limits

For large MPS benchmarking:

```text
nIterLim = 200000000
external timeout = 7200s
```

A timeout is still a valid result if the log records:

- case name,
- backend,
- device,
- commit or upstream source,
- timeout value,
- exit status,
- terminationCode when available,
- iteration count when available,
- primal feasibility,
- dual feasibility,
- duality gap,
- wall-clock time,
- solve time,
- log path.

Do not silently drop hard cases.

## 3090 CUDA baseline command shape

Use the upstream-compatible `plc` from the original cuPDLP-C build. The large MPS directory should be:

```text
~/cuPDLP-C/test_data_large_mps/mps
```

A benchmark script should write:

```text
runtime_summary.csv
run_info.txt
logs/*.log
json/*.json
```

The summary must include at least:

```text
case,status,wall_seconds,log,json
```

Additional parser scripts can later extract solver-level metrics from JSON and logs.

## 890M ROCm baseline command shape

For the pre-tuning ROCm baseline, use the commit that is buildable and before the later tuning pass. The intended baseline commit is:

```text
ae3b683 Add ROCm profiling summary script
```

Build it with:

```bash
cmake -S . -B build-rocm-plc -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=ON \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF \
  -DBUILD_TESTING=ON \
  -DCMAKE_PREFIX_PATH=/opt/rocm \
  -DCMAKE_HIP_ARCHITECTURES=gfx1150

cmake --build build-rocm-plc --target plc -j"$(nproc)"
```

Then run the same verified large MPS case list with the same high-level limits.

## What to commit

Commit only curated metadata and summaries:

```text
validation/datasets/h100_large_mps_inventory.csv
validation/datasets/h100_large_mps_manifest.sha256
validation/cases/h100_large_mps_cases.txt
validation/large_mps_*_summary.csv
docs/LARGE_MPS_BENCHMARK_PLAN.md
docs/LARGE_MPS_BENCHMARK_PLAN.zh-CN.md
```

Do not commit:

```text
*.mps
*.mps.gz
raw solver output directories
BaiduPCS-Go temporary files
large tar archives
```

## Interpretation policy

Large MPS benchmarking should answer three questions:

1. Do CUDA and ROCm backends run the same verified inputs?
2. Which cases benefit from GPU acceleration at larger scales?
3. Which ROCm costs dominate on Radeon 890M before and after tuning?

Results should be interpreted together with profiling. A single timeout or convergence-sensitive case should be documented rather than hidden.

## Completion update / 2026-06-17

The original benchmark plan has now been executed beyond the planning
stage. CUDA baselines, Radeon 890M ROCm baselines, W7900 / `gfx1100`
baselines, targeted profiling, and P11 SpMV tuning summaries have been
committed as curated validation artifacts.

The W7900 target should no longer be described as a future platform in
this branch. It is the completed second ROCm target for the current
project stage. Raw `.mps` files and raw solver logs remain outside Git;
curated summaries and links live under `validation/` and
`docs/W7900_CURRENT_STATUS.md`.
