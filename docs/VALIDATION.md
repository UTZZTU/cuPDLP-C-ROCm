# ROCm validation

<!-- FINAL_W7900_VALIDATION_20260729 -->

> **Final formal-evidence update (2026-07-29)**
>
> The authoritative W7900 validation state is:
>
> - formal branch: `rocm-w7900-gfx1100`
> - frozen solver: `735764807d8698ff30811d1a6fcc45d4a3fd4817`
> - formal harness: `b5b9a6ffc1a041a48a0e051568d0134a3822556c`
> - baseline23: 46/46 `VALIDATED_OPTIMAL`
> - precision: 30/30 `VALIDATED_OPTIMAL`
> - profiles: 5/5 `PASS`
> - total formal solver records: 76/76
> - final state: `FORMAL_W7900_EXPERIMENTS_COMPLETE`,
>   `FINAL_ANALYSIS_RELEASED`
>
> See the [final W7900 results](W7900_FINAL_RESULTS_20260729.md) and
> [final compact validation package](../validation/final_w7900_20260729/README.md).
> The smoke, Netlib, and comparison semantics below remain the general
> validation rules.


> 中文版: [VALIDATION.zh-CN.md](VALIDATION.zh-CN.md)
> Documentation map: [README.md](README.md)
> Validation result index: [../validation/README.md](../validation/README.md)

This document defines how `cuPDLP-C-ROCm` validates the ROCm/HIP backend against the CPU baseline.

## Validation result files

Curated validation Markdown summaries and CSV files are indexed in:

- [../validation/README.md](../validation/README.md)
- [../validation/README.zh-CN.md](../validation/README.zh-CN.md)

Frequently used validation CSVs:

| Result group | Markdown summary | CSV files |
|---|---|---|
| Cross-device Netlib summary | [CROSS_DEVICE_BENCHMARKS.md](CROSS_DEVICE_BENCHMARKS.md) | [cross_device_full_summary.csv](../validation/cross_device_full_summary.csv) |
| current vs reduce repeated comparison | [../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.md) | [comparison](../validation/rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](../validation/rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](../validation/rocm_current_vs_reduce_27cases_repeats_raw.csv) |
| rocprof tuning milestones | [../validation/rocm_prof_tuning_milestones_summary.md](../validation/rocm_prof_tuning_milestones_summary.md) | [summary](../validation/rocm_prof_tuning_milestones_summary.csv), [deltas](../validation/rocm_prof_tuning_milestones_deltas.csv), [HIP API](../validation/rocm_prof_tuning_milestones_hip_api_top.csv), [kernel](../validation/rocm_prof_tuning_milestones_kernel_top.csv), [memory-copy](../validation/rocm_prof_tuning_milestones_memory_copy_top.csv) |
| tuning ablation 6-case repeats | [../validation/rocm_tuning_ablation_6cases_repeats_summary.md](../validation/rocm_tuning_ablation_6cases_repeats_summary.md) | [summary](../validation/rocm_tuning_ablation_6cases_repeats_summary.csv), [raw](../validation/rocm_tuning_ablation_6cases_repeats_raw.csv) |

## Verified ROCm target

| Item | Value |
|---|---|
| GPU/APU | AMD Radeon 890M |
| Architecture | `gfx1150` |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| Solver executable | `build-rocm-plc/bin/plc` |
| CPU baseline executable | `build-cpu/bin/plc` |

## Validation goals

The validation workflow checks whether the ROCm/HIP backend produces numerically reasonable results compared with the CPU backend. The CPU backend is used as the correctness baseline because it does not depend on GPU runtime behavior and is easier to debug.

The goal is not bitwise equality. CPU and ROCm/HIP runs may follow different floating-point trajectories because of:

- different BLAS and sparse libraries,
- different sparse matrix-vector multiplication order,
- different reduction order,
- different restart trajectories,
- different kernel launch and synchronization behavior.

The validation goal is therefore:

```text
same solver status + comparable relative feasibility and gap metrics
```

## Validation levels

This project currently uses the following validation levels:

1. Smoke validation.
2. Extended Netlib validation.
3. Cross-device Netlib benchmark validation.
4. Large MPS dataset validation and performance benchmarking.

Smoke validation is the required minimum check before changing ROCm/HIP backend code. Extended and benchmark validation broaden coverage after larger changes.

## Smoke validation

