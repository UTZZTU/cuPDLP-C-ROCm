# Competition Review Entry: ROCm Migration and Evidence for a Large-Scale LP Solver

> 中文：[COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)
> Project homepage: [README.en.md](../README.en.md)
> Final formal results: [W7900_FINAL_RESULTS_20260729.md](W7900_FINAL_RESULTS_20260729.md)

This page maps the general open-source project to competition-review needs. It
does not redefine the repository as contest-only software.

## Project question

> How can a real CUDA-oriented large-scale LP solver be migrated to AMD
> ROCm/HIP and supported by traceable evidence for buildability, numerical
> validity, performance interpretation, and safe tuning?

The project does not introduce a new PDLP algorithm. Its contributions are
three-backend engineering, CUDA-to-ROCm migration, validation, profiling,
conservative tuning, negative evidence, and a formal evidence contract.

## Final evidence

| Area | Contribution | Final evidence |
|---|---|---|
| ROCm/HIP migration | AMD backend while preserving CPU/CUDA | Migration case study |
| Formal baseline | nonhard23 × 2 | 46/46 `VALIDATED_OPTIMAL` |
| Tolerance sensitivity | 5 × 3 × 2 | 30/30 `VALIDATED_OPTIMAL` |
| Resources | VRAM, utilization, power, temperature, clocks | Samples for every formal run |
| Profiling | targeted rocprof | P10 compact hotspots + final 5/5 trace validation |
| Safe tuning | P11 accepted `CSR_ALG1` | `csr_alg2` fallback retained |
| Negative evidence | P12 changed iterations | Patch rejected and preserved |
| Repeated validation | P14-A1 quick6 | Current wins 6/6 with identical iterations |
| Final QC | source/data/internal identity | `FINAL_ANALYSIS_RELEASED` |
| Reproducibility | compact data, scripts, figures, docs | Inspectable on ordinary Linux |

## Final W7900 numbers

| Metric | Result |
|---|---:|
| Formal solver runs | **76/76 validated** |
| nonhard23 | 23 cases × 2 repeats |
| Complete-repeat total time | 2950.625997 s / 2950.674611 s |
| Mean sequential throughput | **28.061611 cases/hour** |
| Median total-time CV | **0.377%** |
| Top-three total-time share | **82.22%** |
| Tolerance matrix | 30/30 |
| Profiles | 5/5 `PASS` |
| Maximum achieved-error/requested-tolerance | **0.998079** |

## Interpretation

```text
total time
  ≈ input parsing, initialization, and finalization
  + per-iteration execution cost × iteration count
```

The final workload profile separates iteration/compute-dominated cases from
load/initialization-dominated cases. Tolerance cost is strongly case-dependent,
and static-size associations with VRAM do not establish causation.

![W7900 workload profile](assets/w7900/final20260729/workload_profile.en.svg)

![Tolerance, runtime, and VRAM](assets/w7900/final20260729/precision_resource_tradeoff.en.svg)

## Profiling-to-tuning chain

P10 identifies rocSPARSE CSR SpMV as a major kernel group and copy/launch
overhead as secondary concerns. P11 accepts a controlled library-algorithm
policy. P12 is rejected after an iteration-trajectory change. P14-A1 confirms
repeated current gains with identical iteration counts. Final session2 validates
five profile collections and their trace integrity.

## Recommended review path

1. Project homepage
2. Final formal results
3. CUDA-to-ROCm migration case study
4. W7900 performance behavior
5. Profiling notes
6. Validation semantics
7. Final reproduction guide
8. Final compact evidence
9. Competition scorecard

## Claim boundaries

Supported: migration, three-backend boundaries, 76/76 formal validation,
workload and tolerance analysis, evidence-driven safe tuning, and compact
reproducibility.

Not supported: a new PDLP algorithm, universal W7900 superiority, one-LP
multi-GPU solving, generalization from five tolerance cases to all LPs,
causal static-correlation claims, complete Docker reproduction of formal
measurements, or certification of all AMD architectures.
