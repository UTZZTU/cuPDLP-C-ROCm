# Competition Scorecard and Final Repository Evidence

> 中文：[COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md)

| Review area | Repository evidence | Final status and boundary |
|---|---|---|
| Motivation and challenge | Competition entry, migration case study | Real scientific-computing migration; not a new algorithm |
| Architecture | HIP backend and backend-mode docs | CPU/CUDA/ROCm boundaries |
| ROCm components | HIP, hipBLAS, hipSPARSE, rocprofv3 | Real W7900 evidence |
| Correctness | Validation semantics and final results | 76/76 formal runs validated |
| Baseline and throughput | Final compact evidence | Mean sequential throughput 28.061611 cases/hour |
| Tolerance study | Precision CSV and figures | 30/30 across five cases |
| Resources | Resource CSV and trade-off figure | VRAM/utilization/power sampling |
| Profiling | P10 compact plus final profile summary | P10 supports hotspots; final traces 5/5 PASS |
| Safe tuning | P11, P12, P14-A1 | Accepted, rejected, and repeated evidence preserved |
| Workload profile | Performance behavior | Iteration- versus initialization-dominated cases |
| Static features | 23/23 feature validation | Exploratory, non-causal |
| Multi-GPU | Historical fast8 | Independent-task throughput only |
| Reproducibility | Final reproduction guide | Inspection/regeneration on ordinary Linux |
| Delivery | README, map, checksums, verification scripts | Final release package |

## Key numbers

| Claim | Value |
|---|---:|
| Formal solver records | 76/76 |
| nonhard23 | 23 × 2 = 46 |
| tolerance matrix | 5 × 3 × 2 = 30 |
| profiles | 5/5 |
| Mean sequential throughput | 28.061611 cases/hour |
| Median total-time CV | 0.377% |
| Top-three total-time share | 82.22% |
| Maximum achieved-error/requested-tolerance | 0.998079 |

## Required interpretation rules

- Formal harness and frozen solver have different roles.
- Throughput means independent MPS cases, not one-LP multi-GPU.
- hard3 remains separate.
- P12 negative evidence remains visible.
- Tolerance conclusions cover five cases.
- Static correlations are non-causal.
- Docker is not the source of formal measurements.
