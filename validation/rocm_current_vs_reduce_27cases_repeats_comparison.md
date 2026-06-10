# ROCm current vs reduce-scalar-copies repeated comparison

> 中文: [rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md](rocm_current_vs_reduce_27cases_repeats_comparison.zh-CN.md)  
> Validation index: [README.md](README.md)  
> Raw CSVs: [comparison](rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](rocm_current_vs_reduce_27cases_repeats_raw.csv)

Run directory:

```text
/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/current_vs_reduce_27cases_repeats_20260607_230730
```

Baseline:

```text
reduce_scalar_copies = b44c7ab
current = repository HEAD at run time
```

Primary metric:

```text
median solve time across repeated runs
```

Geometric mean speedup of baseline over current:

```text
0.9995092331107024
```

This means the current repository state was essentially performance-neutral relative to `reduce_scalar_copies` on this repeated 27-case validation run.

Cases where current was slower than baseline by more than 2%:

```text
afiro
sc50b
recipe
scfxm1
```

For full per-case medians, coefficient-of-variation values, matvec timing, and slowdown percentages, use the linked CSV files above.
