# Validation Plan

This document records the validation plan for the ROCm/HIP port of cuPDLP-C.

The current verified milestone is:

- Platform: AMD Radeon 890M / gfx1150
- ROCm: 7.2.1
- Example: `example/afiro.mps`
- Result: `terminationCode = OPTIMAL`

## Validation goals

The goal is to verify that the ROCm/HIP version produces numerically reasonable results compared with the CPU version.

The CPU version is used as the baseline because it is easier to debug and does not depend on GPU runtime behavior.

## Current verified case

| Case | Backend | Iteration limit | Status | Notes |
|---|---|---:|---|---|
| `example/afiro.mps` | CPU | 200 | PASS | Baseline run completed |
| `example/afiro.mps` | ROCm/HIP gfx1150 | 200 | PASS | `terminationCode = OPTIMAL` |

## Metrics to compare

For each test case, compare:

- `terminationCode`
- `primalCode`
- `dualCode`
- `nIter`
- `dPrimalObj`
- `dDualObj`
- `dPrimalFeas`
- `dDualFeas`
- `dDualityGap`
- `dRelPrimalFeas`
- `dRelDualFeas`
- `dRelDualityGap`
- `dSolvingTime`

## Numerical tolerance policy

CPU and ROCm/HIP results are not expected to be bitwise identical.

Differences may come from:

- different BLAS/SPARSE implementations
- different floating-point reduction order
- different GPU architecture behavior
- different sparse matrix-vector execution order

Validation should use tolerances instead of exact equality.

Initial suggested tolerances:

| Metric type | Suggested tolerance |
|---|---:|
| Objective value absolute difference | `1e-3` to `1e-2` |
| Relative feasibility difference | `1e-4` |
| Relative duality gap difference | `1e-4` |
| Termination status | must match or be explainable |

These tolerances are initial engineering values and should be refined as more cases are tested.

## Planned validation cases

Small cases:

- `example/afiro.mps`
- additional small Netlib LP cases

Medium cases:

- TBD

Large cases:

- TBD

Stress cases:

- infeasible LP
- unbounded LP
- badly scaled LP
- sparse large LP
- dense-ish LP

## Validation workflow

Recommended workflow:

```bash
# CPU baseline
./build-cpu/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_cpu_sum.json \
  -nIterLim 200

# ROCm/HIP run
./build-rocm-plc/bin/plc \
  -fname ./example/afiro.mps \
  -out /tmp/afiro_hip_sum.json \
  -nIterLim 200

A comparison script should later be added under:

scripts/compare_cpu_rocm.py

# TODO

Add scripts/compare_cpu_rocm.py
Add scripts/run_validation.sh
Add more MPS test cases
Record CPU vs ROCm result tables
Add validation results for other ROCm-supported GPUs

## Current validation result

Latest verified case:

| Case | CPU status | ROCm status | Result |
|---|---|---|---|
| `example/afiro.mps` | `OPTIMAL` | `OPTIMAL` | PASS |

For `afiro.mps` with `nIterLim=200`, CPU and ROCm results match within the current validation tolerances.

Key comparison:

| Metric | CPU | ROCm | Result |
|---|---:|---:|---|
| `nIter` | `199` | `199` | PASS |
| `dPrimalObj` | `-464.7634630424535` | `-464.7634605703561` | PASS |
| `dDualObj` | `-464.8342621613099` | `-464.8342273564149` | PASS |
| `dRelPrimalFeas` | `3.926084712e-05` | `3.927125321e-05` | PASS |
| `dRelDualFeas` | `5.66716996e-06` | `5.655315e-06` | PASS |
| `dRelDualityGap` | `7.607918754e-05` | `7.604444646e-05` | PASS |

Generated detailed reports are written under:

```text
validation/results/latest/
This directory is ignored by Git because it contains generated validation outputs.

## Validation levels

This project currently uses two validation levels.

### Smoke validation

Smoke validation is the default workflow:

```bash
./scripts/run_validation.sh

Current smoke cases:

Case	Backend comparison	Result
example/afiro.mps	CPU vs ROCm	PASS
validation/netlib/sc50b.mps	CPU vs ROCm	PASS

Smoke validation must pass before changing ROCm/HIP backend code.

Extended Netlib validation

Extended validation uses additional small Netlib LP cases prepared through scripts/prepare_netlib_cases.sh.

Run extended validation with:

RESULT_ROOT=validation/results/extended_netlib ./scripts/run_validation.sh validation/cases_extended_netlib.txt

Current extended status:

Case	Result	Notes
afiro	PASS	Baseline example
adlittle	PASS	Relative validation metrics pass
blend	PASS	Relative validation metrics pass
sc50a	PASS	Relative validation metrics pass
sc50b	PASS	Smoke + extended case
share2b	INCOMPLETE	Hits iteration/time limit at current settings
Comparison semantics

The validation comparison script treats solver status codes as hard checks.

When both CPU and ROCm report OPTIMAL, the main hard numeric checks are:

dRelPrimalFeas
dRelDualFeas
dRelDualityGap

The following fields are recorded as diagnostics and are not hard failure criteria by themselves:

nIter
dPrimalObj
dDualObj
dPrimalFeas
dDualFeas
dDualityGap

This is intentional because CPU and ROCm runs can follow slightly different floating-point trajectories while still reaching equivalent relative feasibility and gap criteria

## CTest integration

The ROCm port checks are also registered with CTest when the project is configured with `BUILD_TESTING=ON`.

Example:

```bash
ctest --test-dir build-rocm-plc --output-on-failure

Current registered tests:

Test	Purpose	Expected result
rocm_port_hygiene	Checks ROCm/HIP naming and compatibility guardrails	PASS
rocm_smoke_validation	Runs CPU-vs-ROCm smoke validation	PASS

CTest is the recommended standard entry point after configuring a ROCm build tree.

