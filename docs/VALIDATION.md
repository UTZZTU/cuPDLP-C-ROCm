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
./build-hip-plc/bin/plc \
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
