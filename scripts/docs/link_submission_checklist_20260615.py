from pathlib import Path

def add_after_line(path, anchor_line, new_line):
    p = Path(path)
    lines = p.read_text().splitlines(keepends=True)

    if any(line.strip() == new_line.strip() for line in lines):
        print(f"{path}: already updated")
        return

    for i, line in enumerate(lines):
        if line.strip() == anchor_line.strip():
            lines.insert(i + 1, new_line if new_line.endswith("\n") else new_line + "\n")
            p.write_text("".join(lines))
            print(f"{path}: updated")
            return

    raise SystemExit(f"{path}: anchor line not found: {anchor_line}")

add_after_line(
    "docs/README.md",
    "| Competition scorecard / 竞赛评分项对照 | [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) | [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md) | Contest scoring requirements mapped to repository evidence |",
    "| Submission checklist / 提交清单 | [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) | [SUBMISSION_CHECKLIST.zh-CN.md](SUBMISSION_CHECKLIST.zh-CN.md) | Final paper, PPT, video, repository, Docker, and experiment readiness checklist |",
)

add_after_line(
    "docs/COMPETITION_README.md",
    "| Contest scorecard | [Competition scorecard alignment](COMPETITION_SCORECARD.md) |",
    "| Submission checklist | [Submission checklist](SUBMISSION_CHECKLIST.md) |",
)

add_after_line(
    "docs/COMPETITION_README.zh-CN.md",
    "| 评分项对照 | [竞赛评分项对照](COMPETITION_SCORECARD.zh-CN.md) |",
    "| 提交清单 | [提交清单](SUBMISSION_CHECKLIST.zh-CN.md) |",
)

print("done")
