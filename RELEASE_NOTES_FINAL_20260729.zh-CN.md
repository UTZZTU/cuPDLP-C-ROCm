# 最终仓库发布说明（2026-07-29）

> English: [RELEASE_NOTES_FINAL_20260729.md](RELEASE_NOTES_FINAL_20260729.md)

本次更新是 cuPDLP-C-ROCm 项目的最后一次 W7900 结果、文档和复现体系收口。

## 正式身份

```text
branch=rocm-w7900-gfx1100
frozen_solver=735764807d8698ff30811d1a6fcc45d4a3fd4817
formal_harness=b5b9a6ffc1a041a48a0e051568d0134a3822556c
Window1=d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a
Window2=7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db
```

## 新增

- 最终 W7900 中英文结果页；
- 最终中英文复现指南；
- 46 条 baseline、30 条 precision、5 条 profile 的 compact evidence；
- 23 例静态结构与探索性关联表；
- CSV 精确驱动的中英文 PNG/SVG；
- 最终数据与图表生成脚本；
- Markdown 内部链接检查；
- 仓库最终发布验证脚本。

## 更新

- 中英文主页；
- 文档地图；
- W7900 当前状态；
- 性能行为与工作负载解释；
- profiling 说明；
- validation 索引和语义；
- 竞赛入口、评分对照、提交清单；
- 视频演示指南；
- final-sprint runbook 状态。

## 历史保留

- 日期化 validation 报告不改写；
- P10、P11、P12、P14-A1 证据链保留；
- hard3 保持单独；
- fast8 保持独立任务吞吐语义。

## 防止回退

三个可能覆盖当前文档的六月历史生成脚本被改为只读 no-op，避免误执行后把
主页、竞赛入口或复现指南恢复成旧状态。

## 未修改

本次更新不修改冻结 solver 路径：

```text
CMakeLists.txt
cmake/
cupdlp/
interface/
```

也不提交 raw MPS、raw profiler traces、build、Cookie、SSH key 或 token。
