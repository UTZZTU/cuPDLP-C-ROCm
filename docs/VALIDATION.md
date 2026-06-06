# ROCm validation

This document describes how this repository validates the ROCm/HIP port of cuPDLP-C against the CPU baseline.

The current verified ROCm target is:

| Item                    | Value                    |
| ----------------------- | ------------------------ |
| GPU/APU                 | AMD Radeon 890M          |
| Architecture            | `gfx1150`                |
| ROCm                    | 7.2.1                    |
| HIP compiler            | ROCm Clang 22.0.0        |
| Solver executable       | `build-rocm-plc/bin/plc` |
| CPU baseline executable | `build-cpu/bin/plc`      |

## Validation goals

The validation workflow checks whether the ROCm/HIP backend produces numerically reasonable results compared with the CPU backend.

The CPU backend is used as the baseline because it does not depend on GPU runtime behavior and is easier to debug. The goal is not bitwise equality. CPU and ROCm/HIP runs may follow slightly different floating-point trajectories because of:

* different BLAS and sparse libraries,
* different sparse matrix-vector multiplication order,
* different reduction order,
* different restart trajectories,
* different kernel launch and synchronization behavior.

The validation goal is therefore:

```text
same solver status + comparable relative feasibility and gap metrics
```

## Validation levels

This project currently uses three local validation/benchmark levels:

1. Smoke validation
2. Extended Netlib validation
3. Cross-device benchmark matrix

Smoke validation is the default required check before changing ROCm/HIP backend code. Extended validation broadens coverage with additional small Netlib LP cases. The cross-device benchmark matrix is used to compare CPU, CUDA, and ROCm behavior across multiple devices; it is not intended to be a bitwise correctness test.

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

| Case    | MPS path                      | Iteration limit | Result |
| ------- | ----------------------------- | --------------: | ------ |
| `afiro` | `example/afiro.mps`           |             200 | PASS   |
| `sc50b` | `validation/netlib/sc50b.mps` |            5000 | PASS   |

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

* HIP backend `.cpp` files should not reintroduce direct `CHECK_CUDA`, `CHECK_CUSPARSE`, or `CHECK_CUBLAS` calls.
* CMake files should not reintroduce `plchip`.
* CMake files should not reintroduce the old misleading `CUDA_LIBRARY-NOTFOUND` flag.
* Required HIP check macros such as `CHECK_HIP_STRICT` must remain present.
* Legacy exported compatibility symbols such as `cuda_csr_Ax`, `cuda_csc_ATy`, and `cuda_alloc_MVbuffer` must remain present until the C/HIP boundary is refactored safely.

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

| Case       | MPS path                         | Iteration limit | Result     | Notes                                         |
| ---------- | -------------------------------- | --------------: | ---------- | --------------------------------------------- |
| `afiro`    | `example/afiro.mps`              |             200 | PASS       | Baseline example                              |
| `adlittle` | `validation/netlib/adlittle.mps` |            5000 | PASS       | Relative validation metrics pass              |
| `blend`    | `validation/netlib/blend.mps`    |            5000 | PASS       | Relative validation metrics pass              |
| `sc50a`    | `validation/netlib/sc50a.mps`    |            5000 | PASS       | Relative validation metrics pass              |
| `sc50b`    | `validation/netlib/sc50b.mps`    |            5000 | PASS       | Smoke + extended case                         |
| `share2b`  | `validation/netlib/share2b.mps`  |            5000 | INCOMPLETE | Hits iteration/time limit at current settings |

Expected extended summary:

```text
PASS: 5
INCOMPLETE: 1
FAIL: 0
```

`INCOMPLETE` is not treated as a ROCm port failure when both CPU and ROCm hit the current iteration or time limit consistently.

## Medium Netlib validation

The smoke suite is intentionally small. For broader coverage, use the medium Netlib validation set.

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

The medium set uses higher iteration limits than the smoke suite.

If a case hits `nIterLim`, treat the result as `INCOMPLETE` first and inspect both CPU and ROCm logs before treating it as a correctness failure. Medium validation results are generated artifacts and should not be committed.

## Cross-device benchmark matrix

In addition to smoke and extended Netlib validation, this repository tracks a local cross-device benchmark matrix for comparing the upstream CUDA baseline and the ROCm/HIP port.

The benchmark matrix uses:

```text
validation/cases_benchmark_200m.txt
```

Common settings:

| Setting         | Value                                               |
| --------------- | --------------------------------------------------- |
| Iteration limit | `nIterLim = 200000000`                              |
| Per-run timeout | `3600s`                                             |
| Case source     | Netlib MPS cases plus `afiro`, `sc50b`, and `lotfi` |
| Comparison mode | local CPU + GPU/ROCm on each device                 |

Current devices:

