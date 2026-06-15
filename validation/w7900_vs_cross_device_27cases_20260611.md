# W7900 vs existing cross-device Netlib reference 20260611

> 中文: [w7900_vs_cross_device_27cases_20260611.zh-CN.md](w7900_vs_cross_device_27cases_20260611.zh-CN.md)

CSV source: [w7900_vs_cross_device_27cases_20260611.csv](w7900_vs_cross_device_27cases_20260611.csv)

Compared inputs:

- Existing cross-device reference: [cross_device_full_summary.csv](cross_device_full_summary.csv)
- W7900 baseline: [w7900_27cases_baseline_20260611_aggregated.csv](w7900_27cases_baseline_20260611_aggregated.csv)

Metric definition:

```text
old_over_w7900_speed_ratio = old_platform_gpu_time_sec / W7900_median_solve_time_sec
> 1.0 means W7900 is faster for that case.
< 1.0 means the existing reference platform is faster for that case.
```

Important caveat: the existing cross-device CSV records single-run `gpu_time_sec`, while the W7900 baseline uses repeated-run median solve time. This is a cross-device reference comparison, not a same-platform tuning-gain measurement.

## Platform summary

| device | cases | geomean old/W7900 | median old/W7900 | W7900 faster cases | other faster cases |
|---|---:|---:|---:|---:|---:|
| RTX 3090 CUDA | 27 | 0.646364 | 0.556064 | 5 | 22 |
| RTX 4090D CUDA | 27 | 0.599578 | 0.528769 | 4 | 23 |
| Radeon 890M ROCm | 27 | 0.552744 | 0.473843 | 1 | 26 |

## Interpretation

- W7900 is not yet faster overall in this current W7900 Netlib engineering baseline. This baseline is before W7900-specific tuning and should not be interpreted as the final optimized ROCm/gfx1100 result.
- The result should be used to identify tuning targets, not to judge final hardware capability.
- Future W7900 tuning should compare against the W7900 baseline on the same platform, using the same 27-case list and repeated median metric.

## Per-case comparison

