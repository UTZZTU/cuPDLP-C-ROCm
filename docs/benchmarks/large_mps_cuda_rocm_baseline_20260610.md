<!-- Navigation: [Benchmark index](README.md) · [Documentation map](../README.md) · CSV: [platform summary](../../results/benchmarks/large_mps_platform_summary_20260610.csv), [per-case timing](../../results/benchmarks/large_mps_per_case_timing_summary_20260610.csv) -->

# Large MPS benchmark summary: CUDA baselines and ROCm baseline

Date: 2026-06-10  
Dataset: 26 large `.mps` LP instances.  
Purpose: record the current cuPDLP-C CUDA and ROCm/HIP baseline results for the cuPDLP-C to ROCm migration project.

## Background

cuPDLP-C is the upstream C implementation of cuPDLP for solving LPs on GPUs using first-order PDLP methods. This repository ports that CUDA-oriented implementation to ROCm/HIP. cuPDLPx is a newer GPU LP solver line and is being evaluated separately, so its results are not mixed into this cuPDLP-C baseline table.

## Common configuration

```text
nIterLim / iter_limit = 1000000000
dTimeLim / time_limit = 7200 seconds
external timeout      = 7500 seconds per case
```

Notes:

- RTX 4090D and H100 were run as full 26-case CUDA sweeps with `dTimeLim=7200`.
- RTX 3090 uses the original full sweep for cases that solved before the default 3600-second limit, with `dlr1.mps` replaced by a 7200-second rerun.
- Radeon 890M uses the original ROCm baseline sweep plus 7200-second reruns for `dlr1.mps`, `Dual2_5000.mps`, and `fhnw-binschedule1.mps`.
- H100 raw `tier/size_bytes` columns are ignored because the input MPS directory used symlinks; canonical size/tier metadata is taken from the 4090D dataset summary.

## Platform summary

| Device | Backend | Solver | Commit | OPTIMAL | TIMELIMIT | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| RTX 3090 | CUDA | cuPDLP-C upstream | 7b94c41 | 25/26 | 1/26 | dlr1 replaced by dTimeLim=7200 rerun; other solved rows from original sweep. |
| Radeon 890M | ROCm/HIP | cuPDLP-C-ROCm baseline | ae3b683 | 24/26 | 2/26 | dlr1, Dual2_5000, fhnw-binschedule1 replaced by dTimeLim=7200 reruns. |
| RTX 4090D | CUDA | cuPDLP-C upstream | 7b94c41 | 26/26 | 0/26 | Full 26-case sweep with dTimeLim=7200. |
| H100 PCIe | CUDA | cuPDLP-C upstream | 7b94c41 | 26/26 | 0/26 | Full 26-case sweep with dTimeLim=7200; raw H100 tier/size ignored because symlink size was measured. |

## Key observations

1. **RTX 4090D and H100 solved all 26 cases**.
2. **RTX 3090 solved 25/26 cases**; only `dlr1.mps` remained time-limited after the 7200-second rerun.
3. **Radeon 890M ROCm baseline solved 24/26 cases**, which is a useful portability and correctness signal for an integrated GPU platform.
4. `dlr1.mps` and `Dual2_5000.mps` are the most discriminative hard cases in the current dataset.
5. cuPDLPx short13 has been benchmarked separately on RTX 4090D and documented separately. It remains a separate solver/algorithm comparison and should not be mixed into the cuPDLP-C ROCm baseline table.

## Hard-case snapshot

| Case | Tier | RTX 3090 | Radeon 890M | RTX 4090D | H100 |
| --- | --- | --- | --- | --- | --- |
| dlr1.mps | XL | TIMELIMIT_OR_ITERLIMIT; solve=7200.014369s; wall=7238.71s | TIMELIMIT_OR_ITERLIMIT; solve=7200.010023s; wall=7218.43s | OPTIMAL; solve=5150.691177s; wall=5244.79s | OPTIMAL; solve=2691.242682s; wall=2719.08s |
| Dual2_5000.mps | XXL | OPTIMAL; solve=1533.367997s; wall=1839.78s | TIMELIMIT_OR_ITERLIMIT; solve=7200.191719s; wall=7382.47s | OPTIMAL; solve=807.038528s; wall=1617.02s | OPTIMAL; solve=1336.854824s; wall=1563.83s |
| fhnw-binschedule1.mps | L | OPTIMAL; solve=200.793847s; wall=216.33s | OPTIMAL; solve=5309.224427s; wall=5317.32s | OPTIMAL; solve=82.821262s; wall=192.59s | OPTIMAL; solve=84.740679s; wall=95.04s |
| Primal2_1000.mps | L | OPTIMAL; solve=1084.517597s; wall=1098.8s | OPTIMAL; solve=301.318529s; wall=308.08s | OPTIMAL; solve=970.553189s; wall=993.75s | OPTIMAL; solve=949.049856s; wall=958.5s |
| s100.mps | L | OPTIMAL; solve=134.999971s; wall=139.61s | OPTIMAL; solve=2004.671944s; wall=2006.64s | OPTIMAL; solve=111.008752s; wall=125.13s | OPTIMAL; solve=138.788371s; wall=141.9s |

