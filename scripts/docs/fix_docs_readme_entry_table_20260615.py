from pathlib import Path

p = Path("docs/README.md")
s = p.read_text()

orphan_block = """<!-- COMPETITION_README_20260614_BEGIN -->
<!-- REPRODUCIBILITY_20260614_BEGIN -->
| Reproducibility / 可复现性 | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) | How to reproduce committed summaries, recover W7900 machines, check data, and run starter profiling |
<!-- REPRODUCIBILITY_20260614_END -->

| Competition README / 竞赛入口 | [COMPETITION_README.md](COMPETITION_README.md) | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md) | Reviewer-facing entry point aligned with the AMD ROCm/Radeon contest track |
<!-- COMPETITION_README_20260614_END -->

"""

main_anchor = """| Benchmark index / Benchmark 索引 | [benchmarks/README.md](benchmarks/README.md) | [benchmarks/README.md](benchmarks/README.md) | Benchmark documents and CSV links |
| Upstream reference / 上游参考 | [../README_UPSTREAM.md](../README_UPSTREAM.md) | — | Intentionally preserved as upstream snapshot; not translated |
"""

main_replacement = """| Benchmark index / Benchmark 索引 | [benchmarks/README.md](benchmarks/README.md) | [benchmarks/README.md](benchmarks/README.md) | Benchmark documents and CSV links |
<!-- REPRODUCIBILITY_20260614_BEGIN -->
| Reproducibility / 可复现性 | [REPRODUCIBILITY.md](REPRODUCIBILITY.md) | [REPRODUCIBILITY.zh-CN.md](REPRODUCIBILITY.zh-CN.md) | Reproduce committed summaries, recover W7900 machines, check data, and run starter profiling |
<!-- REPRODUCIBILITY_20260614_END -->
<!-- COMPETITION_README_20260614_BEGIN -->
| Competition README / 竞赛入口 | [COMPETITION_README.md](COMPETITION_README.md) | [COMPETITION_README.zh-CN.md](COMPETITION_README.zh-CN.md) | Reviewer-oriented path through the general project evidence |
| Competition scorecard / 竞赛评分项对照 | [COMPETITION_SCORECARD.md](COMPETITION_SCORECARD.md) | [COMPETITION_SCORECARD.zh-CN.md](COMPETITION_SCORECARD.zh-CN.md) | Contest scoring requirements mapped to repository evidence |
<!-- COMPETITION_README_20260614_END -->
| Upstream reference / 上游参考 | [../README_UPSTREAM.md](../README_UPSTREAM.md) | — | Intentionally preserved as upstream snapshot; not translated |
"""

if orphan_block not in s:
    print("orphan block not found; maybe already cleaned")
else:
    s = s.replace(orphan_block, "", 1)

if main_replacement in s:
    print("main entry rows already present")
elif main_anchor in s:
    s = s.replace(main_anchor, main_replacement, 1)
else:
    raise SystemExit("main entry anchor not found")

p.write_text(s)
print("docs/README.md updated")
