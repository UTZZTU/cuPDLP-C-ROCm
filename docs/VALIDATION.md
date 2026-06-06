# ROCm validation

This document describes how this repository validates the ROCm/HIP port of cuPDLP-C against the CPU baseline.

The current verified ROCm target is:

| Item | Value |
|---|---|
| GPU/APU | AMD Radeon 890M |
| Architecture | `gfx1150` |
| ROCm | 7.2.1 |
| HIP compiler | ROCm Clang 22.0.0 |
| Solver executable | `build-rocm-plc/bin/plc` |
| CPU baseline executable | `build-cpu/bin/plc` |

## Validation goals

The validation workflow checks whether the ROCm/HIP backend produces numerically reasonable results compared with the CPU backend.

The CPU backend is used as the baseline because it does not depend on GPU runtime behavior and is easier to debug.

The goal is not bitwise equality. CPU and ROCm/HIP runs may follow slightly different floating-point trajectories because of:

- different BLAS and sparse libraries,
- different sparse matrix-vector multiplication order,
- different reduction order,
- different restart trajectories,
- different kernel launch and synchronization behavior.

The validation goal is therefore:

```text
same solver status + comparable relative feasibility and gap metrics
```

## Medium Netlib validation

The smoke suite is intentionally small. For broader coverage, use the medium
Netlib validation set.

Prepare the additional Netlib MPS files:

```bash
./scripts/prepare_medium_netlib_cases.sh
```

Run medium validation:

```bash
RESULT_ROOT=validation/results/medium_netlib \
  ./scripts/run_validation.sh validation/cases_medium_netlib.txt

grep -R "Overall result" validation/results/medium_netlib/*/*_compare.md
```

The medium set uses higher iteration limits than the smoke suite. If a case
hits `nIterLim`, treat the result as `INCOMPLETE` first and inspect both CPU and
ROCm logs before treating it as a correctness failure.

Medium validation results are generated artifacts and should not be committed.

## Validation levels

This project currently uses two validation levels:

1. Smoke validation
2. Extended Netlib validation

Smoke validation is the default required check before changing ROCm/HIP backend code.

Extended validation is used to broaden coverage with additional small Netlib LP cases.

## Smoke validation

Smoke validation is the default workflow:

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

Smoke validation writes generated reports under:

```text
validation/results/latest/
```

This directory is generated output and is ignored by Git.

## Full ROCm port check

The recommended local check is:

```bash
./scripts/check_rocm_port.sh
```

This runs:

1. `scripts/check_rocm_port_hygiene.sh`
2. `scripts/run_validation.sh`

Use this command before pushing ROCm/HIP backend or validation changes.

## ROCm hygiene checks

The hygiene check script is:

```bash
./scripts/check_rocm_port_hygiene.sh
```

It checks guardrails such as:

- HIP backend `.cpp` files should not reintroduce direct `CHECK_CUDA`, `CHECK_CUSPARSE`, or `CHECK_CUBLAS` calls.
- CMake files should not reintroduce `plchip`.
- CMake files should not reintroduce the old misleading `CUDA_LIBRARY-NOTFOUND` flag.
- Required HIP check macros such as `CHECK_HIP_STRICT` must remain present.
- Legacy exported compatibility symbols such as `cuda_csr_Ax`, `cuda_csc_ATy`, and `cuda_alloc_MVbuffer` must remain present until the C/HIP boundary is refactored safely.

These checks are intentionally conservative. Some CUDA-style names are still kept because they are compatibility symbols used across C and HIP/C++ boundaries.

## Extended Netlib validation

Extended validation uses additional small Netlib LP cases prepared by:

```bash
./scripts/prepare_netlib_cases.sh
```

Then run:

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

## Preparing Netlib cases

Some Netlib LP cases are distributed in compressed MPS format. This project uses:

```bash
./scripts/prepare_netlib_cases.sh
```

This script prepares the local Netlib validation inputs under:

```text
validation/netlib/
validation/netlib_compressed/
```

These directories are generated outputs and are ignored by Git.

