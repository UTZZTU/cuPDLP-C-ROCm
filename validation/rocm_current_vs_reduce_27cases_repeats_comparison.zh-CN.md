# ROCm current vs reduce-scalar-copies 重复测试对比

> English: [rocm_current_vs_reduce_27cases_repeats_comparison.md](rocm_current_vs_reduce_27cases_repeats_comparison.md)  
> Validation 索引: [README.zh-CN.md](README.zh-CN.md)  
> 原始 CSV: [comparison](rocm_current_vs_reduce_27cases_repeats_comparison.csv), [aggregated](rocm_current_vs_reduce_27cases_repeats_aggregated.csv), [raw](rocm_current_vs_reduce_27cases_repeats_raw.csv)

运行目录：

```text
/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/validation/results/current_vs_reduce_27cases_repeats_20260607_230730
```

对比基线：

```text
reduce_scalar_copies = b44c7ab
current = 运行时仓库 HEAD
```

主指标：

```text
重复运行的 median solve time
```

baseline 相对 current 的几何平均 speedup：

```text
0.9995092331107024
```

这表示在这组 27-case 重复测试上，当前仓库状态相对 `reduce_scalar_copies` 基本是性能中性的。

current 相对 baseline 变慢超过 2% 的 case：

```text
afiro
sc50b
recipe
scfxm1
```

完整逐 case median、CV、matvec 时间和 slowdown 百分比请查看上方链接的 CSV 文件。
