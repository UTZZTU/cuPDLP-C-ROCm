#!/usr/bin/env python3
from pathlib import Path
import re

SKIP_DIRS = {
    ".git",
    "build-cpu",
    "build-rocm-w7900",
    "build-rocm-plc",
    "build-rocm-w7900-ae3b683",
    "third-party",
    "results",
}

def should_skip(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)

def is_table_sep(line: str) -> bool:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return False
    body = s.strip("|").replace(":", "").replace("-", "").replace("|", "").strip()
    return body == ""

def is_table_line(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]

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

    for i, line in enumerate(lines, 1):
        s = line.rstrip("\n")

        if len(s) > 900:
            issues.append((str(p), i, "LONG_LINE", f"{len(s)} chars"))

        # Multiple markdown headings accidentally collapsed into one line.
        if re.search(r"\S\s+##\s+", s) or re.search(r"\S\s+#\s+", s):
            issues.append((str(p), i, "HEADING_NOT_ON_OWN_LINE", s[:180]))

        # Multiple tables collapsed into a single physical line.
        if s.count("|---") >= 2 or s.count("| |---") >= 1:
            issues.append((str(p), i, "POSSIBLE_COLLAPSED_TABLE", s[:180]))

        # Code fence and shell commands collapsed onto one line.
        if "```" in s and s.count("```") >= 2 and len(s) > 120:
            issues.append((str(p), i, "POSSIBLE_COLLAPSED_CODE_BLOCK", s[:180]))

        # Consecutive blockquote navigation lines without table/list formatting.
        if s.startswith("> ") and i < len(lines):
            nxt = lines[i].strip() if i < len(lines) else ""
            if nxt.startswith("> ") and ("[" in s and "](" in s or ":" in s):
                issues.append((str(p), i, "CONSECUTIVE_BLOCKQUOTE_NAV", s[:180]))

        # Table header without separator next line.
        if is_table_line(s) and i < len(lines):
            nxt = lines[i].strip()
            if not is_table_sep(nxt):
                # Avoid flagging normal table body rows after a valid separator.
                prev = lines[i - 2].strip() if i >= 2 else ""
                if not is_table_sep(prev):
                    issues.append((str(p), i, "TABLE_LINE_WITHOUT_SEPARATOR_CONTEXT", s[:180]))

if not issues:
    print("[OK] no markdown format issues detected")
else:
    for path, line, kind, msg in issues:
        loc = f"{path}:{line}" if line else path
        print(f"[{kind}] {loc}: {msg}")
    raise SystemExit(1)