Default smoke validation:

```bash
./scripts/run_validation.sh
```

Current smoke cases are listed in:

```text
validation/cases.txt
```

Current smoke cases:

| Case | MPS path | Iteration limit | Result |
|---|---|---:|---|
| `afiro` | `example/afiro.mps` | 200 | PASS |
| `sc50b` | `validation/netlib/sc50b.mps` | 5000 | PASS |

Expected summary:

```text
PASS: 2
INCOMPLETE: 0
FAIL: 0
```

Generated smoke reports are written under:

```text
validation/results/latest/
```

This directory is generated output and should not be committed.

## Full ROCm port check

Recommended local check:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

The full check runs:

1. `scripts/check_rocm_port_hygiene.sh`
2. `scripts/run_validation.sh`
3. CTest-registered ROCm checks, when a ROCm build tree has been configured.

Use this command before pushing ROCm/HIP backend, validation-script, or workflow changes.

## ROCm hygiene checks

The hygiene check script is:

```bash
./scripts/check_rocm_port_hygiene.sh
```

It checks guardrails such as:

- HIP backend files should not reintroduce direct `CHECK_CUDA`, `CHECK_CUSPARSE`, or `CHECK_CUBLAS` calls.
- CMake files should not reintroduce misleading legacy HIP/CUDA public options.
- Required HIP check macros such as `CHECK_HIP_STRICT` must remain present.
- Legacy exported compatibility symbols such as `cuda_csr_Ax`, `cuda_csc_ATy`, and `cuda_alloc_MVbuffer` must remain present until the C/HIP boundary is refactored safely.

## Extended Netlib validation

Prepare Netlib cases:

```bash
./scripts/prepare_netlib_cases.sh
```

Run extended validation:

```bash
RESULT_ROOT=validation/results/extended_netlib \
  ./scripts/run_validation.sh validation/cases_extended_netlib.txt
```

Current extended cases are listed in:

```text
validation/cases_extended_netlib.txt
```

Current extended validation status:

| Case | MPS path | Iteration limit | Result | Notes |
|---|---|---:|---|---|
| `afiro` | `example/afiro.mps` | 200 | PASS | Baseline example |
| `adlittle` | `validation/netlib/adlittle.mps` | 5000 | PASS | Relative validation metrics pass |
| `blend` | `validation/netlib/blend.mps` | 5000 | PASS | Relative validation metrics pass |
| `sc50a` | `validation/netlib/sc50a.mps` | 5000 | PASS | Relative validation metrics pass |
| `sc50b` | `validation/netlib/sc50b.mps` | 5000 | PASS | Smoke + extended case |
| `share2b` | `validation/netlib/share2b.mps` | 5000 | INCOMPLETE | Hits iteration/time limit at current settings |

Expected extended summary:

```text
PASS: 5
INCOMPLETE: 1
FAIL: 0
```

`INCOMPLETE` is not treated as a ROCm port failure when both CPU and ROCm hit the current iteration or time limit consistently.

## Medium and large validation sets

The project is expanding beyond small Netlib cases. Larger validation work should follow this order:

1. Prepare or download MPS files outside Git.
2. Generate an inventory file with file names and sizes.
3. Generate a SHA256 manifest.
4. Download or copy the same dataset to each device.
5. Run `sha256sum -c` before benchmarking.
6. Commit only manifests, curated summaries, and documentation.

For the current large MPS workflow, see [LARGE_MPS_BENCHMARK_PLAN.md](LARGE_MPS_BENCHMARK_PLAN.md).

## Comparison script

The comparison script is:

```bash
scripts/compare_cpu_rocm.py
```

It reads CPU and ROCm JSON output files and generates a Markdown comparison report including:

- status comparison,
- hard relative metric comparison,
- informational diagnostics.

## Status comparison

The following status fields are hard checks:

| Field | Meaning |
|---|---|
| `terminationCode` | Solver termination status |
| `primalCode` | Primal feasibility status |
| `dualCode` | Dual feasibility status |

CPU and ROCm status codes must match for a PASS result.

## Hard numeric checks

When both CPU and ROCm report:

```text
terminationCode = OPTIMAL
```

hard numeric checks are:

| Metric | Tolerance |
|---|---:|
| `dRelPrimalFeas` | `1e-4` |
| `dRelDualFeas` | `1e-4` |
| `dRelDualityGap` | `1e-4` |

