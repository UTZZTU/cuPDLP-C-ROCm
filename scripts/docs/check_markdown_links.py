#!/usr/bin/env python3
"""Check repository-internal Markdown links.

External URLs, mailto links, and same-page anchors are ignored. Image links are
checked. Optional anchors after a valid local path are ignored.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(
    r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)"
)
SKIP_PARTS = {".git", "build", "build-cpu", "build-rocm-plc",
              "build-rocm-w7900", "node_modules", ".venv", "venv"}

bad = []
checked = 0

for source in ROOT.rglob("*.md"):
    if any(part in SKIP_PARTS for part in source.parts):
        continue
    text = source.read_text(encoding="utf-8", errors="replace")
    for match in LINK_RE.finditer(text):
        raw = next(value for value in match.groups() if value)
        raw = raw.strip()
        if not raw:
            continue
        # Markdown titles after the path: <path> "title" or path "title".
        if raw.startswith("<") and ">" in raw:
            raw = raw[1:raw.index(">")]
        else:
            raw = raw.split()[0]
        raw = raw.strip("<>")
        if raw.startswith(("http://", "https://", "mailto:", "#", "data:")):
            continue
        target_text = unquote(raw.split("#", 1)[0])
        if not target_text:
            continue
        checked += 1
        target = (source.parent / target_text).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            bad.append((source.relative_to(ROOT), raw, "escapes repository"))
            continue
        if not target.exists():
            bad.append((source.relative_to(ROOT), raw, "missing"))

if bad:
    for source, target, reason in bad:
        print(f"{source}: {target} [{reason}]")
    raise SystemExit(f"MARKDOWN_LINK_CHECK_FAIL count={len(bad)}")

print(f"checked_links={checked}")
print("MARKDOWN_LINK_CHECK_PASS")
