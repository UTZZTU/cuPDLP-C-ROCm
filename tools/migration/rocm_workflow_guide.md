# ROCm workflow guide

This guide summarizes the day-to-day commands for the cuPDLP-C-ROCm fork.

The repository currently provides:

- a CPU build path,
- a ROCm/HIP build path,
- smoke validation,
- extended Netlib validation,
- ROCm port hygiene checks,
- rocprofv3 profiling helpers,
- profiling summary helpers,
- copy-trace analysis helpers.

The currently tested ROCm target is AMD Radeon 890M / `gfx1150`.

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

The full check runs:

1. ROCm port hygiene checks.
2. CPU-vs-ROCm smoke validation.

## 2. ROCm port hygiene only

Use this when you changed naming, CMake logic, public logs, or ROCm/HIP wrappers.

```bash
./scripts/check_rocm_port_hygiene.sh
```

This checks that user-visible ROCm/HIP naming does not regress and that known compatibility symbols remain present.

Current compatibility symbols such as the following are intentionally still allowed:

```text
cuda_csr_Ax
cuda_csc_ATy
cuda_alloc_MVbuffer
```

They remain internal compatibility boundaries for now. Do not rename them casually without a dedicated compatibility pass.

## 3. Smoke validation

Use this for quick correctness checks after small code changes.

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

## 4. Extended Netlib validation

Use this after algorithm-adjacent changes, kernel fusion, memory-copy changes, or larger ROCm/HIP refactors.

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt

grep -R "Overall result" validation/results/extended_netlib/*/*_compare.md
```

Current extended cases:

```text
afiro
adlittle
blend
sc50a
sc50b
share2b
```

Current expected status:

```text
afiro    PASS
adlittle PASS
blend    PASS
sc50a    PASS
sc50b    PASS
share2b  INCOMPLETE
```

`share2b` is currently treated as incomplete rather than a hard correctness failure because it does not reach a comparable converged state under the current iteration limit.

## 5. Preparing Netlib cases

Use this when `validation/netlib/` is missing or you need to regenerate local Netlib MPS files.

```bash
./scripts/prepare_netlib_cases.sh
```

Generated Netlib files are local validation artifacts and should remain ignored unless a future decision explicitly vendors small test inputs.

Check local cases:

```bash
find validation/netlib -maxdepth 1 -name '*.mps' -printf '%f\n' | sort
```

## 6. Profiling smoke workflow

Use this after performance-related changes.

```bash
RESULT_ROOT=profiling/results/current \
  ./scripts/profile_rocm_smoke.sh
```

Then summarize the rocprofv3 CSV traces:

```bash
python3 scripts/summarize_rocm_profile.py \
  --input profiling/results/current \
  --output profiling/results/current/profile_summary.md
```

Useful quick view:

```bash
grep -nE 'Top HIP API by total time|Top HIP API by call count|Top kernels by total time|Top kernels by dispatch count|Kernel categories by total time|hipLaunchKernel|hipMemcpyAsync|hipMemcpy|__amd_rocclr_copyBuffer|rocblas|rocSPARSE' \
  profiling/results/current/profile_summary.md | head -260
```

Profiling results are generated artifacts and should not be committed.

## 7. Copy/copyBuffer analysis

Use this when `hipMemcpy`, `hipMemcpyAsync`, or `__amd_rocclr_copyBuffer` is a major hotspot.

```bash
python3 scripts/analyze_rocm_copy_trace.py \
  --input profiling/results/current/sc50b_rocprofv3 \
  | tee profiling/results/current/sc50b_copy_analysis.md
```

The helper reports:

- HIP memcpy API counts and time,
- ROCclr copy/fill buffer dispatch counts and time,
- whether `__amd_rocclr_copyBuffer` dispatches correlate with HIP memcpy calls.

Current observation after the latest tuning pass:

```text
hipMemcpy + hipMemcpyAsync events correlate one-to-one with __amd_rocclr_copyBuffer dispatches.
```

## 8. Current completed ROCm tuning optimizations

The current tuning pass completed four low-risk optimizations:

1. Removed redundant `hipDeviceSynchronize()` in movement interaction.
2. Cached HIP device attributes in linalg helpers.
3. Fused average iterate AXPY updates with `update_average_kernel`.
4. Reduced movement interaction scalar D2D copies with `save_movement_xy_kernel`.

See:

```text
docs/TUNING_GUIDE_ROCM.md
```

for details and before/after profiling counts.

## 9. When to run which command

| Situation | Recommended command |
|---|---|
| You changed ROCm/HIP source code | `./scripts/check_rocm_port.sh && ctest --test-dir build-rocm-plc --output-on-failure` |
| You changed naming, CMake, or public logs | `./scripts/check_rocm_port_hygiene.sh` |
| You changed validation scripts | `./scripts/run_validation.sh` |
| You changed algorithm-adjacent GPU code | Extended Netlib validation |
| You changed performance-sensitive code | Profiling smoke + summary |
| You changed memory-copy behavior | Profiling smoke + copy analysis |
| You changed documentation only | `git diff`, then optionally `./scripts/check_rocm_port_hygiene.sh` |

## 10. Suggested commit policy

Commit code and documentation. Do not commit generated validation/profiling outputs.

Usually commit:

```text
scripts/*.sh
scripts/*.py
docs/*.md
validation/cases*.txt
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
```

## 11. Current next priorities

The recommended next priorities are:

1. Add a clearer usage link from `README.md`.
2. Expand Netlib validation with a medium case list and higher iteration limits.
3. Continue internal CUDA-name cleanup in a staged compatibility-safe way.
4. Only then revisit higher-risk performance work such as reductions, the remaining movement-interaction copy, SpMV, or HIP Graphs.

Avoid replacing all rocBLAS calls, changing rocSPARSE SpMV, or renaming internal exported compatibility symbols without a dedicated validation branch.
