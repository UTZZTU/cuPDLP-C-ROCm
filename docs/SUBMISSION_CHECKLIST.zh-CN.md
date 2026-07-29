# 最终提交清单

> English: [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md)

## 仓库内材料

| 条目 | 状态 | 入口 |
|---|---|---|
| 中英文主页 | 已更新 | [中文](../README.md)、[English](../README.en.md) |
| 文档地图 | 已更新 | [docs/README.md](README.md) |
| 最终正式结果 | 已完成 | [结果页](W7900_FINAL_RESULTS_20260729.zh-CN.md) |
| W7900 当前状态 | 已更新 | [状态](W7900_CURRENT_STATUS.zh-CN.md) |
| 最终复现指南 | 已完成 | [指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md) |
| 验证语义 | 已补最终合同 | [验证](VALIDATION.zh-CN.md) |
| 性能与工作负载 | 已更新 | [分析](W7900_PERFORMANCE_BEHAVIOR.zh-CN.md) |
| Profiling | 已更新 | [记录](ROCM_PROFILING_NOTES.zh-CN.md) |
| Validation 索引 | 已更新 | [索引](../validation/README.zh-CN.md) |
| Final compact evidence | 已完成 | [目录](../validation/final_w7900_20260729/README.zh-CN.md) |
| 最终 PNG/SVG | 已生成 | [图目录](assets/w7900/final20260729/) |
| 分析与验证脚本 | 已添加 | `scripts/analysis/`、`scripts/docs/` |
| Release notes | 已添加 | [最终发布说明](../RELEASE_NOTES_FINAL_20260729.md) |

## 最终证据闭环

- [x] 正式分支：`rocm-w7900-gfx1100`
- [x] 冻结 solver：`735764807d8698ff30811d1a6fcc45d4a3fd4817`
- [x] 正式 harness：`b5b9a6ffc1a041a48a0e051568d0134a3822556c`
- [x] Window 1：46/46
- [x] Window 2 precision：30/30
- [x] Window 2 profile：5/5
- [x] 数据集和包内 SHA PASS
- [x] 每条 solver 记录有资源采样
- [x] 最终分析发布
- [x] raw MPS、raw trace、凭据不进入 Git

## 仓库外材料人工核对

- [ ] 技术论文使用最终数字和最终图；
- [ ] PPT 不混用六月单轮数字和七月正式双重复数字；
- [ ] 展架的吞吐明确为单卡顺序独立 MPS；
- [ ] 视频区分真实 W7900 运行和离线 evidence inspection；
- [ ] 答辩不把 8 卡 fast8 写成单个 LP 分布式求解；
- [ ] 所有材料只把 precision 结论限定到五例；
- [ ] 静态相关使用“探索性关联”，不写成因果；
- [ ] 引用的仓库路径和 commit 可访问。

## 推送前命令

```bash
git diff --check
python3 scripts/docs/check_markdown_links.py
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```
