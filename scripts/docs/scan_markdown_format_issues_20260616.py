#!/usr/bin/env python3
from pathlib import Path
import re

SKIP_DIRS = {
    ".git",
    "build-cpu",
    "build-rocm-w7900",
    "build-rocm-w7900-ae3b683",
    "third-party",
    "results",
}

def should_skip(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)

def is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]

def is_table_sep(line: str) -> bool:
    s = line.strip()
    if not is_table_line(s):
        return False
    cells = [c.strip() for c in s.strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c) for c in cells)

def table_blocks(lines):
    i = 0
    while i < len(lines):
        if is_table_line(lines[i]):
            start = i
            block = []
            while i < len(lines) and is_table_line(lines[i]):
                block.append(lines[i])
                i += 1
            yield start, block
            continue
        i += 1

issues = []

for p in sorted(Path(".").rglob("*.md")):
    if should_skip(p):
        continue

    text = p.read_text(errors="replace")
    lines = text.splitlines()

    if len(lines) < 5:
        issues.append((str(p), 0, "LOW_LINE_COUNT", f"{len(lines)} lines"))

    fence_count = sum(1 for line in lines if line.strip().startswith("```"))
    if fence_count % 2 != 0:
        issues.append((str(p), 0, "ODD_CODE_FENCE_COUNT", f"{fence_count} fences"))

    inside_fence = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith("```"):
            inside_fence = not inside_fence
            continue

        if inside_fence:
            continue

        if len(line) > 1200:
            issues.append((str(p), i, "LONG_LINE", f"{len(line)} chars"))

        # A real collapsed-heading symptom: paragraph text and heading marker on one physical line.
        if re.search(r"\S\s+#{1,6}\s+\S", line):
            issues.append((str(p), i, "HEADING_NOT_ON_OWN_LINE", line[:180]))

        # A real collapsed-code symptom: multiple fences and prose on one physical line.
        if line.count("```") >= 2 and len(line) > 120:
            issues.append((str(p), i, "POSSIBLE_COLLAPSED_CODE_BLOCK", line[:180]))

        # Do not treat normal top navigation blockquotes as fatal.
        # They render acceptably and are widespread in existing project docs.
        # Root README quick links are handled separately as tables.

    for start, block in table_blocks(lines):
        if len(block) == 1:
            # A single table-looking line is only suspicious when surrounded by non-table content.
            prev = lines[start - 1].strip() if start > 0 else ""
            nxt = lines[start + 1].strip() if start + 1 < len(lines) else ""
            if not is_table_line(prev) and not is_table_line(nxt):
                issues.append((str(p), start + 1, "SINGLE_TABLE_LINE", block[0][:180]))
            continue

        if not is_table_sep(block[1]):
            issues.append((str(p), start + 1, "TABLE_BLOCK_MISSING_SEPARATOR", block[0][:180]))

        # GitHub needs a blank line before a table for reliable rendering.
        if start > 0:
            prev = lines[start - 1].strip()
            if prev and not prev.startswith("#") and not prev.startswith("<!--"):
                issues.append((str(p), start + 1, "TABLE_BLOCK_NO_BLANK_BEFORE", block[0][:180]))

if not issues:
    print("[OK] no markdown format issues detected")
else:
    for path, line, kind, msg in issues:
        loc = f"{path}:{line}" if line else path
        print(f"[{kind}] {loc}: {msg}")
    raise SystemExit(1)