| device | case | tier | old time | W7900 median | old/W7900 | winner | old iter | W7900 iter |
|---|---|---|---:|---:|---:|---|---:|---|
| RTX 3090 CUDA | 25fv47 | L | 0.559851 | 1.205027 | 0.464596 | RTX 3090 | 6560 | 9680;9680;9680 |
| RTX 3090 CUDA | 80bau3b | L | 1.05833 | 1.023789 | 1.03374 | W7900 | 11720 | 7800;7800;7800 |
| RTX 3090 CUDA | afiro | S | 0.035574 | 0.106813 | 0.333049 | RTX 3090 | 200 | 200;200;200 |
| RTX 3090 CUDA | degen2 | M | 0.126777 | 0.22799 | 0.556064 | RTX 3090 | 1400 | 1360;1360;1360 |
| RTX 3090 CUDA | degen3 | L | 0.694678 | 0.801251 | 0.866992 | RTX 3090 | 7960 | 6000;6000;6000 |
| RTX 3090 CUDA | fit1d | M | 0.252616 | 0.521367 | 0.484526 | RTX 3090 | 2960 | 3520;3520;3520 |
| RTX 3090 CUDA | fit2d | L | 0.430777 | 1.493279 | 0.288477 | RTX 3090 | 4640 | 5040;5040;5040 |
| RTX 3090 CUDA | greenbeb | L | 81.6909 | 61.144834 | 1.33602 | W7900 | 965560 | 502640;502640;502640 |
| RTX 3090 CUDA | israel | M | 0.202475 | 0.348547 | 0.580912 | RTX 3090 | 2560 | 2480;2480;2480 |
| RTX 3090 CUDA | lotfi | S | 7.2219 | 8.437827 | 0.855896 | RTX 3090 | 102400 | 85840;85840;85840 |
| RTX 3090 CUDA | maros-r7 | L | 0.074724 | 0.152325 | 0.490556 | RTX 3090 | 560 | 560;560;560 |
| RTX 3090 CUDA | pilot4 | M | 218.612 | 110.295226 | 1.98206 | W7900 | 2979880 | 1119160;1119160;1119160 |
| RTX 3090 CUDA | pilot87 | L | 7.98787 | 10.432215 | 0.765693 | RTX 3090 | 91880 | 82240;82240;82240 |
| RTX 3090 CUDA | recipe | S | 0.065269 | 0.159525 | 0.409146 | RTX 3090 | 720 | 720;720;720 |
| RTX 3090 CUDA | sc105 | S | 0.230136 | 0.433761 | 0.530559 | RTX 3090 | 3120 | 3560;3560;3560 |
| RTX 3090 CUDA | sc205 | S | 1.00029 | 1.373476 | 0.728291 | RTX 3090 | 15680 | 13320;13320;13320 |
| RTX 3090 CUDA | sc50b | S | 0.066647 | 0.139734 | 0.476956 | RTX 3090 | 560 | 560;560;560 |
| RTX 3090 CUDA | scagr25 | M | 1.43483 | 1.545581 | 0.928343 | RTX 3090 | 19400 | 14800;14800;14800 |
| RTX 3090 CUDA | scagr7 | S | 0.356301 | 0.423053 | 0.842214 | RTX 3090 | 5400 | 3400;3400;3400 |
| RTX 3090 CUDA | scfxm1 | M | 0.564645 | 1.144653 | 0.493289 | RTX 3090 | 7520 | 10920;10920;10920 |
| RTX 3090 CUDA | scfxm2 | M | 1.80875 | 1.312772 | 1.37781 | W7900 | 23920 | 12000;12000;12000 |
| RTX 3090 CUDA | scfxm3 | M | 1.68529 | 1.57367 | 1.07093 | W7900 | 20600 | 13120;13120;13120 |
| RTX 3090 CUDA | sctap1 | M | 0.149817 | 0.247539 | 0.605226 | RTX 3090 | 1560 | 1560;1560;1560 |
| RTX 3090 CUDA | sctap2 | M | 0.105992 | 0.194312 | 0.545473 | RTX 3090 | 960 | 920;920;920 |
| RTX 3090 CUDA | ship04s | M | 0.371501 | 0.712118 | 0.521685 | RTX 3090 | 4320 | 5440;5440;5440 |
| RTX 3090 CUDA | ship08s | M | 0.363455 | 0.68956 | 0.527082 | RTX 3090 | 4160 | 5240;5240;5240 |
| RTX 3090 CUDA | stair | M | 2.07426 | 5.640418 | 0.367749 | RTX 3090 | 28520 | 56080;56080;56080 |
| RTX 4090D CUDA | 25fv47 | L | 0.532387 | 1.205027 | 0.441805 | RTX 4090D | 6560 | 9680;9680;9680 |
| RTX 4090D CUDA | 80bau3b | L | 0.873151 | 1.023789 | 0.852862 | RTX 4090D | 11720 | 7800;7800;7800 |
| RTX 4090D CUDA | afiro | S | 0.033316 | 0.106813 | 0.31191 | RTX 4090D | 200 | 200;200;200 |
| RTX 4090D CUDA | degen2 | M | 0.121058 | 0.22799 | 0.530979 | RTX 4090D | 1400 | 1360;1360;1360 |
| RTX 4090D CUDA | degen3 | L | 0.616253 | 0.801251 | 0.769114 | RTX 4090D | 7960 | 6000;6000;6000 |
| RTX 4090D CUDA | fit1d | M | 0.249037 | 0.521367 | 0.477662 | RTX 4090D | 2960 | 3520;3520;3520 |
| RTX 4090D CUDA | fit2d | L | 0.376708 | 1.493279 | 0.252269 | RTX 4090D | 4640 | 5040;5040;5040 |
| RTX 4090D CUDA | greenbeb | L | 72.3501 | 61.144834 | 1.18326 | W7900 | 965560 | 502640;502640;502640 |
| RTX 4090D CUDA | israel | M | 0.237514 | 0.348547 | 0.68144 | RTX 4090D | 2560 | 2480;2480;2480 |
| RTX 4090D CUDA | lotfi | S | 6.37122 | 8.437827 | 0.755078 | RTX 4090D | 102400 | 85840;85840;85840 |
| RTX 4090D CUDA | maros-r7 | L | 0.061516 | 0.152325 | 0.403847 | RTX 4090D | 560 | 560;560;560 |
| RTX 4090D CUDA | pilot4 | M | 214.632 | 110.295226 | 1.94598 | W7900 | 2979880 | 1119160;1119160;1119160 |
| RTX 4090D CUDA | pilot87 | L | 8.00709 | 10.432215 | 0.767535 | RTX 4090D | 91880 | 82240;82240;82240 |
| RTX 4090D CUDA | recipe | S | 0.056562 | 0.159525 | 0.354565 | RTX 4090D | 720 | 720;720;720 |
| RTX 4090D CUDA | sc105 | S | 0.200001 | 0.433761 | 0.461086 | RTX 4090D | 3120 | 3560;3560;3560 |
| RTX 4090D CUDA | sc205 | S | 0.881959 | 1.373476 | 0.642136 | RTX 4090D | 15680 | 13320;13320;13320 |
| RTX 4090D CUDA | sc50b | S | 0.058011 | 0.139734 | 0.415153 | RTX 4090D | 560 | 560;560;560 |
| RTX 4090D CUDA | scagr25 | M | 1.24601 | 1.545581 | 0.806176 | RTX 4090D | 19400 | 14800;14800;14800 |
| RTX 4090D CUDA | scagr7 | S | 0.433425 | 0.423053 | 1.02452 | W7900 | 5400 | 3400;3400;3400 |
| RTX 4090D CUDA | scfxm1 | M | 0.586958 | 1.144653 | 0.512782 | RTX 4090D | 7520 | 10920;10920;10920 |
| RTX 4090D CUDA | scfxm2 | M | 1.527 | 1.312772 | 1.16319 | W7900 | 23920 | 12000;12000;12000 |
| RTX 4090D CUDA | scfxm3 | M | 1.45537 | 1.57367 | 0.924825 | RTX 4090D | 20600 | 13120;13120;13120 |
| RTX 4090D CUDA | sctap1 | M | 0.130891 | 0.247539 | 0.528769 | RTX 4090D | 1560 | 1560;1560;1560 |
| RTX 4090D CUDA | sctap2 | M | 0.096884 | 0.194312 | 0.4986 | RTX 4090D | 960 | 920;920;920 |
| RTX 4090D CUDA | ship04s | M | 0.355447 | 0.712118 | 0.499141 | RTX 4090D | 4320 | 5440;5440;5440 |
| RTX 4090D CUDA | ship08s | M | 0.346102 | 0.68956 | 0.501917 | RTX 4090D | 4160 | 5240;5240;5240 |
| RTX 4090D CUDA | stair | M | 2.03344 | 5.640418 | 0.360512 | RTX 4090D | 28520 | 56080;56080;56080 |
| Radeon 890M ROCm | 25fv47 | L | 0.435295 | 1.205027 | 0.361233 | Radeon 890M | 6160 | 9680;9680;9680 |
| Radeon 890M ROCm | 80bau3b | L | 0.887086 | 1.023789 | 0.866473 | Radeon 890M | 10280 | 7800;7800;7800 |
| Radeon 890M ROCm | afiro | S | 0.055775 | 0.106813 | 0.522174 | Radeon 890M | 200 | 200;200;200 |
| Radeon 890M ROCm | degen2 | M | 0.11105 | 0.22799 | 0.487083 | Radeon 890M | 1560 | 1360;1360;1360 |
| Radeon 890M ROCm | degen3 | L | 0.622692 | 0.801251 | 0.77715 | Radeon 890M | 7680 | 6000;6000;6000 |
| Radeon 890M ROCm | fit1d | M | 0.251398 | 0.521367 | 0.48219 | Radeon 890M | 3080 | 3520;3520;3520 |
| Radeon 890M ROCm | fit2d | L | 1.18779 | 1.493279 | 0.795424 | Radeon 890M | 5040 | 5040;5040;5040 |
| Radeon 890M ROCm | greenbeb | L | 152.025 | 61.144834 | 2.48631 | W7900 | 1814520 | 502640;502640;502640 |
| Radeon 890M ROCm | israel | M | 0.153273 | 0.348547 | 0.439748 | Radeon 890M | 2480 | 2480;2480;2480 |
| Radeon 890M ROCm | lotfi | S | 3.58774 | 8.437827 | 0.425197 | Radeon 890M | 85840 | 85840;85840;85840 |
| Radeon 890M ROCm | maros-r7 | L | 0.116644 | 0.152325 | 0.765757 | Radeon 890M | 560 | 560;560;560 |
| Radeon 890M ROCm | pilot4 | M | 97.1357 | 110.295226 | 0.880688 | Radeon 890M | 2222240 | 1119160;1119160;1119160 |
| Radeon 890M ROCm | pilot87 | L | 7.91001 | 10.432215 | 0.758229 | Radeon 890M | 81960 | 82240;82240;82240 |
| Radeon 890M ROCm | recipe | S | 0.07604 | 0.159525 | 0.476665 | Radeon 890M | 720 | 720;720;720 |
| Radeon 890M ROCm | sc105 | S | 0.183978 | 0.433761 | 0.424146 | Radeon 890M | 3560 | 3560;3560;3560 |
| Radeon 890M ROCm | sc205 | S | 0.576624 | 1.373476 | 0.419828 | Radeon 890M | 13320 | 13320;13320;13320 |
| Radeon 890M ROCm | sc50b | S | 0.066212 | 0.139734 | 0.473843 | Radeon 890M | 560 | 560;560;560 |
| Radeon 890M ROCm | scagr25 | M | 0.679735 | 1.545581 | 0.439793 | Radeon 890M | 14800 | 14800;14800;14800 |
| Radeon 890M ROCm | scagr7 | S | 0.180376 | 0.423053 | 0.426367 | Radeon 890M | 3400 | 3400;3400;3400 |
| Radeon 890M ROCm | scfxm1 | M | 0.507364 | 1.144653 | 0.443247 | Radeon 890M | 10920 | 10920;10920;10920 |
| Radeon 890M ROCm | scfxm2 | M | 0.535406 | 1.312772 | 0.407844 | Radeon 890M | 11040 | 12000;12000;12000 |
| Radeon 890M ROCm | scfxm3 | M | 1.42719 | 1.57367 | 0.906918 | Radeon 890M | 24400 | 13120;13120;13120 |
| Radeon 890M ROCm | sctap1 | M | 0.112531 | 0.247539 | 0.454599 | Radeon 890M | 1560 | 1560;1560;1560 |
| Radeon 890M ROCm | sctap2 | M | 0.096109 | 0.194312 | 0.494612 | Radeon 890M | 880 | 920;920;920 |
| Radeon 890M ROCm | ship04s | M | 0.3257 | 0.712118 | 0.457368 | Radeon 890M | 5440 | 5440;5440;5440 |
| Radeon 890M ROCm | ship08s | M | 0.253043 | 0.68956 | 0.366963 | Radeon 890M | 3600 | 5240;5240;5240 |
| Radeon 890M ROCm | stair | M | 2.39416 | 5.640418 | 0.424465 | Radeon 890M | 56080 | 56080;56080;56080 |
