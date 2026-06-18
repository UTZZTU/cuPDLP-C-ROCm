# W7900 视频演示指南

本文件用于准备比赛演示视频。比赛视频要求：

* 分辨率不小于 `1920x1080`
* 文件大小不超过 `100MB`
* 时长不超过 `5 分钟`
* 格式为 `avi`、`mp4`、`wmv` 之一
* 内容应包括：作品原理及创新点、结构介绍、功能演示三部分

建议使用 OBS 录制，推荐录制格式为 `mp4`，画面分辨率为 `1920x1080`，帧率为 `30 FPS`，视频码率建议控制在 `2200 Kbps` 左右，音频码率建议 `96 Kbps` 或 `128 Kbps`。视频总时长建议控制在 `4 分 30 秒` 左右，避免超过 100MB。

## 1. 视频整体结构

建议视频按以下顺序录制：

| 时间        | 内容        | 画面                                                       |
| --------- | --------- | -------------------------------------------------------- |
| 0:00-0:25 | 项目背景与目标   | GitHub 主页、项目 README                                      |
| 0:25-1:35 | 作品原理及创新点  | 架构图、ROCm/HIP 迁移说明、W7900 当前状态                             |
| 1:35-2:25 | 项目结构介绍    | `cupdlp/hip`、`scripts`、`validation`、`docs`、`docs/assets` |
| 2:25-4:10 | 功能演示      | 从恢复环境到构建 `plc`，运行一个简单 MPS 样例并查看结果                        |
| 4:10-4:50 | 实验结果展示与总结 | 展示 W7900 图表、P11/P14/P5 结果和结论                             |

视频重点不要放在长时间 benchmark，而应展示完整工程链路：

1. 能恢复环境；
2. 能从 GitHub 或 bundle 恢复仓库；
3. 能构建 ROCm/HIP 版本 `plc`；
4. 能运行一个简单 MPS 样例；
5. 能查看输出结果；
6. 能展示已提交的 W7900 profiling、调优和多卡吞吐图表。

## 2. OBS 推荐设置

OBS 推荐设置：

| 项目                       | 建议                      |
| ------------------------ | ----------------------- |
| Base Canvas Resolution   | `1920x1080`             |
| Output Scaled Resolution | `1920x1080`             |
| FPS                      | `30`                    |
| Recording Format         | `mp4`                   |
| Encoder                  | H.264 / x264 / 硬件 H.264 |
| Rate Control             | CBR                     |
| Video Bitrate            | `2200 Kbps`             |
| Audio Bitrate            | `96 Kbps` 或 `128 Kbps`  |
| 录制时长                     | 建议 `4 分 30 秒` 以内        |

录制前建议先录 30 秒测试文件大小。如果 30 秒文件明显超过 10MB，应降低视频码率；如果终端文字不清楚，优先放大终端字体，而不是提高码率。

## 3. 录制前准备

W7900 机器的工作目录约定为：

```bash
/app/cupdlp_w7900
```

仓库目录为：

```bash
/app/cupdlp_w7900/src/cuPDLP-C-ROCm
```

当前分支为：

```bash
rocm-w7900-gfx1100
```

目标演示命令只使用短命令，不运行大 MPS benchmark，避免视频等待时间过长。

## 4. W7900 新机器恢复：修 DNS / 网络

如果 W7900 新机器无法访问 GitHub 或百度，先修 DNS：

```bash
cd /app

cp /etc/resolv.conf /etc/resolv.conf.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

cat > /etc/resolv.conf <<'EOF'
nameserver 223.5.5.5
nameserver 119.29.29.29
options timeout:2 attempts:2
EOF

getent hosts github.com || true
curl -I --connect-timeout 10 https://github.com || true
curl -I --connect-timeout 10 https://www.baidu.com || true
```

如果 GitHub 能访问，继续从 GitHub clone。
如果 GitHub 仍然不稳定，则使用 890M 上生成的 bundle 恢复仓库。

## 5. 从 GitHub 恢复仓库

在 W7900 上执行：

```bash
mkdir -p /app/cupdlp_w7900/src /app/cupdlp_w7900/logs /app/cupdlp_w7900/results

cd /app/cupdlp_w7900/src

rm -rf cuPDLP-C-ROCm

GIT_TERMINAL_PROMPT=0 git clone \
  --branch rocm-w7900-gfx1100 \
  https://github.com/UTZZTU/cuPDLP-C-ROCm.git \
  cuPDLP-C-ROCm

cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

git log --oneline --decorate -8
git status --short
```