The helper tool:

```text
tools/emps
tools/emps.c
```

is also generated or downloaded locally and ignored by Git.

## Comparison script

The comparison script is:

```bash
scripts/compare_cpu_rocm.py
```

It reads CPU and ROCm JSON output files and generates a Markdown comparison report.

The report includes:

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

the hard numeric checks are:

| Metric | Tolerance |
|---|---:|
| `dRelPrimalFeas` | `1e-4` |
| `dRelDualFeas` | `1e-4` |
| `dRelDualityGap` | `1e-4` |

These metrics are used because they are relative measures of feasibility and gap, and are more robust across CPU and GPU execution paths than raw absolute objective differences.

## Informational diagnostics

The following fields are recorded in reports but are not hard failure criteria by themselves:

| Field | Reason |
|---|---|
| `nIter` | CPU and ROCm may follow different restart or floating-point trajectories |
| `dPrimalObj` | Absolute objective differences can be scale-dependent |
| `dDualObj` | Absolute objective differences can be scale-dependent |
| `dPrimalFeas` | Absolute feasibility can be scale-dependent |
| `dDualFeas` | Absolute feasibility can be scale-dependent |
| `dDualityGap` | Absolute gap can be scale-dependent |

This is intentional. A CPU and ROCm run can differ in iteration count or absolute intermediate values while still reaching equivalent relative feasibility and gap criteria.

## PASS, INCOMPLETE, and FAIL

### PASS

A case is PASS when:

- status fields match,
- both CPU and ROCm report `OPTIMAL`,
- hard relative metrics are within tolerance.

### INCOMPLETE

A case is INCOMPLETE when:

- CPU and ROCm both hit the current iteration or time limit,
- the case therefore needs a larger iteration limit or separate investigation,
- the result does not indicate a ROCm-specific correctness failure.

Current example:

```text
share2b
```

### FAIL

A case is FAIL when:

- CPU and ROCm status codes differ,
- or both report `OPTIMAL` but hard relative metrics exceed tolerance,
- or an unhandled status combination appears.

FAIL means the case needs investigation before the ROCm/HIP backend can be considered validated for that case.

## CTest integration

ROCm validation is registered with CTest when configuring with:

```bash
-DBUILD_TESTING=ON
```

Configure example:

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

Current registered tests:

| Test | Purpose | Expected result |
|---|---|---|
| `rocm_port_hygiene` | Checks ROCm/HIP naming and compatibility guardrails | PASS |
| `rocm_smoke_validation` | Runs CPU-vs-ROCm smoke validation | PASS |

CTest is the preferred standard validation entry point after configuring a ROCm build tree.

## Manual validation commands

The scripts automate validation, but the underlying manual commands are useful for debugging.

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

## Generated validation files

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

These are intentionally ignored by Git.

Only source scripts, case lists, and documentation should be committed.

## Recommended workflow before pushing

Run:

```bash
./scripts/check_rocm_port.sh
ctest --test-dir build-rocm-plc --output-on-failure
```

Then confirm no generated files are staged:

```bash
git status --short
git status --ignored --short | grep -E 'validation/results|validation/netlib|validation/netlib_compressed|tools/emps' || true
```

## Current limitations

The current validation status should be read with the following limitations:

- The tested matrix is still small.
- Larger LP problems are not yet validated.
- `share2b` remains INCOMPLETE at the current iteration/time limit.
- No CI runner is currently available for ROCm validation.
- The current ROCm/HIP backend is verified on `gfx1150`; other AMD GPU/APU architectures require separate validation.
- Some legacy CUDA-style names remain intentionally for compatibility across C and HIP/C++ boundaries.

## Future validation work

Planned validation improvements:

- Add more Netlib LP cases.
- Add larger sparse LP cases.
- Add infeasible and unbounded LP cases.
- Add badly scaled cases.
- Record periodic validation result snapshots.
- Add ROCm CI when a suitable runner is available.
- Validate additional ROCm architectures beyond `gfx1150`.
- Add performance regression checks once profiling and tuning are more mature.
