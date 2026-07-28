# W7900 决赛冲刺运行手册（v2）

本手册固化 fresh-machine 恢复、百度网盘 large-MPS 下载、正式基线、精度敏感性、资源采样、targeted profiling、throughput 后处理、断点恢复、归档与发布流程。

## 1. 冻结边界

- 求解器源码基线：`735764807d8698ff30811d1a6fcc45d4a3fd4817`。
- harness 和文档可以形成新提交，但 `CMakeLists.txt`、`cmake/`、`cupdlp/`、`interface/` 必须保持与冻结基线一致。
- 主结果使用 non-hard23；hard3 仅作已有困难实例诊断，不在本轮 W7900 默认下载范围内。
- 8 卡结果只表示 8 个独立 MPS 作业并发吞吐，不表示一个 LP 的分布式多 GPU 求解。
- 本轮不做新算法、大规模核心重写、混合精度或真正单问题多 GPU。

## 2. v2 文件

```text
scripts/prepare_w7900_final_sprint.sh
scripts/download_w7900_large_mps.sh
scripts/run_w7900_final_sprint.sh
scripts/publish_w7900_final_sprint.sh
docs/W7900_FINAL_SPRINT_RUNBOOK.zh-CN.md
```

## 3. Runner 标准入口

```text
status
mini
pilot
all
baseline23
precision
profile
throughput
archive
resume
```

便利别名：

```text
session1 -> baseline23
session2 -> precision + profile
```

## 4. 下载范围

```text
metadata
mini
pilot
nonhard23
precision5
profile5
hard3
all26
```

- `mini`：仅 `qap15.mps`，约 3.35 MB，用于最小真实数据全链测试。
- `pilot`：`set-cover-model.mps`、`square41.mps`。
- `nonhard23`：正式主结果 23 例。
- `precision5` / `profile5`：`L2CTA3D`、`set-cover-model`、`thk_48`、`square41`、`tpl-tub-ws1617`。
- `hard3`：`dlr1`、`Dual2_5000`、`fhnw-binschedule1`，默认不下载。
- `all26`：完整集合，只作备用。

所有下载逐文件做 SHA256；已验证文件自动跳过，中断后重新执行同一 scope 即可。

## 5. 首次安装后最小真实测试

### 5.1 静态检查

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

chmod +x \
  scripts/prepare_w7900_final_sprint.sh \
  scripts/download_w7900_large_mps.sh \
  scripts/run_w7900_final_sprint.sh \
  scripts/publish_w7900_final_sprint.sh

bash -n scripts/prepare_w7900_final_sprint.sh
bash -n scripts/download_w7900_large_mps.sh
bash -n scripts/run_w7900_final_sprint.sh
bash -n scripts/publish_w7900_final_sprint.sh
```

### 5.2 下载最小真实 case

```bash
bash scripts/download_w7900_large_mps.sh mini
```

成功标准：

```text
scope=mini
total=1
verified=1
failed=0
```

### 5.3 全链运行

```bash
WINDOW_MINUTES=20 \
RESERVE_MINUTES=5 \
BASELINE_REPEATS=1 \
PRECISION_REPEATS=1 \
bash scripts/run_w7900_final_sprint.sh mini
```

mini 会完成：

1. `qap15 @ 1e-4` 基线；
2. `qap15 @ 1e-3 / 1e-4 / 1e-5`；
3. `qap15` 的 `rocprofv3 --runtime-trace`；
4. wall/solver/iteration/termination/residual/gap；
5. VRAM、GPU/memory utilization、功耗、温度、时钟原始采样；
6. `commands.tsv`、`run_manifest.json`、解析 CSV；
7. throughput CSV；
8. tar.gz 与 SHA256。

成功标准：

- 4 条 `qap15` solver 记录均为 `DONE + OPTIMAL`；
- 三档精度均存在；
- profile exit code 为 0；
- archive 和 `.sha256` 已生成。

## 6. 测试通过后提交与推送

先为 fresh machine 配置临时 SSH：

```bash
INSTALL_APT_PACKAGES=0 \
RUN_BUILD=0 \
RUN_SMOKE=0 \
SETUP_GITHUB_SSH=1 \
bash scripts/bootstrap_w7900_workspace.sh
```

将打印出的公钥添加到 GitHub 后，执行：

```bash
bash scripts/publish_w7900_final_sprint.sh
```

发布脚本会拒绝：

- 求解器源码变化；
- 五个白名单文件以外的工作树变化；
- mini 没有完成；
- 三档精度不完整；
- profile 失败；
- archive/SHA256 缺失。

它只提交并推送五个 harness/文档文件，不会添加 Cookie、MPS、build、raw trace 或结果包。

## 7. Fresh machine 恢复

克隆后：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
bash scripts/prepare_w7900_final_sprint.sh setup
bash scripts/download_w7900_large_mps.sh login
```

