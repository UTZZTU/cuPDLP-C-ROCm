from pathlib import Path

def replace_section_to_eof(path, heading, new_tail):
    p = Path(path)
    s = p.read_text()
    if new_tail.strip() in s:
        print(f"{path}: already updated")
        return
    idx = s.find(heading)
    if idx < 0:
        raise SystemExit(f"{path}: heading not found: {heading}")
    p.write_text(s[:idx] + new_tail)
    print(f"{path}: updated")

def replace_phrase(path, old, new):
    p = Path(path)
    s = p.read_text()
    if new in s:
        print(f"{path}: already updated")
        return
    if old not in s:
        raise SystemExit(f"{path}: phrase not found: {old}")
    p.write_text(s.replace(old, new, 1))
    print(f"{path}: updated")

new_en_tail = """## 11. Docker / container status

A dedicated Docker/Containerfile is not the primary reproduction path because the available W7900 environment uses a pre-installed ROCm/Python SDK layout. The current reproducible path is the documented bootstrap workflow.

This repository now provides a lightweight Docker/container skeleton:

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
docker/README_DOCKER_W7900.zh-CN.md
```

The skeleton documents the expected build-environment shape and final-submission packaging direction. It is not claimed as the source of the committed W7900 performance numbers. Raw MPS data and raw profiler traces stay outside the image.
"""

new_zh_tail = """## 11. Docker / container 状态

dedicated Docker/Containerfile 不是当前主复现路径，因为 W7900 环境使用预安装 ROCm/Python SDK 布局。当前可复现路径是 bootstrap workflow。

本仓库现在提供轻量 Docker/container skeleton：

```text
docker/Dockerfile.w7900
docker/README_DOCKER_W7900.md
docker/README_DOCKER_W7900.zh-CN.md
```

该骨架用于说明预期 build environment 形态和 final-submission 打包方向。它不声称是当前已提交 W7900 性能数字的来源。raw MPS 数据和 raw profiler traces 不进入镜像。
"""

replace_section_to_eof(
    "docs/REPRODUCIBILITY.md",
    "## 11. Docker / container status",
    new_en_tail,
)

replace_section_to_eof(
    "docs/REPRODUCIBILITY.zh-CN.md",
    "## 11. Docker / container 状态",
    new_zh_tail,
)

replace_phrase(
    "docs/COMPETITION_SCORECARD.md",
    "Dedicated Docker/Containerfile remains a final-submission work item",
    "Lightweight Docker/container skeleton is present; strict final image remains future packaging work",
)

replace_phrase(
    "docs/COMPETITION_SCORECARD.zh-CN.md",
    "Dedicated Docker/Containerfile 仍是 final-submission work item",
    "已提供轻量 Docker/container skeleton；严格 final image 仍属于最终打包工作",
)

print("done")
