# 最终视频演示指南

> 最终结果：[W7900_FINAL_RESULTS_20260729.zh-CN.md](W7900_FINAL_RESULTS_20260729.zh-CN.md)
> 竞赛入口：[COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md)

本指南用于项目最终演示视频。W7900 正式实验已经完成，视频不再申请临时
W7900，也不为了录屏重跑长实验。视频以以下内容为准：

1. 真实项目结构和迁移代码；
2. 4090/普通主机上的 compact evidence inspection；
3. 已提交的正式 W7900 数据和精确图表；
4. 已保存的真实 W7900 运行画面或日志；
5. 清楚说明哪些是硬件实测、哪些是离线证据检查。

视频时长、分辨率、格式和文件大小以提交时最新官方要求为准。仓库不长期固化
可能变化的赛事数字。

## 推荐三分钟结构

| 时间 | 内容 | 画面 |
|---|---|---|
| 0:00–0:20 | 问题与目标 | 项目标题、CUDA-to-ROCm 挑战 |
| 0:20–0:55 | 架构与贡献 | CPU/CUDA/ROCm 后端、验证链 |
| 0:55–1:25 | 工程演示 | 仓库结构、构建脚本、compact evidence 检查 |
| 1:25–2:20 | 正式结果 | 76/76、工作负载画像、精度—时间—显存 |
| 2:20–2:45 | Profiling 与安全调优 | P10、P11、P12、P14-A1 |
| 2:45–3:00 | 边界与总结 | 不夸大多 GPU、算法创新和适用范围 |

## 录制前准备

在 4090 主机更新最终仓库后：

```bash
cd /data/cuPDLP-C-ROCm
git branch --show-current
git rev-parse HEAD
git status --short

python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

画面中可以展示：

```text
FINAL_W7900_RELEASE_DATA_PASS
FINAL_REPOSITORY_RELEASE_PASS
```

这表示已提交 compact evidence 通过检查，不表示 4090 重新测量了 W7900。

## 建议展示的仓库路径

```text
README.md
docs/W7900_FINAL_RESULTS_20260729.zh-CN.md
docs/CUDA_TO_ROCM_MIGRATION_CASE_STUDY.zh-CN.md
docs/W7900_PERFORMANCE_BEHAVIOR.zh-CN.md
docs/ROCM_PROFILING_NOTES.zh-CN.md
validation/final_w7900_20260729/
docs/assets/w7900/final20260729/
scripts/analysis/generate_final_w7900_release.py
```

## 正式结果画面

推荐依次展示：

1. `baseline_total_time.zh-CN.svg`
   - 解释 23 例耗时长尾；
   - 强调前三例贡献约 82.22%。
2. `baseline_repeatability.zh-CN.svg`
   - 总时间 CV 中位数约 0.377%；
   - 22/23 低于 2%。
3. `workload_profile.zh-CN.svg`
   - 区分迭代/计算主导和读取/初始化主导。
4. `precision_cost.zh-CN.svg`
   - 收紧目标精度的成本具有实例依赖性。
5. `precision_resource_tradeoff.zh-CN.svg`
   - 同一实例跨精度显存较稳定，时间变化更明显。
6. `precision_quality.zh-CN.svg`
   - 30/30 实际误差不高于目标精度。

## 建议口播数字

```text
正式 W7900 solver 运行：76/76 验证通过
nonhard23：23 例双重复，共 46 条
精度实验：5 例、3 档、双重复，共 30 条
targeted profile：5/5 通过
单卡顺序吞吐均值：约 28.0616 cases/hour
基线前三例总时间占比：约 82.22%
目标精度从 1e-3 收紧到 1e-5：
总时间成本约 1.01× 到 4.01×
```

## Profiling 与调优叙事

用一条完整证据链讲清楚：

```text
P10 profiling
→ 定位 CSR SpMV、copy、launch
→ P11 接受 CSR_ALG1 默认
→ P12 因迭代轨迹变化拒绝 patch
→ P14-A1 重复验证 current 收益
→ 最终 session2 5/5 trace 完整性 PASS
```

不要只讲“更快”，要强调性能修改必须同时保护数值行为。

## 真实运行画面

优先使用此前已经保存的真实 W7900：

- build/smoke 终端；
- `gfx1100` 设备识别；
- solver 输出；
- profile trace 生成；
- archive 和 SHA 校验。

若没有可用素材，可以展示仓库中的正式 manifest、日志摘要、QC JSON 和 compact
CSV，但必须口播：

> 这里展示的是已提交 W7900 证据的离线检查，不是当前主机重新运行 W7900。

不要伪造 W7900 终端，也不要把 4090 输出剪辑成 W7900。

## 必须保留的边界

- 项目贡献是迁移、验证和证据驱动调优，不是新 PDLP 算法；
- 吞吐是单卡顺序独立 MPS；
- 8 卡 fast8 是八个独立任务；
- precision 结论只覆盖五例；
- static correlation 是探索性；
- hard3 单独报告；
- Docker 是环境骨架；
- W7900 aggregate 不应被包装成在所有 case 上超过 CUDA。

## 画面规范

- 使用简体中文；
- 图表标题不加“图 1/图 2”；
- 不使用“墙钟时间”，统一写“总时间”；
- 字体、字号和数字口径与论文/PPT一致；
- 不使用图片生成模型重新绘制数据点；
- 数据图直接使用仓库提交的 SVG/PNG；
- 代码和终端字体足够大；
- 不展示 Cookie、token、SSH key、用户名隐私或本地绝对凭据路径。

## 最后检查

- [ ] 视频数字来自最终结果页；
- [ ] 没有引用六月单轮 2960.171 s 作为当前主结果；
- [ ] 76/76、46/46、30/30、5/5 口径一致；
- [ ] 吞吐语义正确；
- [ ] W7900 实测与离线检查画面明确区分；
- [ ] 图表使用最终 CSV 驱动版本；
- [ ] 仓库链接和 commit 可访问。
