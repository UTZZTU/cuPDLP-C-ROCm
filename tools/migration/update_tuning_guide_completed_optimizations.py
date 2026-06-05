#!/usr/bin/env python3
from pathlib import Path

doc = Path("docs/TUNING_GUIDE_ROCM.md")
section_path = Path("tools/migration/tuning_completed_optimizations_section.md")

if not doc.exists():
    raise SystemExit(f"missing {doc}")
if not section_path.exists():
    raise SystemExit(f"missing {section_path}")

text = doc.read_text(encoding="utf-8")
section = section_path.read_text(encoding="utf-8").strip() + "\n\n"

marker = "## Future tuning work\n"
heading = "## Completed profiling-driven optimizations"

if heading in text:
    print("skip: completed optimizations section already exists")
    raise SystemExit(0)

if marker not in text:
    raise SystemExit(f"could not find insertion marker: {marker!r}")

text = text.replace(marker, section + marker, 1)
doc.write_text(text, encoding="utf-8")
print(f"updated {doc}")
