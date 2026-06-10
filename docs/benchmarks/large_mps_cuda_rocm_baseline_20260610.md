# Large MPS benchmark summary: CUDA baselines and ROCm baseline

Date: 2026-06-10  
Dataset: 26 large `.mps` LP instances shared across CUDA and ROCm runs.

This document records the current benchmark state for the cuPDLP-C to ROCm migration project. cuPDLPx is being tested separately on RTX 4090D and is not merged into this baseline table yet.

## Public project context

- cuPDLP-C is the upstream C implementation of cuPDLP for solving LPs on GPU using first-order PDLP methods.
- cuPDLPx/cuPDLP+ is a newer GPU-accelerated first-order LP solver based on restarted Halpern PDHG and is being evaluated separately as a future direction.

References:

- https://github.com/COPT-Public/cuPDLP-C
- https://arxiv.org/abs/2312.14832
- https://github.com/MIT-Lu-Lab/cuPDLPx
- https://arxiv.org/abs/2507.14051

## Benchmark configuration

Common target configuration:

```text
nIterLim / iter_limit = 1000000000
dTimeLim / time_limit = 7200 seconds
external timeout      = 7500 seconds per case
```

Important notes:

- RTX 4090D and H100 were run as full 26-case CUDA sweeps with `dTimeLim=7200`.
- RTX 3090 uses the earlier full sweep for solved cases and replaces only `dlr1.mps` with the `dTimeLim=7200` rerun.
- Radeon 890M uses the earlier ROCm baseline sweep for 23 solved cases and replaces `dlr1.mps`, `Dual2_5000.mps`, and `fhnw-binschedule1.mps` with `dTimeLim=7200` reruns.
- H100 raw `tier` and `size_bytes` are not used because its input directory contained symlinks; this document uses canonical case size/tier metadata from the 4090D run.

## Platform summary

| Device | Backend | Solver | Commit | OPTIMAL | TIMELIMIT |
| --- | --- | --- | --- | --- | --- |
| RTX 3090 | CUDA | cuPDLP-C upstream | 7b94c41 | 25/26 | 1/26 |
| Radeon 890M | ROCm/HIP | cuPDLP-C-ROCm baseline | ae3b683 | 24/26 | 2/26 |
| RTX 4090D | CUDA | cuPDLP-C upstream | 7b94c41 | 26/26 | 0/26 |
| H100 PCIe | CUDA | cuPDLP-C upstream | 7b94c41 | 26/26 | 0/26 |

## Key observations

1. RTX 4090D and H100 both solved all 26 cases under the 7200-second solver time limit.
2. RTX 3090 solved 25/26 cases; `dlr1.mps` remained `TIMELIMIT_OR_ITERLIMIT` after the 7200-second rerun.
3. Radeon 890M ROCm baseline solved 24/26 cases. `fhnw-binschedule1.mps` became `OPTIMAL` after the 7200-second rerun, while `dlr1.mps` and `Dual2_5000.mps` remained time-limited.
4. The 890M result is useful as a ROCm portability and correctness signal: it solves most large MPS instances despite being an integrated GPU platform.
5. cuPDLPx should be documented separately until its RTX 4090D short-case comparison is reviewed.

## Hard-case snapshot

| case | tier | 3090 status / solve(s) | 4090D status / solve(s) | H100 status / solve(s) | 890M status / solve(s) |
| --- | --- | --- | --- | --- | --- |
| dlr1.mps | XL | TIMELIMIT_OR_ITERLIMIT / 7200.014369 | OPTIMAL / 5150.691177 | OPTIMAL / 2691.242682 | TIMELIMIT_OR_ITERLIMIT / 7200.010023 |
| Dual2_5000.mps | XXL | OPTIMAL / 1533.367997 | OPTIMAL / 807.038528 | OPTIMAL / 1336.854824 | TIMELIMIT_OR_ITERLIMIT / 7200.191719 |
| fhnw-binschedule1.mps | L | OPTIMAL / 200.793847 | OPTIMAL / 82.821262 | OPTIMAL / 84.740679 | OPTIMAL / 5309.224427 |
| Primal2_1000.mps | L | OPTIMAL / 1084.517597 | OPTIMAL / 970.553189 | OPTIMAL / 949.049856 | OPTIMAL / 301.318529 |
| s100.mps | L | OPTIMAL / 134.999971 | OPTIMAL / 111.008752 | OPTIMAL / 138.788371 | OPTIMAL / 2004.671944 |

## Full per-case status / wall time snapshot

