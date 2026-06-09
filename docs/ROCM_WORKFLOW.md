# ROCm workflow guide

> 中文版: [`ROCM_WORKFLOW.zh-CN.md`](ROCM_WORKFLOW.zh-CN.md)

This guide summarizes day-to-day commands for the `cuPDLP-C-ROCm` fork.

The repository currently provides:

- CPU build path,
- upstream-compatible CUDA build path,
- ROCm/HIP build path,
- smoke validation,
- extended Netlib validation,
- ROCm port hygiene checks,
- CTest integration,
- `rocprofv3` profiling helpers,
- profiling summary helpers,
- copy-trace analysis helpers,
- cross-device and large MPS benchmark workflows.

The currently verified ROCm target is AMD Radeon 890M / `gfx1150`.

## 1. Repository health checks

Use this after changing ROCm/HIP code, validation scripts, profiling scripts, or public documentation.

```bash
cd ~/rocm_dir/pdlp/cuPDLP-C-ROCm
git status --short
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

Expected result:

```text
== cuPDLP-C-ROCm full port check: PASS ==
100% tests passed
```

The full check runs ROCm port hygiene checks and CPU-vs-ROCm smoke validation.

## 2. ROCm build

For Radeon 890M / `gfx1150`:

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

For Radeon PRO W7900, use the same command but switch to:

```bash
-DCMAKE_HIP_ARCHITECTURES=gfx1100
```

## 3. ROCm port hygiene only

Use this when changing naming, CMake logic, public logs, or ROCm/HIP wrappers.

```bash
./scripts/check_rocm_port_hygiene.sh
```

Current compatibility symbols such as the following are intentionally still allowed:

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

They remain internal compatibility boundaries for now. Do not rename them casually without a dedicated compatibility pass.

## 4. Smoke validation

```bash
./scripts/run_validation.sh
```

Default smoke cases are defined in:

```text
validation/cases.txt
```

Current smoke coverage:

```text
afiro
sc50b
```

Results are written to:

```text
validation/results/latest/
```

Useful summary command:

```bash
grep -R "Overall result" validation/results/latest/*/*_compare.md
```

Expected result:

```text
afiro: PASS
sc50b: PASS
```

## 5. Extended Netlib validation

Use this after algorithm-adjacent changes, kernel fusion, memory-copy changes, or larger ROCm/HIP refactors.

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt

grep -R "Overall result" validation/results/extended_netlib/*/*_compare.md
```

Current expected status:

```text
afiro PASS
adlittle PASS
blend PASS
sc50a PASS
sc50b PASS
share2b INCOMPLETE
```

`share2b` is treated as incomplete rather than a hard correctness failure under the current limit.

## 6. Preparing Netlib cases

```bash
./scripts/prepare_netlib_cases.sh
```

Generated Netlib files are local validation artifacts and should remain ignored.

Check local cases:

```bash
find validation/netlib -maxdepth 1 -name '*.mps' -printf '%f\n' | sort
```

## 7. Profiling smoke workflow

Use this after performance-related changes.

```bash
RESULT_ROOT=profiling/results/current \
  ./scripts/profile_rocm_smoke.sh
```

Summarize `rocprofv3` CSV traces:

```bash
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

Useful quick view:

```bash
grep -nE 'Top HIP API|Top kernels|Kernel categories|hipLaunchKernel|hipMemcpy|copyBuffer|rocblas|rocSPARSE' \
  profiling/results/current/profile_summary.md | head -260
```

Profiling results are generated artifacts and should not be committed.

## 8. Copy/copyBuffer analysis

Use this when `hipMemcpy`, `hipMemcpyAsync`, or `__amd_rocclr_copyBuffer` is a hotspot.

```bash
python3 scripts/analyze_rocm_copy_trace.py \
  --input profiling/results/current/sc50b_rocprofv3 \
  | tee profiling/results/current/sc50b_copy_analysis.md
```

The helper reports HIP memcpy counts/time, ROCclr copy/fill buffer dispatch counts/time, and whether copyBuffer dispatches correlate with HIP memcpy calls.

## 9. Cross-device benchmark workflow

For the Netlib benchmark matrix:

```bash
CASE_TIMEOUT_SEC=3600 ./scripts/run_benchmark_890m_full.sh
./scripts/summarize_benchmark.py
```

Use the same case list and high-level settings on CUDA baseline machines:

```text
validation/cases_benchmark_200m.txt
nIterLim = 200000000
per-run timeout = 3600s
```

## 10. Large MPS workflow

The large MPS workflow uses H100 as the source dataset host and Baidu Netdisk as a transfer mechanism. Each target machine must verify the dataset with SHA256 before running benchmarks.

See:

```text
docs/LARGE_MPS_BENCHMARK_PLAN.md
```

## 11. When to run which command

| Situation | Recommended command |
|---|---|
| You changed ROCm/HIP source code | `./scripts/check_rocm_port.sh && ctest --test-dir build-rocm-plc --output-on-failure` |
| You changed naming, CMake, or public logs | `./scripts/check_rocm_port_hygiene.sh` |
| You changed validation scripts | `./scripts/run_validation.sh` |
| You changed algorithm-adjacent GPU code | Extended Netlib validation |
| You changed performance-sensitive code | Profiling smoke + summary |
| You changed memory-copy behavior | Profiling smoke + copy analysis |
| You changed documentation only | `git diff`, then optionally `./scripts/check_rocm_port_hygiene.sh` |
| You changed benchmark case lists | Recreate manifest/summary and rerun affected subset |

## 12. Suggested commit policy

Usually commit:

```text
scripts/*.sh
scripts/*.py
docs/*.md
validation/cases*.txt
validation/*.csv
validation/datasets/*.sha256
validation/datasets/*.csv
tools/migration/*.py
```

Usually do not commit:

```text
validation/results/
profiling/results/
build-*/
validation/netlib/
validation/netlib_compressed/
tools/emps
tools/emps.c
large raw MPS files
```

## 13. Current next priorities

1. Keep English and Chinese documentation in sync.
2. Finish the large MPS benchmark matrix.
3. Record Radeon 890M pre-tuning ROCm baseline and later tuned rerun.
4. Expand profiling evidence beyond smoke cases.
5. Prepare W7900 / `gfx1100` migration and profiling.