| Device                | Backend  | Role                   |
| --------------------- | -------- | ---------------------- |
| RTX 3090              | CUDA     | upstream CUDA baseline |
| RTX 4090D             | CUDA     | upstream CUDA baseline |
| Radeon 890M / gfx1150 | ROCm/HIP | ROCm port target       |

The benchmark is not a bitwise correctness test. It is used to compare:

* termination status,
* iteration counts,
* solve time,
* relative primal feasibility,
* relative dual feasibility,
* relative duality gap,
* GPU timing behavior where available.

Current high-level status:

| Device             |                                     CPU result | GPU/ROCm result | Exception                                                |
| ------------------ | ---------------------------------------------: | --------------: | -------------------------------------------------------- |
| RTX 3090 / CUDA    | 28/28 OPTIMAL after `greenbea` 200M supplement |   27/28 OPTIMAL | `greenbea` CUDA reached solver internal 3600s time limit |
| RTX 4090D / CUDA   |                                  28/28 OPTIMAL |   27/28 OPTIMAL | `greenbea` CUDA hit external 3600s timeout               |
| Radeon 890M / ROCm |                                  28/28 OPTIMAL |   27/28 OPTIMAL | `greenbea` ROCm hit external 3600s timeout               |

See [CROSS_DEVICE_BENCHMARKS.md](CROSS_DEVICE_BENCHMARKS.md) for the benchmark interpretation.

Generated benchmark run directories are local artifacts and should not be committed:

```text
validation/results/
validation/netlib/
*.tar.gz
```

The compact result summary can be committed as:

```text
validation/cross_device_summary.csv
```

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

It reads CPU and ROCm JSON output files and generates a Markdown comparison report. The report includes:

* status comparison,
* hard relative metric comparison,
* informational diagnostics.

## Status comparison

The following status fields are hard checks:

| Field             | Meaning                   |
| ----------------- | ------------------------- |
| `terminationCode` | Solver termination status |
| `primalCode`      | Primal feasibility status |
| `dualCode`        | Dual feasibility status   |

CPU and ROCm status codes must match for a PASS result.

## Hard numeric checks

When both CPU and ROCm report:

```text
terminationCode = OPTIMAL
```

the hard numeric checks are:

| Metric           | Tolerance |
| ---------------- | --------: |
| `dRelPrimalFeas` |    `1e-4` |
| `dRelDualFeas`   |    `1e-4` |
| `dRelDualityGap` |    `1e-4` |

These metrics are used because they are relative measures of feasibility and gap, and are more robust across CPU and GPU execution paths than raw absolute objective differences.

## Informational diagnostics

The following fields are recorded in reports but are not hard failure criteria by themselves:

| Field         | Reason                                                                   |
| ------------- | ------------------------------------------------------------------------ |
| `nIter`       | CPU and ROCm may follow different restart or floating-point trajectories |
| `dPrimalObj`  | Absolute objective differences can be scale-dependent                    |
| `dDualObj`    | Absolute objective differences can be scale-dependent                    |
| `dPrimalFeas` | Absolute feasibility can be scale-dependent                              |
| `dDualFeas`   | Absolute feasibility can be scale-dependent                              |
| `dDualityGap` | Absolute gap can be scale-dependent                                      |

This is intentional. A CPU and ROCm run can differ in iteration count or absolute intermediate values while still reaching equivalent relative feasibility and gap criteria.

## PASS, INCOMPLETE, TIMEOUT, and FAIL

### PASS

A case is PASS when:

* status fields match,
* both CPU and ROCm report `OPTIMAL`,
* hard relative metrics are within tolerance.

### INCOMPLETE

A case is INCOMPLETE when:

* CPU and ROCm both hit the current iteration or time limit,
* the case therefore needs a larger iteration limit or separate investigation,
* the result does not indicate a ROCm-specific correctness failure.

Current extended validation example:

```text
share2b
```

### TIMEOUT

A case is TIMEOUT when the outer shell timeout kills a solver run before a JSON summary is written.

Current cross-device benchmark example:

```text
greenbea
```

On Radeon 890M, `greenbea` ROCm hit the 3600s external timeout. This is tracked as a convergence-sensitive benchmark case, not as a build or runtime failure.

### FAIL

A case is FAIL when:

* CPU and ROCm status codes differ in a way that is not classified as INCOMPLETE or TIMEOUT,
* or both report `OPTIMAL` but hard relative metrics exceed tolerance,
* or an unhandled status combination appears.

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

| Test                    | Purpose                                             | Expected result |
| ----------------------- | --------------------------------------------------- | --------------- |
| `rocm_port_hygiene`     | Checks ROCm/HIP naming and compatibility guardrails | PASS            |
| `rocm_smoke_validation` | Runs CPU-vs-ROCm smoke validation                   | PASS            |

CTest is the preferred standard validation entry point after configuring a ROCm build tree.
