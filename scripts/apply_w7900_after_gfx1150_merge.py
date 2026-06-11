from pathlib import Path


def update(path, ops):
    p = Path(path)
    s = p.read_text()

    for desc, old, new in ops:
        if new in s:
            print(f"[skip] {path}: {desc}")
            continue
        if old not in s:
            print(f"[warn] {path}: anchor not found for {desc}")
            continue
        s = s.replace(old, new, 1)
        print(f"[ok] {path}: {desc}")

    p.write_text(s)


update("README.md", [
    (
        "target table",
        "| Planned larger AMD target | AMD Radeon PRO W7900 / `gfx1100` |",
        "| Additional ROCm target under validation | AMD Radeon PRO W7900 / `gfx1100` |",
    ),
    (
        "status sentence",
        "It is not yet a production-ready or fully tuned ROCm solver release.",
        "The W7900 / `gfx1100` branch has passed first-port CPU-vs-ROCm `afiro` smoke validation and is now in extended validation and tuning. It is not yet a production-ready or fully tuned ROCm solver release.",
    ),
    (
        "documentation row",
        "| Upstream reference snapshot | [README_UPSTREAM.md](README_UPSTREAM.md) | — |",
        "| W7900 / `gfx1100` first-port record | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |\n| Upstream reference snapshot | [README_UPSTREAM.md](README_UPSTREAM.md) | — |",
    ),
    (
        "provided bullet",
        "- Extended Netlib validation cases.",
        "- W7900 / `gfx1100` first-port build scripts and smoke validation notes. - Extended Netlib validation cases.",
    ),
])


update("README.zh-CN.md", [
    (
        "target table",
        "| 计划中的更大 AMD 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
        "| 正在验证的额外 ROCm 目标 | AMD Radeon PRO W7900 / `gfx1100` |",
    ),
    (
        "status sentence",
        "它还不是生产级、完全调优、广泛认证的 ROCm solver release。",
        "W7900 / `gfx1100` 分支已通过 first-port CPU-vs-ROCm `afiro` smoke validation，正在进入 extended validation 和 tuning 阶段。它还不是生产级、完全调优、广泛认证的 ROCm solver release。",
    ),
    (
        "documentation row",
        "| 上游参考快照 | [README_UPSTREAM.md](README_UPSTREAM.md) | — |",
        "| W7900 / `gfx1100` first-port 记录 | [docs/W7900_FIRST_PORT.md](docs/W7900_FIRST_PORT.md) | [docs/W7900_FIRST_PORT.zh-CN.md](docs/W7900_FIRST_PORT.zh-CN.md) |\n| 上游参考快照 | [README_UPSTREAM.md](README_UPSTREAM.md) | — |",
    ),
    (
        "provided bullet",
        "- 扩展 Netlib 验证 case。",
        "- W7900 / `gfx1100` first-port 构建脚本和 smoke validation 记录。 - 扩展 Netlib 验证 case。",
    ),
])

print("[done] W7900 status applied after gfx1150 merge")
