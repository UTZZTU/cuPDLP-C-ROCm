# 可复现性指南

> English: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
> 最终完整指南：[FINAL_REPRODUCTION_GUIDE.zh-CN.md](FINAL_REPRODUCTION_GUIDE.zh-CN.md)

本页给出项目复现层级和推荐入口。最终发布的详细命令、正式矩阵、故障处理与
验收标准统一维护在
[最终复现指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md)。

## 复现层级

| 层级 | 工作 | 硬件 |
|---|---|---|
| Compact evidence 检查 | CSV/JSON、身份、QC、图表、文档链接 | 任意 Linux |
| 离线分析复现 | 重算统计与重画最终图 | 普通 Linux + Python |
| CPU build/smoke | 构建 CPU 路径与单例运行 | C/C++ build 环境 |
| W7900 build/smoke | 真实 ROCm/HIP 构建与最小验证 | W7900 / `gfx1100` |
| 完整正式矩阵 | baseline23、session2、资源、profile、archive | W7900 与外部 MPS |

非 W7900 主机上的检查有效，但不能描述为新的 W7900 性能测量。

## 当前正式身份

```text
branch=rocm-w7900-gfx1100
solver=735764807d8698ff30811d1a6fcc45d4a3fd4817
harness=b5b9a6ffc1a041a48a0e051568d0134a3822556c
```

## 推荐的无硬件检查

```bash
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

## 推荐的图表复现

```bash
python3 -m pip install pandas numpy matplotlib
python3 scripts/analysis/generate_final_w7900_release.py
```

## W7900 最小检查

```bash
bash scripts/prepare_w7900_final_sprint.sh setup
bash scripts/prepare_w7900_final_sprint.sh build
bash scripts/prepare_w7900_final_sprint.sh smoke
```

## 完整正式重跑

- mini gate；
- `baseline23`：23 × 2 = 46；
- `session2`：5 × 3 × 2 = 30，外加 5 profiles；
- archive、SHA256 和接收端校验。

命令、成功标志和 troubleshooting 见
[最终复现指南](FINAL_REPRODUCTION_GUIDE.zh-CN.md)。

## 数据策略

允许提交：源码、脚本、case list、manifest、compact CSV/JSON、Markdown、
小型 SVG/PNG。
禁止提交：raw MPS、raw profiler traces、本地 builds、Cookie、SSH key、
token。

## 解释边界

- 8 卡 fast8 是独立任务吞吐；
- hard3 单独报告；
- precision 只覆盖五例；
- static correlation 不代表因果；
- Docker 是环境骨架。