## Full per-case status and wall time

| Case | Tier | RTX 3090 | Radeon 890M | RTX 4090D | H100 |
| --- | --- | --- | --- | --- | --- |
| a2864.mps | XL | OPTIMAL / 25.99s | OPTIMAL / 20.78s | OPTIMAL / 90.59s | OPTIMAL / 20.2s |
| datt256_lp.mps | M | OPTIMAL / 2.99s | OPTIMAL / 2.33s | OPTIMAL / 16.22s | OPTIMAL / 4.02s |
| dlr1.mps | XL | TIMELIMIT_OR_ITERLIMIT / 7238.71s | TIMELIMIT_OR_ITERLIMIT / 7218.43s | OPTIMAL / 5244.79s | OPTIMAL / 2719.08s |
| Dual2_5000.mps | XXL | OPTIMAL / 1839.78s | TIMELIMIT_OR_ITERLIMIT / 7382.47s | OPTIMAL / 1617.02s | OPTIMAL / 1563.83s |
| ex10.mps | M | OPTIMAL / 1.67s | OPTIMAL / 0.92s | OPTIMAL / 11.34s | OPTIMAL / 1.63s |
| fhnw-binschedule1.mps | L | OPTIMAL / 216.33s | OPTIMAL / 5317.32s | OPTIMAL / 192.59s | OPTIMAL / 95.04s |
| graph40-40.mps | L | OPTIMAL / 3.42s | OPTIMAL / 1.85s | OPTIMAL / 18.85s | OPTIMAL / 2.35s |
| irish-electricity.mps | M | OPTIMAL / 9.26s | OPTIMAL / 27.48s | OPTIMAL / 16.35s | OPTIMAL / 7.36s |
| L2CTA3D.mps | XXL | OPTIMAL / 82.91s | OPTIMAL / 37.89s | OPTIMAL / 387.39s | OPTIMAL / 55.57s |
| neos-3025225.mps | L | OPTIMAL / 17.99s | OPTIMAL / 33.83s | OPTIMAL / 44.76s | OPTIMAL / 11.0s |
| neos-5052403-cygnet.mps | L | OPTIMAL / 7.85s | OPTIMAL / 17.16s | OPTIMAL / 9.6s | OPTIMAL / 5.47s |
| neos-5251015.mps | L | OPTIMAL / 4.07s | OPTIMAL / 3.13s | OPTIMAL / 6.61s | OPTIMAL / 2.81s |
| Primal2_1000.mps | L | OPTIMAL / 1098.8s | OPTIMAL / 308.08s | OPTIMAL / 993.75s | OPTIMAL / 958.5s |
| qap15.mps | M | OPTIMAL / 0.89s | OPTIMAL / 0.63s | OPTIMAL / 1.44s | OPTIMAL / 0.72s |
| rmine15.mps | M | OPTIMAL / 5.13s | OPTIMAL / 34.72s | OPTIMAL / 12.82s | OPTIMAL / 4.13s |
| s100.mps | L | OPTIMAL / 139.61s | OPTIMAL / 2006.64s | OPTIMAL / 125.13s | OPTIMAL / 141.9s |
| s250r10.mps | L | OPTIMAL / 4.39s | OPTIMAL / 10.3s | OPTIMAL / 16.92s | OPTIMAL / 4.88s |
| savsched1.mps | L | OPTIMAL / 3.89s | OPTIMAL / 2.64s | OPTIMAL / 12.23s | OPTIMAL / 2.96s |
| scpm1.mps | L | OPTIMAL / 10.52s | OPTIMAL / 8.6s | OPTIMAL / 44.57s | OPTIMAL / 7.07s |
| set-cover-model.mps | XL | OPTIMAL / 39.93s | OPTIMAL / 159.38s | OPTIMAL / 81.2s | OPTIMAL / 34.74s |
| square41.mps | XL | OPTIMAL / 98.88s | OPTIMAL / 568.9s | OPTIMAL / 197.62s | OPTIMAL / 245.92s |
| supportcase10.mps | M | OPTIMAL / 4.1s | OPTIMAL / 13.1s | OPTIMAL / 5.74s | OPTIMAL / 13.26s |
| thk_48.mps | XL | OPTIMAL / 138.48s | OPTIMAL / 731.1s | OPTIMAL / 170.63s | OPTIMAL / 77.32s |
| thk_63.mps | XL | OPTIMAL / 123.24s | OPTIMAL / 542.74s | OPTIMAL / 211.73s | OPTIMAL / 68.4s |
| tpl-tub-ws1617.mps | XL | OPTIMAL / 69.62s | OPTIMAL / 480.0s | OPTIMAL / 237.89s | OPTIMAL / 27.9s |
| woodlands09.mps | L | OPTIMAL / 4.74s | OPTIMAL / 3.54s | OPTIMAL / 17.38s | OPTIMAL / 3.24s |

## CSV files

- `results/benchmarks/large_mps_platform_summary_20260610.csv`
- `results/benchmarks/large_mps_per_case_timing_summary_20260610.csv`
