#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
readme = ROOT / "README.md"

s = readme.read_text(encoding="utf-8")

start = "## Final W7900 validation endpoint after P14-A1 / 2026-06-18"
end = "## P14-A1 后的最终补充验证 / 2026-06-18"

if start not in s:
    print("[SKIP] English P14-A1 block not found in README.md")
else:
    pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
    new_s, n = re.subn(pattern, "", s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"[ERR] expected to remove one English block, removed {n}")
    readme.write_text(new_s.rstrip() + "\n", encoding="utf-8", newline="\n")
    print("[OK] removed English P14-A1 block from Chinese README.md")

# Guardrails: English README should not contain the Chinese final P14-A1 heading.
en = ROOT / "README.en.md"
en_s = en.read_text(encoding="utf-8")
bad_zh = "## P14-A1 后的最终补充验证 / 2026-06-18"
if bad_zh in en_s:
    raise SystemExit("[ERR] README.en.md contains Chinese P14-A1 heading; inspect manually")
print("[OK] README.en.md does not contain Chinese P14-A1 heading")
