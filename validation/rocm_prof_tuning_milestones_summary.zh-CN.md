# ROCm rocprofv3 tuning milestone trace 汇总

> English: [rocm_prof_tuning_milestones_summary.md](rocm_prof_tuning_milestones_summary.md)  
> Validation 索引: [README.zh-CN.md](README.zh-CN.md)  
> 原始 CSV: [summary](rocm_prof_tuning_milestones_summary.csv), [deltas](rocm_prof_tuning_milestones_deltas.csv), [HIP API top](rocm_prof_tuning_milestones_hip_api_top.csv), [kernel top](rocm_prof_tuning_milestones_kernel_top.csv), [memory-copy top](rocm_prof_tuning_milestones_memory_copy_top.csv)

运行目录：

```text
/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/rocprof_tuning_milestones_20260608_205749
```

Trace 模式：

```text
rocprofv3 --runtime-trace --output-format csv
```

milestone 顺序：

```text
pre_tuning
remove_sync
cache_attrs
fused_average
reduce_scalar_copies
current
```

百分比列计算方式：

```text
(current / reference - 1) * 100
```

解释检查清单：

- `remove_sync`：检查 HIP API 时间或同步类 API 的次数/时间是否下降。
- `cache_attrs`：检查 device attribute 相关 HIP API 调用是否下降，尤其是短 case。
- `fused_average`：检查 kernel dispatch 数量，以及 vector-update kernel 是否变化。
- `reduce_scalar_copies`：检查 memory-copy 次数/时间或 HIP API 时间是否下降。
- `current`：检查工程兼容性修改是否保持类似 trace 结构。

完整 milestone 表格请查看上方链接的 CSV 文件。
