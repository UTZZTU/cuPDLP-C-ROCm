from pathlib import Path

path = Path(".gitignore")

existing = path.read_text(encoding="utf-8") if path.exists() else ""

patterns = [
    "validation/results/",
    "validation/netlib/",
    "validation/netlib_compressed/",
    "tools/emps",
    "tools/emps.c",
]

lines = existing.splitlines()

for pattern in patterns:
    if pattern not in lines:
        lines.append(pattern)

path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

print("updated .gitignore")
