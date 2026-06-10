from pathlib import Path


def update_file(path, edits):
    p = Path(path)
    text = p.read_text()

    for old, new in edits:
        if new in text:
            print(f"[skip] {path}: already has update")
            continue
        if old not in text:
            raise SystemExit(f"[error] {path}: text not found:\n{old}")
        text = text.replace(old, new, 1)
        print(f"[ok] {path}: updated one item")

    p.write_text(text)


update_file("README.md", [
    (
        "| Planned larger AMD target | AMD Radeon PRO W7900 / `gfx1100` |",
        "| Additional ROCm target under validation | AMD Radeon PRO W7900 / `gfx1100` |",
    ),
    (
        "The ROCm/HIP backend has passed smoke validation and a cross-device Netlib benchmark matrix on AMD Radeon 890M / `gfx1150`.",
        "The ROCm/HIP backend has passed smoke validation and a cross-device Netlib benchmark matrix on AMD Radeon 890M / `gfx1150`. The W7900 / `gfx1100` branch has passed first-port CPU-vs-ROCm `afiro` smoke validation and is now in extended validation and tuning.",
    ),
    (
        "| [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | Original upstream README backup |",
        "| [`docs/W7900_FIRST_PORT.md`](docs/W7900_FIRST_PORT.md) | [`docs/W7900_FIRST_PORT.zh-CN.md`](docs/W7900_FIRST_PORT.zh-CN.md) | W7900 / `gfx1100` first-port build and smoke validation record | | [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | Original upstream README backup |",
    ),
    (
        "- Large MPS benchmark workflow based on H100-hosted cases, inventory files, and SHA256 manifests.",
        "- W7900 / `gfx1100` first-port build scripts and smoke validation notes. - Large MPS benchmark workflow based on H100-hosted cases, inventory files, and SHA256 manifests.",
    ),
])


update_file("README.zh-CN.md", [
    (
        "| 后续更大 AMD 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
        "| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
    ),
    (
        "ROCm/HIP backend 已经在 AMD Radeon 890M / `gfx1150` 上通过 smoke validation 和跨设备 Netlib benchmark matrix。",
        "ROCm/HIP backend 已经在 AMD Radeon 890M / `gfx1150` 上通过 smoke validation 和跨设备 Netlib benchmark matrix。W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。",
    ),
    (
        "| [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | 上游原始 README 备份 |",
        "| [`docs/W7900_FIRST_PORT.md`](docs/W7900_FIRST_PORT.md) | [`docs/W7900_FIRST_PORT.zh-CN.md`](docs/W7900_FIRST_PORT.zh-CN.md) | W7900 / `gfx1100` first-port 构建和 smoke validation 记录 | | [`README_UPSTREAM.md`](README_UPSTREAM.md) | - | 上游原始 README 备份 |",
    ),
    (
        "- 基于 H100 来源 case、inventory 和 SHA256 manifest 的 large MPS benchmark workflow。",
        "- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。 - 基于 H100 来源 case、inventory 和 SHA256 manifest 的 large MPS benchmark workflow。",
    ),
])

print("[done] README W7900 status updated")
