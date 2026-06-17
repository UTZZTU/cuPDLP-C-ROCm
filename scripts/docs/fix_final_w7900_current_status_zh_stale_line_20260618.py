#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / "docs/W7900_CURRENT_STATUS.zh-CN.md"

old = """该派生结果对后续调优解释很重要：current 在 6 个 fast-core6 case 上
均降低了单迭代执行耗时，但由于部分 case 迭代次数增加，总 solve time
仍呈 mixed pattern。因此后续 W7900-specific tuning 应同时优化执行效率
与收敛行为。"""

new = """该派生结果现在作为 fast-core6 mixed-pattern 历史记录保留：current 在
6 个 fast-core6 case 上均降低了单迭代执行耗时，但由于部分 case 迭代次数增加，
总 solve time 仍呈 mixed pattern。后续 P10/P11/P12/P14-A1 已进一步补充证据链，
其中 P14-A1 quick6 repeated validation 显示 current 在 6/6 quick6 case 上快于
pre_tuning，geomean speedup 为 1.18889，median speedup 为 1.19502。"""

s = p.read_text(encoding="utf-8")
if old not in s:
    raise SystemExit("[MISS] exact stale paragraph not found; inspect docs/W7900_CURRENT_STATUS.zh-CN.md around before/current derived analysis")
p.write_text(s.replace(old, new, 1).rstrip() + "\n", encoding="utf-8", newline="\n")
print("[OK] fixed stale W7900-specific tuning sentence in docs/W7900_CURRENT_STATUS.zh-CN.md")
