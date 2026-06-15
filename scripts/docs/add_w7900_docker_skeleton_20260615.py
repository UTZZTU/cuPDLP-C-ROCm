from pathlib import Path

Path("docker").mkdir(exist_ok=True)
Path("scripts/docs").mkdir(parents=True, exist_ok=True)

dockerfile = """# W7900 ROCm/HIP environment skeleton
#
# This Dockerfile is a final-submission environment declaration skeleton.
# It is not the source of the committed W7900 performance numbers.
# Current W7900 results were produced on the contest-provided environment
# with a pre-installed ROCm/Python SDK layout.
#
# Raw MPS data and raw profiler traces must stay outside the image.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \\
    ca-certificates \\
    git \\
    cmake \\
    ninja-build \\
    build-essential \\
    python3 \\
    python3-pip \\
    pkg-config \\
    curl \\
    time \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/cuPDLP-C-ROCm

# Copying the repository is intended for source-level reproducibility.
# ROCm installation is environment-specific and should follow the
# contest-provided W7900 documentation or AMD ROCm installation guide.
COPY . /workspace/cuPDLP-C-ROCm

CMD ["bash"]
"""

readme_en = """# W7900 Docker / container skeleton

> 中文: [README_DOCKER_W7900.zh-CN.md](README_DOCKER_W7900.zh-CN.md)

This directory contains a lightweight container skeleton for final-submission environment documentation.

## Scope

The current W7900 benchmark and validation numbers were produced on the contest-provided W7900 environment, which uses a pre-installed ROCm/Python SDK layout. Therefore, this Dockerfile is not claimed as the source of the committed W7900 performance numbers.

Its purpose is to document the expected build environment shape and to make final packaging easier.

## What is included

- Ubuntu 24.04 base image.
- Generic build tools: CMake, Ninja, GCC/G++, Python, Git.
- Repository source copy.

## What is intentionally not included

- Raw `.mps` benchmark data.
- Raw profiler trace directories.
- Contest-provided ROCm/Python SDK binaries.
- Large benchmark outputs.

## Current reproduction path

Use the repository reproducibility guide first:

```text
docs/REPRODUCIBILITY.md
```

For W7900, the primary path is still the documented bootstrap workflow on the contest-provided machine:

```bash
bash scripts/bootstrap_w7900_workspace.sh
```

## Future work

Before final submission, this skeleton can be extended into a stricter Docker/Containerfile if the final ROCm runtime layout is fixed and redistributable.
"""

readme_zh = """# W7900 Docker / container 骨架

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
"""

Path("docker/Dockerfile.w7900").write_text(dockerfile)
Path("docker/README_DOCKER_W7900.md").write_text(readme_en)
Path("docker/README_DOCKER_W7900.zh-CN.md").write_text(readme_zh)

print("wrote docker/Dockerfile.w7900")
print("wrote docker/README_DOCKER_W7900.md")
print("wrote docker/README_DOCKER_W7900.zh-CN.md")
