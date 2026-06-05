#!/usr/bin/env python3
from pathlib import Path

doc = Path("docs/ROCM_WORKFLOW.md")
content_path = Path("tools/migration/rocm_workflow_guide.md")

if not content_path.exists():
    raise SystemExit(f"missing {content_path}")

content = content_path.read_text(encoding="utf-8")
doc.write_text(content, encoding="utf-8")
print(f"updated {doc}")

readme = Path("README.md")
if readme.exists():
    text = readme.read_text(encoding="utf-8")
    link_line = "- [ROCm workflow guide](docs/ROCM_WORKFLOW.md) - common build, validation, profiling, and troubleshooting commands.\n"

    if "docs/ROCM_WORKFLOW.md" in text:
        print("README already links docs/ROCM_WORKFLOW.md")
    elif "## Documentation" in text:
        marker = "## Documentation\n"
        text = text.replace(marker, marker + "\n" + link_line, 1)
        readme.write_text(text, encoding="utf-8")
        print("updated README.md documentation section")
    elif "## What this repository provides" in text:
        marker = "## What this repository provides\n"
        text = text.replace(marker, "## Documentation\n\n" + link_line + "\n" + marker, 1)
        readme.write_text(text, encoding="utf-8")
        print("added README.md documentation section")
    else:
        text = text.rstrip() + "\n\n## Documentation\n\n" + link_line
        readme.write_text(text, encoding="utf-8")
        print("appended README.md documentation section")
