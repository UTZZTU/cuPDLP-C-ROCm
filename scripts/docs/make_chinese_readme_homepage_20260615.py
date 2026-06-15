from pathlib import Path

def replace_all(text, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text

root = Path(".")
readme_en_path = root / "README.md"
readme_zh_path = root / "README.zh-CN.md"

if not readme_en_path.exists():
    raise SystemExit("missing README.md")
if not readme_zh_path.exists():
    raise SystemExit("missing README.zh-CN.md")

english = readme_en_path.read_text()
chinese = readme_zh_path.read_text()

english = replace_all(english, [
    ("中文主页: [README.zh-CN.md](README.zh-CN.md)", "中文主页: [README.md](README.md)"),
    ("> General users: start from this README and the [documentation map](docs/README.md).\n"
     "> AMD ROCm/Radeon contest reviewers: see [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).",
     "> General users: start from this English README or the [Chinese homepage](README.md).\n"
     "> AMD ROCm/Radeon contest reviewers: see [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)."),
])

chinese = replace_all(chinese, [
    ("English homepage: [README.md](README.md)", "English homepage: [README.en.md](README.en.md)"),
    ("> AMD ROCm/Radeon contest reviewers: start from [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md).",
     "> 普通 GitHub 读者：请从本 README 和 [文档地图](docs/README.md) 开始。\n"
     "> AMD ROCm/Radeon 赛题评委：请查看 [docs/COMPETITION_README.md](docs/COMPETITION_README.md) / [docs/COMPETITION_README.zh-CN.md](docs/COMPETITION_README.zh-CN.md)。"),
])
chinese = chinese.replace("English homepage: [README.md](README.md)", "English homepage: [README.en.md](README.en.md)")

(root / "README.en.md").write_text(english)
(root / "README.md").write_text(chinese)
(root / "README.zh-CN.md").write_text(chinese)

docs_readme = root / "docs" / "README.md"
if docs_readme.exists():
    s = docs_readme.read_text()
    s = s.replace(
        "| General GitHub users / 普通 GitHub 读者 | [Repository README](../README.md) / [中文主页](../README.zh-CN.md) |",
        "| General GitHub users / 普通 GitHub 读者 | [English README](../README.en.md) / [中文主页](../README.md) |",
    )
    s = s.replace(
        "| Repository homepage / 仓库主页 | [../README.md](../README.md) | [../README.zh-CN.md](../README.zh-CN.md) | Main project overview |",
        "| Repository homepage / 仓库主页 | [../README.en.md](../README.en.md) | [../README.md](../README.md) | Main project overview |",
    )
    docs_readme.write_text(s)

for path in [root / "docs" / "COMPETITION_SCORECARD.md", root / "docs" / "COMPETITION_SCORECARD.zh-CN.md"]:
    if path.exists():
        s = path.read_text()
        s = s.replace(
            "General users should start from [../README.md](../README.md) and [README.md](README.md).",
            "General users should start from the [Chinese homepage](../README.md), [English README](../README.en.md), and [documentation map](README.md).",
        )
        s = s.replace(
            "普通读者应先阅读 [../README.zh-CN.md](../README.zh-CN.md) 和 [README.md](README.md)。",
            "普通读者应先阅读 [中文主页](../README.md)、[English README](../README.en.md) 和 [文档地图](README.md)。",
        )
        path.write_text(s)

print("wrote README.en.md")
print("updated README.md as Chinese homepage")
print("kept README.zh-CN.md as Chinese compatibility alias")
print("updated docs/README.md language links when anchors were present")
print("updated competition scorecard intro links when anchors were present")
