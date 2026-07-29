# cuPDLP-C-ROCm 最终复现指南

> English: [FINAL_REPRODUCTION_GUIDE.md](FINAL_REPRODUCTION_GUIDE.md)
> 正式结果：[W7900_FINAL_RESULTS_20260729.zh-CN.md](W7900_FINAL_RESULTS_20260729.zh-CN.md)

本指南是项目最终发布后的唯一推荐复现路径。它区分：

1. 无 W7900 时检查已提交证据；
2. 普通主机重新生成分析与图；
3. 有 W7900 时做最小 build/smoke；
4. 需要时重跑完整正式矩阵。

当前发布已经完成 W7900 正式实验，不要求评审者或普通用户重新占用 W7900。

## 1. 固定身份

```text
branch: rocm-w7900-gfx1100
frozen solver source: 735764807d8698ff30811d1a6fcc45d4a3fd4817
formal harness: b5b9a6ffc1a041a48a0e051568d0134a3822556c
Window 1 SHA256: d2ce13091072a7c40c2c89bdd988e94c2fca36772da38e0af87de6332e7cd94a
Window 2 SHA256: 7f8fbcd45591f4dbe0899d18df76329b1f9a17ff433b6dcd3c06d743aaead0db
```

两个提交的角色不同：

- `735764807d8698ff30811d1a6fcc45d4a3fd4817`：冻结求解器源码；
- `b5b9a6ffc1a041a48a0e051568d0134a3822556c`：增加实验、资源采样、profiling、归档和验收，不改变
  `CMakeLists.txt`、`cmake/`、`cupdlp/`、`interface/`。

## 2. 克隆与检查最终发布

```bash
git clone --recurse-submodules   --branch rocm-w7900-gfx1100   https://github.com/UTZZTU/cuPDLP-C-ROCm.git
cd cuPDLP-C-ROCm

git branch --show-current
git rev-parse HEAD
git status --short
```

静态验证：

```bash
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```

预期：

```text
FINAL_W7900_RELEASE_DATA_PASS
FINAL_REPOSITORY_RELEASE_PASS
```

这一步检查：

- 23 个 baseline case、46 条正式基线记录；
- 5 × 3 × 2 = 30 条 precision 记录；
- 5/5 profile；
- 正式 branch、solver、harness 和 archive SHA；
- compact 数据结构与关键数值；
- Markdown 相对链接；
- Python/Bash 语法；
- 没有求解器源码变化。

## 3. 在普通主机重画最终图

依赖：

```bash
python3 -m pip install pandas numpy matplotlib
```

运行：

```bash
python3 scripts/analysis/generate_final_w7900_release.py
```

输出默认写入：

```text
docs/assets/w7900/final20260729/
validation/final_w7900_20260729/generated_summary.json
validation/final_w7900_20260729/static_performance_spearman_regenerated.csv
```

图和数据只来自提交的 compact CSV，不访问原始 MPS，也不伪装成新的 W7900
测量。

## 4. 最小 CPU 复现

```bash
cmake -S . -B build-cpu -G Ninja   -DCMAKE_BUILD_TYPE=Release   -DBUILD_CUDA=OFF   -DBUILD_ROCM=OFF
cmake --build build-cpu -j"$(nproc)"

./build-cpu/bin/plc   -fname ./example/afiro.mps   -out /tmp/afiro_cpu.json   -nIterLim 200
```

## 5. W7900 最小 build/smoke

要求：

- Radeon PRO W7900 / `gfx1100`；
- 匹配的 ROCm/HIP SDK；
- `hipcc`、`rocm_agent_enumerator`、`rocm-smi`；
- HiGHS 1.6.0；
- Ninja、CMake、C/C++ 编译器。

在项目历史云环境中，默认工作区是：

```text
/app/cupdlp_w7900
```

运行：

```bash
bash scripts/prepare_w7900_final_sprint.sh setup
bash scripts/prepare_w7900_final_sprint.sh build
bash scripts/prepare_w7900_final_sprint.sh smoke
```

或在已恢复的环境中：

```bash
bash scripts/build_w7900_cpu.sh
bash scripts/build_w7900_rocm.sh
bash scripts/run_w7900_smoke.sh
```

## 6. 数据集

原始 large-MPS 不进入 Git。正式运行前必须：

1. 获取与 manifest 对应的 MPS；
2. 逐文件做 SHA256；
3. 只运行验证通过的输入。

下载脚本支持：

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

最小下载：

```bash
bash scripts/download_w7900_large_mps.sh login
bash scripts/download_w7900_large_mps.sh mini
bash scripts/download_w7900_large_mps.sh verify mini
```