These relative metrics are more robust across CPU and GPU execution paths than raw absolute objective differences.

## Informational diagnostics

The following fields are recorded but are not hard failure criteria by themselves:

| Field | Reason |
|---|---|
| `nIter` | CPU and GPU may follow different restart or floating-point trajectories |
| `dPrimalObj` | Absolute objective differences can be scale-dependent |
| `dDualObj` | Absolute objective differences can be scale-dependent |
| `dPrimalFeas` | Absolute feasibility can be scale-dependent |
| `dDualFeas` | Absolute feasibility can be scale-dependent |
| `dDualityGap` | Absolute gap can be scale-dependent |

A CPU and ROCm run can differ in iteration count or absolute intermediate values while still reaching equivalent relative feasibility and gap criteria.

## PASS, INCOMPLETE, and FAIL

### PASS

A case is PASS when:

- status fields match,
- both CPU and ROCm report `OPTIMAL`,
- hard relative metrics are within tolerance.

### INCOMPLETE

A case is INCOMPLETE when:

- CPU and ROCm both hit the current iteration or time limit, or
- the case needs a larger iteration limit or separate investigation, and
- the result does not indicate a ROCm-specific correctness failure.

`share2b` and `greenbea`-style convergence-sensitive cases should be recorded, not hidden.

### FAIL

A case is FAIL when:

- CPU and ROCm status codes differ,
- or both report `OPTIMAL` but hard relative metrics exceed tolerance,
- or an unhandled status combination appears.

FAIL means the case needs investigation before the ROCm/HIP backend can be considered validated for that case.

## CTest integration

Configure with testing enabled:

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
```

List tests:

```bash
ctest --test-dir build-rocm-plc -N
```

Run tests:

```bash
ctest --test-dir build-rocm-plc --output-on-failure
```

## Manual validation commands

Build CPU:

```bash
cmake -S . -B build-cpu -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_CUDA=OFF \
  -DBUILD_ROCM=OFF \
  -DBUILD_HIP=OFF \
  -DBUILD_APPS=OFF \
  -DBUILD_PYTHON=OFF

cmake --build build-cpu --target plc -j"$(nproc)"
```

Build ROCm/HIP:

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

Run CPU:

```bash
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200
```

Run ROCm/HIP:

```bash
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_rocm_sum.json \
  -nIterLim 200
```

Compare outputs:

```bash
scripts/compare_cpu_rocm.py \
  --case afiro \
  --cpu /tmp/afiro_cpu_sum.json \
  --rocm /tmp/afiro_rocm_sum.json \
  --out /tmp/afiro_compare.md
```

## Generated files

Validation scripts generate files under:

```text
validation/results/
```

Netlib preparation generates files under:

```text
validation/netlib/
validation/netlib_compressed/
tools/emps
tools/emps.c
```

These are intentionally ignored by Git. Only source scripts, case lists, manifests, curated summaries, and documentation should be committed.

## Current limitations and completed validation scope

- The ROCm/HIP backend remains experimental and is not a production-certified
  solver release.
- The original `gfx1150` / 890M validation target is complete for the current
  scope.
- W7900 / `gfx1100` validation is also complete for the current scope: smoke,
  Netlib, large-MPS baseline, P10 profiling, P11 SpMV tuning, and P12 rejected
  experiment note are documented.
- `share2b` remains INCOMPLETE at the current Netlib iteration/time limit.
- `greenbea` is convergence-sensitive and should remain documented separately.
- No ROCm CI runner is currently available.
- Some legacy CUDA-style names remain intentionally for C/HIP compatibility.

## Future validation maintenance

Completed for the current scope:

- curated larger sparse LP validation;
- W7900 / `gfx1100` build and validation;
- P10/P11/P12 profiling and tuning validation;
- P14-A1 repeated current-vs-pre-tuning validation.

Useful future extensions include:

- more Netlib cases;
- infeasible and unbounded cases;
- badly scaled cases;
- periodic snapshots after toolchain changes;
- a ROCm CI runner when suitable hardware is available;
- optional P14-B repeated ALG1-vs-ALG2 evidence;
- explicit validation of optional presolve/postsolve behavior.

The primary committed validation path keeps HiGHS presolve disabled. Optional presolve support exists, but nontrivial postsolve and recovery to the original variable space are not part of the current validated contract.
