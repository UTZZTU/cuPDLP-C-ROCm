#!/usr/bin/env python3
from pathlib import Path

doc = Path("docs/VALIDATION.md")
if not doc.exists():
    raise SystemExit(f"missing {doc}")

text = doc.read_text(encoding="utf-8")
heading = "## Medium Netlib validation"

section = """
## Medium Netlib validation

The smoke suite is intentionally small. For broader coverage, use the medium
Netlib validation set.

Prepare the additional Netlib MPS files:

```bash
./scripts/prepare_medium_netlib_cases.sh
```

Run medium validation:

```bash
RESULT_ROOT=validation/results/medium_netlib \\
  ./scripts/run_validation.sh validation/cases_medium_netlib.txt

grep -R "Overall result" validation/results/medium_netlib/*/*_compare.md
```

The medium set uses higher iteration limits than the smoke suite. If a case
hits `nIterLim`, treat the result as `INCOMPLETE` first and inspect both CPU and
ROCm logs before treating it as a correctness failure.

Medium validation results are generated artifacts and should not be committed.
"""

if heading in text:
    print("skip: medium validation section already exists")
    raise SystemExit(0)

marker = "## Validation levels\n"
if marker in text:
    text = text.replace(marker, section.strip() + "\n\n" + marker, 1)
else:
    text = text.rstrip() + "\n\n" + section.strip() + "\n"

doc.write_text(text, encoding="utf-8")
print(f"updated {doc}")
