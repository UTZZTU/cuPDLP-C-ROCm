# W7900 Docker / container 骨架

> English: [README_DOCKER_W7900.md](README_DOCKER_W7900.md)

本目录提供 final submission 使用的轻量容器骨架和环境声明。

## 范围

当前 W7900 benchmark 和 validation 数字来自赛题提供的 W7900 环境，该环境使用预安装 ROCm/Python SDK 布局。因此，本 Dockerfile 不声称是当前已提交 W7900 性能数字的来源。

它的作用是说明预期 build environment 形态，并为最终打包提交做准备。

## 包含内容

- Ubuntu 24.04 base image。
- 通用构建工具：CMake、Ninja、GCC/G++、Python、Git。
- 仓库源码复制。

## 明确不包含

- 原始 `.mps` benchmark 数据。
- raw profiler trace 目录。
- 赛题环境预装的 ROCm/Python SDK 二进制。
- 大型 benchmark 输出。

## 当前复现路径

请优先使用仓库复现文档：

```text
docs/REPRODUCIBILITY.zh-CN.md
```

对于 W7900，当前主复现路径仍然是在赛题提供机器上执行 bootstrap workflow：

```bash
bash scripts/bootstrap_w7900_workspace.sh
```

## 后续工作

最终提交前，如果 ROCm runtime layout 固定且可再分发，可以把该骨架扩展为更严格的 Docker/Containerfile。
