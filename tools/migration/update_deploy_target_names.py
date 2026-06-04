from pathlib import Path

path = Path("interface/CMakeLists.txt")

text = path.read_text(encoding="utf-8")
old_text = text

replacements = [
    (
        'COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plchip"',
        'COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plcrocm"',
    ),
    (
        'COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plccpu"',
        'COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plccpu"',
    ),
    (
        'COMMAND mv "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plcgpu"',
        'COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${CMAKE_BINARY_DIR}/bin/plc" "${CMAKE_BINARY_DIR}/bin/plcgpu"',
    ),
]

for old, new in replacements:
    if old not in text:
        print(f"not found: {old}")
    text = text.replace(old, new)

if text == old_text:
    print("no changes made")
else:
    path.write_text(text, encoding="utf-8")
    print("updated interface/CMakeLists.txt")
