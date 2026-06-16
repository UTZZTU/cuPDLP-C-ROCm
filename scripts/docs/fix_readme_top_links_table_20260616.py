#!/usr/bin/env python3
from pathlib import Path

def replace_block(path, old_lines, new_block):
    p = Path(path)
    text = p.read_text()
    old = "\n".join(old_lines)
    if old not in text:
        raise SystemExit(f"anchor block not found in {path}")
    text = text.replace(old, new_block.strip(), 1)
    p.write_text(text)
    print(f"updated {path}")

zh_old = [
    "> English homepage: [README.en.md](README.en.md)",
    "> ROCm/gfx1150 快速入口: [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md)",
    "> 文档地图: [docs/README.md](docs/README.md)",
    "> 验证数据索引: [validation/README.zh-CN.md](validation/README.zh-CN.md)",
    "> Benchmark 索引: [docs/benchmarks/README.md](docs/benchmarks/README.md)",
]

zh_new = """
| 入口 | 链接 |
|---|---|
| English homepage | [README.en.md](README.en.md) |
| ROCm/gfx1150 快速入口 | [README_ROCM_gfx1150.zh-CN.md](README_ROCM_gfx1150.zh-CN.md) |
| 文档地图 | [docs/README.md](docs/README.md) |
| 验证数据索引 | [validation/README.zh-CN.md](validation/README.zh-CN.md) |
| Benchmark 索引 | [docs/benchmarks/README.md](docs/benchmarks/README.md) |
"""

en_old = [
    "> 中文主页: [README.md](README.md)",
    "> ROCm/gfx1150 quick start: [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md)",
    "> Documentation map: [docs/README.md](docs/README.md)",
    "> Validation index: [validation/README.md](validation/README.md)",
    "> Benchmark index: [docs/benchmarks/README.md](docs/benchmarks/README.md)",
]

en_new = """
| Entry | Link |
|---|---|
| Chinese homepage | [README.md](README.md) |
| ROCm/gfx1150 quick start | [README_ROCM_gfx1150.md](README_ROCM_gfx1150.md) |
| Documentation map | [docs/README.md](docs/README.md) |
| Validation index | [validation/README.md](validation/README.md) |
| Benchmark index | [docs/benchmarks/README.md](docs/benchmarks/README.md) |
"""

replace_block("README.md", zh_old, zh_new)
replace_block("README.zh-CN.md", zh_old, zh_new)
replace_block("README.en.md", en_old, en_new)