如果 GitHub clone 失败，则使用下一节的 bundle 方案。

## 6. 从 890M 生成 bundle 并上传到 W7900

如果 W7900 无法稳定访问 GitHub，可以在 890M 上生成最新 bundle。

890M 上的最新 W7900 仓库路径为：

```bash
/home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/cuPDLP-C-ROCm-w7900
```

在 890M 上执行：

```bash
cd /home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/cuPDLP-C-ROCm-w7900

git switch rocm-w7900-gfx1100
git pull --ff-only origin rocm-w7900-gfx1100

git log --oneline --decorate -8
git status --short

mkdir -p "$HOME/下载"

COMMIT="$(git rev-parse --short HEAD)"
BUNDLE="$HOME/下载/cupdlp_w7900_rocm-w7900-gfx1100_${COMMIT}_$(date +%Y%m%d_%H%M%S).bundle"

git bundle create "$BUNDLE" HEAD rocm-w7900-gfx1100

git bundle verify "$BUNDLE"
git bundle list-heads "$BUNDLE"

ls -lh "$BUNDLE"
echo "$BUNDLE"
```

然后把生成的 bundle 文件上传到 W7900 的 `/app/` 目录。

在 W7900 上用 bundle 恢复：

```bash
mkdir -p /app/cupdlp_w7900/src /app/cupdlp_w7900/logs /app/cupdlp_w7900/results

cd /app/cupdlp_w7900/src

rm -rf cuPDLP-C-ROCm

git clone /app/cupdlp_w7900_rocm-w7900-gfx1100_*.bundle cuPDLP-C-ROCm

cd cuPDLP-C-ROCm

git switch rocm-w7900-gfx1100 || true

git log --oneline --decorate -8
git status --short
```

如果看到：

```text
warning: remote HEAD refers to nonexistent ref, unable to checkout
```

不用慌，继续执行：

```bash
git switch rocm-w7900-gfx1100
```

即可。

## 7. 恢复 W7900 环境

进入仓库后执行：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm

INSTALL_APT_PACKAGES=0 RUN_BUILD=0 RUN_SMOKE=0 \
bash scripts/bootstrap_w7900_workspace.sh \
  2>&1 | tee /app/cupdlp_w7900/logs/bootstrap_video_demo_$(date +%Y%m%d_%H%M%S).log
```

激活环境：

```bash
source /app/cupdlp_w7900/activate_w7900.sh

echo "HIGHS_HOME=$HIGHS_HOME"
"$HIGHS_HOME/bin/highs" --version || true

hipcc --version | head -20
rocm_agent_enumerator
rocm-smi
```

视频里可以展示 `rocm_agent_enumerator` 输出 8 个 `gfx1100`，证明 W7900 多卡环境被识别。

## 8. 构建 `plc`

先检查是否已有可执行文件：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
source /app/cupdlp_w7900/activate_w7900.sh

find . -maxdepth 3 -type f -name plc -print
```

如果没有 `./build-rocm-w7900/bin/plc`，则重新构建：

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
source /app/cupdlp_w7900/activate_w7900.sh

bash scripts/build_w7900_cpu.sh \
  2>&1 | tee /app/cupdlp_w7900/logs/build_w7900_cpu_video_demo_$(date +%Y%m%d_%H%M%S).log

bash scripts/build_w7900_rocm.sh \
  2>&1 | tee /app/cupdlp_w7900/logs/build_w7900_rocm_video_demo_$(date +%Y%m%d_%H%M%S).log

find . -maxdepth 3 -type f -name plc -print
```

演示时不一定要完整录下所有编译过程。如果编译时间较长，可以录制构建命令开始、构建完成和 `plc` 文件存在即可。

## 9. 运行一个简单样例

推荐使用仓库自带的 `example/afiro.mps`，不要在视频里跑 large MPS。

```bash
cd /app/cupdlp_w7900/src/cuPDLP-C-ROCm
source /app/cupdlp_w7900/activate_w7900.sh

mkdir -p /app/cupdlp_w7900/results/video_demo

./build-rocm-w7900/bin/plc \
  -fname ./example/afiro.mps \
  -out /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.json \
  -nIterLim 100000 \
  -dTimeLim 60 \
  2>&1 | tee /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.log