| case | tier | 3090 status/wall(s) | 4090D status/wall(s) | H100 status/wall(s) | 890M status/wall(s) |
| --- | --- | --- | --- | --- | --- |
| a2864.mps | XL | OPTIMAL / 25.99 | OPTIMAL / 90.59 | OPTIMAL / 20.2 | OPTIMAL / 20.78 |
| datt256_lp.mps | M | OPTIMAL / 2.99 | OPTIMAL / 16.22 | OPTIMAL / 4.02 | OPTIMAL / 2.33 |
| dlr1.mps | XL | TIMELIMIT_OR_ITERLIMIT / 7238.71 | OPTIMAL / 5244.79 | OPTIMAL / 2719.08 | TIMELIMIT_OR_ITERLIMIT / 7218.43 |
| Dual2_5000.mps | XXL | OPTIMAL / 1839.78 | OPTIMAL / 1617.02 | OPTIMAL / 1563.83 | TIMELIMIT_OR_ITERLIMIT / 7382.47 |
| ex10.mps | M | OPTIMAL / 1.67 | OPTIMAL / 11.34 | OPTIMAL / 1.63 | OPTIMAL / 0.92 |
| fhnw-binschedule1.mps | L | OPTIMAL / 216.33 | OPTIMAL / 192.59 | OPTIMAL / 95.04 | OPTIMAL / 5317.32 |
| graph40-40.mps | L | OPTIMAL / 3.42 | OPTIMAL / 18.85 | OPTIMAL / 2.35 | OPTIMAL / 1.85 |
| irish-electricity.mps | M | OPTIMAL / 9.26 | OPTIMAL / 16.35 | OPTIMAL / 7.36 | OPTIMAL / 27.48 |
| L2CTA3D.mps | XXL | OPTIMAL / 82.91 | OPTIMAL / 387.39 | OPTIMAL / 55.57 | OPTIMAL / 37.89 |
| neos-3025225.mps | L | OPTIMAL / 17.99 | OPTIMAL / 44.76 | OPTIMAL / 11.0 | OPTIMAL / 33.83 |
| neos-5052403-cygnet.mps | L | OPTIMAL / 7.85 | OPTIMAL / 9.6 | OPTIMAL / 5.47 | OPTIMAL / 17.16 |
| neos-5251015.mps | L | OPTIMAL / 4.07 | OPTIMAL / 6.61 | OPTIMAL / 2.81 | OPTIMAL / 3.13 |
| Primal2_1000.mps | L | OPTIMAL / 1098.8 | OPTIMAL / 993.75 | OPTIMAL / 958.5 | OPTIMAL / 308.08 |
| qap15.mps | M | OPTIMAL / 0.89 | OPTIMAL / 1.44 | OPTIMAL / 0.72 | OPTIMAL / 0.63 |
| rmine15.mps | M | OPTIMAL / 5.13 | OPTIMAL / 12.82 | OPTIMAL / 4.13 | OPTIMAL / 34.72 |
| s100.mps | L | OPTIMAL / 139.61 | OPTIMAL / 125.13 | OPTIMAL / 141.9 | OPTIMAL / 2006.64 |
| s250r10.mps | L | OPTIMAL / 4.39 | OPTIMAL / 16.92 | OPTIMAL / 4.88 | OPTIMAL / 10.3 |
| savsched1.mps | L | OPTIMAL / 3.89 | OPTIMAL / 12.23 | OPTIMAL / 2.96 | OPTIMAL / 2.64 |
| scpm1.mps | L | OPTIMAL / 10.52 | OPTIMAL / 44.57 | OPTIMAL / 7.07 | OPTIMAL / 8.6 |
| set-cover-model.mps | XL | OPTIMAL / 39.93 | OPTIMAL / 81.2 | OPTIMAL / 34.74 | OPTIMAL / 159.38 |
| square41.mps | XL | OPTIMAL / 98.88 | OPTIMAL / 197.62 | OPTIMAL / 245.92 | OPTIMAL / 568.9 |
| supportcase10.mps | M | OPTIMAL / 4.1 | OPTIMAL / 5.74 | OPTIMAL / 13.26 | OPTIMAL / 13.1 |
| thk_48.mps | XL | OPTIMAL / 138.48 | OPTIMAL / 170.63 | OPTIMAL / 77.32 | OPTIMAL / 731.1 |
| thk_63.mps | XL | OPTIMAL / 123.24 | OPTIMAL / 211.73 | OPTIMAL / 68.4 | OPTIMAL / 542.74 |
| tpl-tub-ws1617.mps | XL | OPTIMAL / 69.62 | OPTIMAL / 237.89 | OPTIMAL / 27.9 | OPTIMAL / 480.0 |
| woodlands09.mps | L | OPTIMAL / 4.74 | OPTIMAL / 17.38 | OPTIMAL / 3.24 | OPTIMAL / 3.54 |

## Raw CSV files in this bundle

- `results/benchmarks/large_mps_platform_summary_20260610.csv`
- `results/benchmarks/large_mps_per_case_timing_summary_20260610.csv`

## Source run directories

```text
3090:
  /home/psdz/cuPDLP-C/test_data_large_mps/large_mps_3090_upstream_26cases_niter1b_20260610_015140
  /home/psdz/cuPDLP-C/test_data_large_mps/large_mps_3090_dlr1_niter1b_dtimelim7200_20260610_103452

890M:
  /home/bjut316/cuPDLP-C/test_data_large_mps/large_mps_890m_rocm_ae3b683_niter1b_20260610_022207
  /home/bjut316/cuPDLP-C/test_data_large_mps/large_mps_890m_rocm_ae3b683_3cases_dtimelim7200_20260610_104927

4090D:
  /home/omnisky/cuPDLP-C/test_data_large_mps/large_mps_4090_upstream_26cases_niter1b_dtimelim7200_20260610_162424

H100:
  /home/wangwenbo/cuPDLP-C/test_data_large_mps/large_mps_h100_upstream_26cases_niter1b_dtimelim7200_20260610_185127
```

## Future updates

- Add W7900/gfx1100 results after the W7900 branch is smoke-tested and benchmarked.
- Add cuPDLPx results in a separate document first because it is a different solver/algorithm line.
- If rerunning H100 with symlinked MPS files, use `stat -Lc%s "$mps"` instead of `stat -c%s "$mps"` when deriving file-size tiers.