建议两个终端并行。

终端 A 下载：

```bash
bash scripts/download_w7900_large_mps.sh nonhard23
```

终端 B build/smoke：

```bash
bash scripts/prepare_w7900_final_sprint.sh build
bash scripts/prepare_w7900_final_sprint.sh smoke
```

## 8. 四小时窗口一：non-hard23 两轮

```bash
WINDOW_MINUTES=165 \
RESERVE_MINUTES=35 \
BASELINE_REPEATS=2 \
bash scripts/run_w7900_final_sprint.sh baseline23
```

v2 固定使用 repeat-major 顺序：

```text
repeat 1：完整 23 例
repeat 2：完整 23 例
repeat 3：仅时间允许时显式设置
```

不会再采用“每个 case 连跑两次再进入下一个 case”的顺序。

历史单轮 wall 合计约 49 分钟；正式资源采样后按 55–65 分钟预算。进入保留时间后停止启动新 solver，并自动解析、打包和生成 SHA256。

## 9. 四小时窗口二：精度与 profiling

只下载五个代表实例：

```bash
bash scripts/download_w7900_large_mps.sh precision5
```

精度实验：

```bash
WINDOW_MINUTES=165 \
RESERVE_MINUTES=35 \
PRECISION_REPEATS=2 \
PRECISION_LEVELS="1e-3 1e-4 1e-5" \
bash scripts/run_w7900_final_sprint.sh precision
```

顺序固定为：

```text
repeat 1：五例 @ 1e-3 -> 五例 @ 1e-4 -> 五例 @ 1e-5
repeat 2：重复完整矩阵
```

然后在同一 `RUN_ROOT` 或新 run 中执行 profiling：

```bash
WINDOW_MINUTES=90 \
RESERVE_MINUTES=30 \
bash scripts/run_w7900_final_sprint.sh profile
```

也可以一次执行：

```bash
WINDOW_MINUTES=165 \
RESERVE_MINUTES=35 \
PRECISION_REPEATS=2 \
bash scripts/run_w7900_final_sprint.sh session2
```

但严格精度大量超时时，分开执行更安全。

## 10. Resume

记录 runner 输出的 `run_root`。中断后：

```bash
RUN_ROOT=/app/cupdlp_w7900/results/final_sprint/<run-id> \
WINDOW_MINUTES=120 \
RESERVE_MINUTES=35 \
bash scripts/run_w7900_final_sprint.sh resume
```

也可显式指定：

```bash
RUN_ROOT=/app/cupdlp_w7900/results/final_sprint/<run-id> \
bash scripts/run_w7900_final_sprint.sh resume baseline23
```

- `DONE + JSON` 自动跳过；
- `TIMEOUT` 默认视为有效结果并跳过；
- 设置 `RERUN_TIMEOUTS=1` 才重跑 timeout；
- `ERROR` 会重新尝试。

## 11. Throughput

`baseline23` 和 `all` 归档时会自动生成：

```text
05_throughput/single_card_throughput.csv
```

包括：

- completed cases；
- wall time sum；
- solve time sum；
- cases/hour；
- solve-seconds per elapsed hour。

已有 8 卡 fast8 只作为历史证据复制到：

```text
05_throughput/legacy_8card_fast8/
```

其中明确写明独立任务吞吐边界。v2 不自动重跑 8 卡，避免挤占核心实验窗口。

## 12. 归档

正常运行结束自动生成：

```text
/app/cupdlp_w7900/results/<run-id>.tar.gz
/app/cupdlp_w7900/results/<run-id>.tar.gz.sha256
```

手动重新解析/归档：

```bash
RUN_ROOT=/app/cupdlp_w7900/results/final_sprint/<run-id> \
bash scripts/run_w7900_final_sprint.sh archive
```

接收端必须重新计算 SHA256。没有成功导出并校验的数据，不算完成。

## 13. Git 禁止项

不得提交：

```text
Cookie 或 BaiduPCS 配置
SSH 私钥
*.mps
build 目录
raw profiler trace
大型资源日志
结果 tar.gz
```

只提交：

```text
harness scripts
runbook
curated CSV
manifest
case list
compact profiling summary
小型图表
```
