# cuPDLP-C-ROCm Final Reproduction Guide

> 中文：[FINAL_REPRODUCTION_GUIDE.zh-CN.md](FINAL_REPRODUCTION_GUIDE.zh-CN.md)
> Formal results: [W7900_FINAL_RESULTS_20260729.md](W7900_FINAL_RESULTS_20260729.md)

This is the recommended final reproduction path. It separates evidence
inspection, offline result regeneration, minimal build/smoke, and optional full
hardware reruns. The committed release does not require another W7900 run.

## Frozen identity

```text
branch: rocm-w7900-gfx1100
frozen solver source: 735764807d8698ff30811d1a6fcc45d4a3fd4817
formal harness: b5b9a6ffc1a041a48a0e051568d0134a3822556c
Window 1 SHA256: d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a
Window 2 SHA256: 7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db
```

The harness adds measurement, profiling, archival, and QC support while
`CMakeLists.txt`, `cmake/`, `cupdlp/`, and `interface/` remain at the frozen
solver source.

## Clone and inspect the final release

```bash
git clone --recurse-submodules   --branch rocm-w7900-gfx1100   https://github.com/UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm

python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

Expected:

```text
FINAL_W7900_RELEASE_DATA_PASS
FINAL_REPOSITORY_RELEASE_PASS
```

## Regenerate the final figures on any Linux host

```bash
python3 -m pip install pandas numpy matplotlib
python3 scripts/analysis/generate_final_w7900_release.py
```

This uses committed compact CSV data. It is evidence regeneration, not a new
W7900 measurement.

## Minimal CPU reproduction

```bash
cmake -S . -B build-cpu -G Ninja   -DCMAKE_BUILD_TYPE=Release   -DBUILD_CUDA=OFF   -DBUILD_ROCM=OFF
cmake --build build-cpu -j"$(nproc)"

./build-cpu/bin/plc   -fname ./example/afiro.mps   -out /tmp/afiro_cpu.json   -nIterLim 200
```

## Minimal W7900 build/smoke

```bash
bash scripts/prepare_w7900_final_sprint.sh setup
bash scripts/prepare_w7900_final_sprint.sh build
bash scripts/prepare_w7900_final_sprint.sh smoke
```

A matching W7900 / `gfx1100` ROCm environment, HiGHS, compiler, CMake, and
Ninja are required.

## Dataset and login

Raw large-MPS inputs remain outside Git. Verify every input against its SHA256
manifest. For the historical BaiduPCS-Go workflow, exit code 0 from `who` is not
enough: `uid: 0` means unauthenticated.

```bash
bash scripts/download_w7900_large_mps.sh login
bash scripts/download_w7900_large_mps.sh mini
bash scripts/download_w7900_large_mps.sh verify mini
```

## Formal mini gate

```bash
ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=5 BASELINE_REPEATS=1 PRECISION_REPEATS=1 bash scripts/run_w7900_final_sprint.sh mini
```

Require four valid qap15 solver rows, a valid profile with a non-empty kernel
trace, a clean validation summary, and an archive plus checksum.

## Formal Window 1

```bash
bash scripts/download_w7900_large_mps.sh nonhard23

ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=35 BASELINE_REPEATS=2 bash scripts/run_w7900_final_sprint.sh baseline23
```

Require 46/46 validated rows, complete 23×2 identity, resource coverage,
dataset and internal checksum PASS, no timeouts/errors, and an archive.

## Formal Window 2

```bash
bash scripts/download_w7900_large_mps.sh precision5

ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=35 PRECISION_REPEATS=2 PRECISION_LEVELS="1e-3 1e-4 1e-5" bash scripts/run_w7900_final_sprint.sh session2
```

Require 30/30 validated precision rows and 5/5 validated profiles with
non-empty trace and kernel-trace files.

## Archive verification

A checksum sidecar may contain an absolute path from the W7900 host. On another
host compare the first digest field:

```bash
EXPECTED="$(awk 'NF {print $1; exit}' archive.tar.gz.sha256)"
ACTUAL="$(sha256sum archive.tar.gz | awk '{print $1}')"
test "$EXPECTED" = "$ACTUAL"
```

## Operational lessons

- `ACCESS_DEADLINE` is the real access deadline; restarting a script does not
  reset the hardware allocation.
- A single GitHub homepage probe is not a reliable network gate; raw, codeload,
  and Git may differ.
- A HiGHS archive endpoint may reject range resume; remove the partial file and
  download from byte zero.
- A `--single-branch` clone may require an explicit fetch refspec.
- Missing traces are normal for baseline23 but are a failure for profile/session2.
- Inspect an existing run root/archive before rerunning after wrapper failure.
- Never store cookies, SSH keys, or tokens in scripts, logs, archives, or Git.

## Interpretation boundaries

- nonhard23 and hard3 remain separate;
- throughput is independent-case throughput, not one-LP multi-GPU;
- tolerance conclusions cover five cases;
- correlations are exploratory;
- raw traces remain outside Git;
- evidence inspection on a non-W7900 host is not fresh W7900 benchmarking.

## Release checks

```bash
git diff --check
python3 scripts/docs/check_markdown_links.py
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```
