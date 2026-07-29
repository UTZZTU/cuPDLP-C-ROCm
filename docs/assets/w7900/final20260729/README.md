# Final W7900 Figures / W7900 最终图

All figures in this directory are generated from committed compact CSV data by:

```bash
python3 scripts/analysis/generate_final_w7900_release.py
```

每张图同时提供中文/英文、PNG/SVG。数据点不由图片生成模型重绘。

| Stem | 中文用途 | English purpose |
|---|---|---|
| `baseline_total_time` | 23 例基线总时间 | 23-case baseline total time |
| `baseline_repeatability` | 双重复稳定性 | Two-repeat stability |
| `workload_profile` | 总时间、求解占比、显存画像 | Total time, solver share, VRAM |
| `precision_cost` | 收紧目标精度的时间与迭代成本 | Time and iteration cost |
| `precision_resource_tradeoff` | 目标精度、总时间、峰值显存 | Tolerance, total time, peak VRAM |
| `precision_quality` | 实际误差与目标精度 | Achieved error versus target |
| `static_vram_association` | 静态结构与显存探索性关联 | Static structure and VRAM association |

Interpretation boundaries / 解释边界：

- throughput is sequential independent MPS;
- tolerance results cover five cases;
- sampled VRAM is not an exact instantaneous maximum;
- static association is non-causal;
- Chinese titles contain no fixed figure numbering, so figures can be reused.
