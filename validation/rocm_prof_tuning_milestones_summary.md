# ROCm rocprofv3 tuning milestone trace summary

> 中文: [rocm_prof_tuning_milestones_summary.zh-CN.md](rocm_prof_tuning_milestones_summary.zh-CN.md)  
> Validation index: [README.md](README.md)  
> Raw CSVs: [summary](rocm_prof_tuning_milestones_summary.csv), [deltas](rocm_prof_tuning_milestones_deltas.csv), [HIP API top](rocm_prof_tuning_milestones_hip_api_top.csv), [kernel top](rocm_prof_tuning_milestones_kernel_top.csv), [memory-copy top](rocm_prof_tuning_milestones_memory_copy_top.csv)

Run directory:

```text
/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/rocprof_tuning_milestones_20260608_205749
```

Trace mode:

```text
rocprofv3 --runtime-trace --output-format csv
```

Milestone order:

```text
pre_tuning
remove_sync
cache_attrs
fused_average
reduce_scalar_copies
current
```

Percentage columns use:

```text
(current / reference - 1) * 100
```

Interpretation checklist:

- `remove_sync`: check whether HIP API time or synchronization-like API count/time drops.
- `cache_attrs`: check whether HIP API calls around device attributes drop, especially on short cases.
- `fused_average`: check whether kernel dispatch count changes and whether vector-update kernels change.
- `reduce_scalar_copies`: check whether memory-copy count/time or HIP API time drops.
- `current`: check whether engineering compatibility changes preserve similar trace structure.

The full milestone tables are in the linked CSV files.
