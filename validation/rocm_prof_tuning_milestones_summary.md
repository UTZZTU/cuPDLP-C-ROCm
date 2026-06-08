# ROCm rocprofv3 tuning milestone trace summary

Run dir: `/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/rocprof_tuning_milestones_20260608_205749`

Trace mode: `rocprofv3 --runtime-trace --output-format csv`.

Milestone order:

- `pre_tuning`
- `remove_sync`
- `cache_attrs`
- `fused_average`
- `reduce_scalar_copies`
- `current`

The percentage columns use `(current / reference - 1) * 100`.

## `lotfi`

| milestone | status | nIter | solve s | solve Δ% prev | solve Δ% pre | matvec s | HIP calls | HIP time ms | kernel dispatches | kernel time ms | memcpy count | memcpy time ms | memalloc count | memalloc time ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | OPTIMAL | 85840 | 8.223583 |  | 0.000 | 0.669345 | 1996484 | 6515.748 | 1218718 | 2057.070 | 0 | 0.000 | 95 | 4.331 |
| `remove_sync` | OPTIMAL | 85840 | 7.198186 | -12.469 | -12.469 | 0.631637 | 1910087 | 5662.380 | 1218718 | 1977.850 | 0 | 0.000 | 95 | 5.167 |
| `cache_attrs` | OPTIMAL | 85840 | 7.063279 | -1.874 | -14.109 | 0.647592 | 1611724 | 5676.082 | 1218718 | 1956.161 | 0 | 0.000 | 95 | 4.061 |
| `fused_average` | OPTIMAL | 85840 | 6.490873 | -8.104 | -21.070 | 0.593820 | 1354204 | 5348.784 | 1132878 | 1809.215 | 0 | 0.000 | 95 | 4.097 |
| `reduce_scalar_copies` | OPTIMAL | 85840 | 6.197615 | -4.518 | -24.636 | 0.615925 | 1267807 | 5083.985 | 1046481 | 1695.235 | 0 | 0.000 | 95 | 7.880 |
| `current` | OPTIMAL | 85840 | 6.247886 | 0.811 | -24.025 | 0.622912 | 1267807 | 5132.296 | 1046481 | 1707.998 | 0 | 0.000 | 95 | 10.673 |

## `pilot87`

| milestone | status | nIter | solve s | solve Δ% prev | solve Δ% pre | matvec s | HIP calls | HIP time ms | kernel dispatches | kernel time ms | memcpy count | memcpy time ms | memalloc count | memalloc time ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | OPTIMAL | 81960 | 11.409471 |  | 0.000 | 0.642537 | 2185559 | 9493.764 | 1426619 | 5024.325 | 13 | 0.173 | 95 | 4.369 |
| `remove_sync` | OPTIMAL | 81960 | 10.382973 | -8.997 | -8.997 | 0.604242 | 2103171 | 8676.847 | 1426619 | 4960.781 | 13 | 0.133 | 95 | 4.551 |
| `cache_attrs` | OPTIMAL | 81960 | 10.372410 | -0.102 | -9.089 | 0.598264 | 1818571 | 8793.960 | 1426619 | 4952.330 | 13 | 0.246 | 95 | 4.352 |
| `fused_average` | OPTIMAL | 81960 | 9.861996 | -4.921 | -13.563 | 0.569638 | 1572691 | 8517.270 | 1344659 | 4815.554 | 13 | 0.178 | 95 | 4.458 |
| `reduce_scalar_copies` | OPTIMAL | 81960 | 9.708346 | -1.558 | -14.910 | 0.575513 | 1490303 | 8357.069 | 1262271 | 4777.123 | 13 | 0.183 | 95 | 7.649 |
| `current` | OPTIMAL | 81960 | 9.407482 | -3.099 | -17.547 | 0.567742 | 1490303 | 8104.049 | 1262271 | 4629.568 | 13 | 0.129 | 95 | 4.396 |

## `scfxm1`

| milestone | status | nIter | solve s | solve Δ% prev | solve Δ% pre | matvec s | HIP calls | HIP time ms | kernel dispatches | kernel time ms | memcpy count | memcpy time ms | memalloc count | memalloc time ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `pre_tuning` | OPTIMAL | 10920 | 1.084953 |  | 0.000 | 0.102785 | 256319 | 922.222 | 156167 | 263.927 | 2 | 0.027 | 95 | 4.245 |
| `remove_sync` | OPTIMAL | 10920 | 0.966914 | -10.880 | -10.880 | 0.097886 | 245387 | 819.601 | 156167 | 258.893 | 2 | 0.029 | 95 | 4.205 |
| `cache_attrs` | OPTIMAL | 10920 | 0.955351 | -1.196 | -11.945 | 0.105545 | 207273 | 830.082 | 156167 | 255.263 | 2 | 0.014 | 95 | 7.028 |
| `fused_average` | OPTIMAL | 10920 | 0.936831 | -1.939 | -13.652 | 0.107788 | 174513 | 823.154 | 145247 | 250.803 | 2 | 0.023 | 95 | 9.630 |
| `reduce_scalar_copies` | OPTIMAL | 10920 | 0.919185 | -1.884 | -15.279 | 0.110574 | 163581 | 801.814 | 134315 | 245.635 | 2 | 0.019 | 95 | 7.216 |
| `current` | OPTIMAL | 10920 | 0.826017 | -10.136 | -23.866 | 0.095681 | 163581 | 732.687 | 134315 | 219.761 | 2 | 0.009 | 95 | 4.175 |

## Interpretation checklist

- `remove_sync`: check whether HIP API time or synchronization-like API count/time drops.
- `cache_attrs`: check whether HIP API calls around device attributes drop, especially on short cases.
- `fused_average`: check whether kernel dispatch count changes and whether vector-update kernels change in `trace_kernel_top.csv`.
- `reduce_scalar_copies`: check whether memory copy count/time or HIP API time drops.
- `current`: check whether engineering compatibility changes preserve similar trace structure.