```

这个命令用于证明 ROCm/HIP 版 `plc` 能读取 MPS 文件并完成求解流程。

## 10. 查看样例结果

运行结束后查看输出文件：

```bash
ls -lh /app/cupdlp_w7900/results/video_demo

echo "===== log tail ====="
tail -80 /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.log

echo "===== json head ====="
head -80 /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.json
```

如果要快速查找状态字段，可执行：

```bash
grep -niE "termination|optimal|iter|time|gap|primal|dual" \
  /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.log \
  /app/cupdlp_w7900/results/video_demo/afiro_rocm_demo.json \
  | head -80
```

视频里重点展示：

1. `plc` 成功运行；
2. 输出了 `.json`；
3. log 中出现 solver timing、iteration、termination 等信息；
4. 结果文件可追溯。

## 11. 展示已有实验图表

运行样例之后，不需要再跑长实验。直接打开 GitHub 页面展示已提交图表：

```text
validation/w7900_latest_experiment_figures_20260616.zh-CN.md
docs/W7900_CURRENT_STATUS.zh-CN.md
validation/w7900_8card_batch_fast8_summary_20260616.zh-CN.md
validation/w7900_p14a1_quick6_repeat_summary_20260618.zh-CN.md
```

重点讲：

* 8-card fast8：8 个独立 MPS 任务，单 GPU 顺序 `558s`，8 卡并发 `146s`，约 `3.82x` batch makespan speedup；
* before/current fast-core6：用于分析调优前后表现；
* rocprof starter3：展示 profiling 和 kernel 热点；
* P11/P14-A1：展示 W7900 SpMV tuning 与 repeated validation。

## 12. 视频讲解建议话术

可以按下面方式讲：

```text
本作品基于上游 cuPDLP-C 线性规划求解器，完成了面向 AMD ROCm/HIP 平台的迁移、验证和调优。项目保留 CPU 与上游兼容路径，同时新增 AMD Radeon 平台的 ROCm/HIP 后端。当前分支重点验证了 Radeon 890M/gfx1150 和 W7900/gfx1100 平台。

在结构上，cupdlp/hip 保存 HIP 后端代码，scripts 保存构建、恢复、实验和分析脚本，validation 保存 compact CSV 和 Markdown 实验摘要，docs 和 docs/assets 保存说明文档和图表。仓库通过 README、validation index 和 W7900 current status 页面组织证据链。

功能演示中，首先恢复 W7900 环境并识别 8 张 gfx1100 GPU，然后构建 ROCm/HIP 版本 plc，最后运行 example/afiro.mps 这一简单 MPS 样例，生成 JSON 和 log 输出，证明求解流程可运行、可复现。

实验方面，项目已经完成 rocprof profiling、hard case 诊断、before/current 对比、SpMV tuning 和 8 卡批处理吞吐验证。其中 8 个独立 MPS 任务在单 GPU 顺序运行时需要 558 秒，而在 8 张 W7900 上并发运行只需要 146 秒，体现了多卡节点在批量独立优化任务上的工程价值。
```

## 13. 视频录制注意事项

录制时建议：

* 终端字体调大；
* 浏览器页面缩放到 `125%` 或 `150%`；
* 不展示账号 cookies、SSH 私钥、token；
* 不展示百度网盘 cookies；
* 不现场跑 large MPS；
* 不录制长时间编译等待；
* 录制前先试录 30 秒；
* 最终文件检查分辨率、时长、大小。

检查视频文件大小和时长可用：

```bash
ls -lh your_video.mp4
```

如果安装了 `ffprobe`，可进一步检查：

```bash
ffprobe -hide_banner your_video.mp4
```

## 14. 890M 上提交本文档到 GitHub

如果本文档是在 890M 上创建的，使用以下命令提交：

```bash
cd /home/bjut316/rocm_dir/pdlp/cuPDLP-C-ROCm/cuPDLP-C-ROCm-w7900

git switch rocm-w7900-gfx1100
git pull --ff-only origin rocm-w7900-gfx1100

python3 scripts/docs/scan_markdown_format_issues_20260616.py
git diff --check
git status --short
git diff --stat

git add docs/VIDEO_DEMO_GUIDE.zh-CN.md

git commit -m "docs: add Chinese video demo guide"

git push origin rocm-w7900-gfx1100

git log --oneline --decorate -6
git status --short
```

如果后续需要英文版，可再创建：

```text
docs/VIDEO_DEMO_GUIDE.md
```

但比赛视频准备阶段，中文版即可。