注意：`BaiduPCS-Go who` 返回 exit code 0 不代表已登录。`uid: 0` 必须视为
未登录。

## 7. 正式 mini gate

任何完整正式重跑前先执行：

```bash
ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=5 BASELINE_REPEATS=1 PRECISION_REPEATS=1 bash scripts/run_w7900_final_sprint.sh mini
```

成功标准：

```text
4 条 qap15 solver 记录均 DONE
OPTIMAL + FEASIBLE + FEASIBLE
solver_validation_status=PASS
profile_validation_status=PASS
非空 kernel trace
archive 和 SHA256 存在
run_validation_summary.json 无结构性错误
```

## 8. 正式 Window 1：baseline23

```bash
bash scripts/download_w7900_large_mps.sh nonhard23

ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=35 BASELINE_REPEATS=2 bash scripts/run_w7900_final_sprint.sh baseline23
```

完整成功标准：

```text
46/46 solver rows
23 cases × 2 repeats
all VALIDATED_OPTIMAL
no timeout
no error
every solver row has resource samples
dataset SHA PASS
internal manifest PASS
matrix complete
archive + SHA256
```

## 9. 正式 Window 2：目标精度与 profiling

```bash
bash scripts/download_w7900_large_mps.sh precision5

ACCESS_DEADLINE="YYYY-MM-DD HH:MM:SS" RESERVE_MINUTES=35 PRECISION_REPEATS=2 PRECISION_LEVELS="1e-3 1e-4 1e-5" bash scripts/run_w7900_final_sprint.sh session2
```

完整成功标准：

```text
30/30 precision solver rows
5 cases × 3 tolerances × 2 repeats
5/5 profiles
all solver rows validated
all profiles PASS
trace_csv_count > 0
kernel_trace_count > 0
archive + SHA256
```

## 10. 归档和跨主机校验

W7900 输出：

```text
<run-id>.tar.gz
<run-id>.tar.gz.sha256
```

sidecar 可能包含 W7900 上的绝对路径。复制到其他主机后，优先比较第一列
digest：

```bash
EXPECTED="$(awk 'NF {print $1; exit}' archive.tar.gz.sha256)"
ACTUAL="$(sha256sum archive.tar.gz | awk '{print $1}')"
test "$EXPECTED" = "$ACTUAL"
```

不要因为 sidecar 中的旧绝对路径找不到文件而误判 archive 损坏。

## 11. Resume 与截止时间

- 真实截止时间使用 `ACCESS_DEADLINE`；
- 重新启动脚本不能获得新的四小时；
- 剩余 30–40 分钟应停止启动新 solver，优先归档和传输；
- 中断后使用原 `RUN_ROOT` 执行 `resume`；
- wrapper 失败后先检查 run root 和 archive，不能盲目从头重跑。

## 12. 常见故障

### GitHub 访问不稳定

不同入口可能状态不同：

- `github.com`
- `raw.githubusercontent.com`
- `codeload.github.com`
- Git protocol / `git ls-remote`

不要用一次 GitHub 首页 `curl` 作为唯一硬门禁。依赖 tarball 可直接使用
codeload，并设置有限重试。

### HiGHS 下载

GitHub archive 重定向目标可能不支持 `curl -C -`。断点续传返回 curl 33 时，
删除残包并从字节 0 完整下载，再用 `tar -tzf` 验证。

### `--single-branch` clone

单分支 clone 可能没有 `origin/rocm-w7900-gfx1100`。应使用显式 refspec：

```bash
git fetch origin   +refs/heads/rocm-w7900-gfx1100:refs/remotes/origin/rocm-w7900-gfx1100
```

### Profile

- baseline23 没有 kernel trace 是正常的；
- session2/profile 没有 kernel trace 是失败；
- 失败重跑前清理旧 trace，避免把旧文件当成新证据。

### 凭据

Cookie、SSH key、token 不写入脚本、日志、archive 或 Git。

## 13. 证据解释边界

- nonhard23 与 hard3 分开；
- 单卡吞吐是顺序独立 MPS；
- fast8 是八个独立作业；
- precision 结论只覆盖五例；
- static correlation 不代表因果；
- raw profiler trace 不提交；
- 非 W7900 主机上的数据检查不能写成 fresh W7900 性能复现。

## 14. 发布前检查

```bash
git diff --check
python3 scripts/docs/check_markdown_links.py
python3 scripts/analysis/generate_final_w7900_release.py --check-only
bash scripts/verify_final_repository_release.sh
```
