#!/usr/bin/env python3
from pathlib import Path

p = Path("docs/README.md")
s = p.read_text()

start = "## Benchmarks and numerical behavior / Benchmark 与数值行为\n"
end = "## Profiling and tuning / Profiling 与调优\n"

if start not in s or end not in s:
    raise SystemExit("section anchor not found")

before, rest = s.split(start, 1)
section, after = rest.split(end, 1)

lines = section.splitlines()
new = []
in_table = False

for line in lines:
    stripped = line.strip()

    if stripped.startswith("<!--") and stripped.endswith("-->"):
        continue

    if stripped.startswith("|") and stripped.endswith("|"):
        new.append(stripped)
        in_table = True
        continue

    if stripped == "" and in_table:
        continue

    if stripped:
        new.append(line)
    else:
        new.append("")

# remove repeated blank lines
clean = []
prev_blank = False
for line in new:
    blank = (line.strip() == "")
    if blank and prev_blank:
        continue
    clean.append(line)
    prev_blank = blank

new_section = start + "\n".join(clean).strip() + "\n\n"
p.write_text(before + new_section + end + after)

print("docs/README.md: compacted benchmark table section")
