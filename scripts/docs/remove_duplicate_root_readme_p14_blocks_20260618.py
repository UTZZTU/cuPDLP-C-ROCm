#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

FILES = [
    (
        ROOT / "README.en.md",
        "## Final W7900 validation endpoint after P14-A1 / 2026-06-18",
        "## Final supplemental validation after P14-A1 / 2026-06-18",
    ),
    (
        ROOT / "README.zh-CN.md",
        "## P14-A1 后的 W7900 最终验证终点 / 2026-06-18",
        "## P14-A1 后的最终补充验证 / 2026-06-18",
    ),
]

def remove_block(path: Path, start: str, end: str):
    text = path.read_text(encoding="utf-8")
    if start not in text:
        print(f"[SKIP] {path.relative_to(ROOT)}: duplicate start not found")
        return
    if end not in text:
        raise SystemExit(f"[ERR] {path.relative_to(ROOT)}: end marker not found")

    pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
    new_text, n = re.subn(pattern, "", text, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"[ERR] {path.relative_to(ROOT)}: removed {n} blocks, expected 1")

    path.write_text(new_text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"[OK] removed duplicate P14 block from {path.relative_to(ROOT)}")

def main():
    for path, start, end in FILES:
        remove_block(path, start, end)

    # Guardrails
    en = (ROOT / "README.en.md").read_text(encoding="utf-8")
    zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    if "## Final W7900 validation endpoint after P14-A1 / 2026-06-18" in en:
        raise SystemExit("[ERR] README.en.md still has duplicate endpoint block")
    if "## P14-A1 后的 W7900 最终验证终点 / 2026-06-18" in zh:
        raise SystemExit("[ERR] README.zh-CN.md still has duplicate endpoint block")

    print("[DONE] duplicate root README P14 blocks removed")

if __name__ == "__main__":
    main()
