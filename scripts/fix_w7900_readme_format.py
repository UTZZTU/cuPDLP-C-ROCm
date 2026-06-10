from pathlib import Path


def fix(path):
    p = Path(path)
    s = p.read_text()

    s = s.replace(
        "record | | [`README_UPSTREAM.md`](README_UPSTREAM.md)",
        "record |\n| [`README_UPSTREAM.md`](README_UPSTREAM.md)",
    )

    s = s.replace(
        "notes. - Large MPS benchmark workflow",
        "notes.\n- Large MPS benchmark workflow",
    )

    s = s.replace(
        "记录 | | [`README_UPSTREAM.md`](README_UPSTREAM.md)",
        "记录 |\n| [`README_UPSTREAM.md`](README_UPSTREAM.md)",
    )

    s = s.replace(
        "记录。 - 基于 H100 来源 case",
        "记录。\n- 基于 H100 来源 case",
    )

    p.write_text(s)


fix("README.md")
fix("README.zh-CN.md")
print("[done] README formatting fixed")
