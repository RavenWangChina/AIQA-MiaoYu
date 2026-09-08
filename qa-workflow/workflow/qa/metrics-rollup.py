# -*- coding: utf-8 -*-
"""度量看板自动汇总：扫描 03-BUG库 与 results/，生成度量看板 markdown，写入 00-索引.md。
用法：python docs/workflow/qa/metrics-rollup.py [--write]
  默认仅打印；--write 更新 00-索引.md 中 <METRICS>...</METRICS> 标记之间内容。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
KB = Path(r"F:\[TARGET_APP]-Toolchain\docs\qa-knowledge")
RESULTS = Path(r"F:\[TARGET_APP]-Toolchain\results")

def rollup():
    bug_dir = KB / "03-BUG库"
    bugs = [b for b in bug_dir.glob("*.md") if b.name.startswith(("SWAN-BUG", "BUG报告-"))]
    failed = broken = pending = 0
    sev = {"S1": 0, "S2": 0, "S3": 0, "S4": 0, "未定级": 0}
    for b in bugs:
        t = b.read_text(encoding="utf-8", errors="ignore")
        if "# BUG" not in t:
            continue
        if "分类：failed" in t or "分类：`failed`" in t:
            failed += 1
        elif "broken" in t:
            broken += 1
        if "缺陷管理系统单号：local" in t or "未提单" in t:
            pending += 1
        m = re.search(r"严重级[（(]?[^S]*?(S[1-4])", t) or re.search(r"严重级初判：?\s*L([1-4])", t)
        if m:
            key = ("S" if m.group(1).startswith("S") else "S") + m.group(1)[-1]
            sev[key] = sev.get(key, 0) + 1
        else:
            sev["未定级"] += 1
    # results 任务状态
    task_status = {}
    for s in RESULTS.glob("*/summary.yaml"):
        t = s.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^status:\s*(\S+)", t, re.M)
        task_status[s.parent.name] = m.group(1) if m else "unknown"
    done = sum(1 for v in task_status.values() if v in ("done", "completed", "complete"))
    partial = sum(1 for v in task_status.values() if v == "partially_done")
    blocked = sum(1 for v in task_status.values() if v == "blocked")
    lines = [
        f"- BUG 累计 {failed + broken}：failed {failed} / broken {broken}；未提单(local) {pending}",
        f"- 严重级分布：S1 {sev['S1']} / S2 {sev['S2']} / S3 {sev['S3']} / S4 {sev['S4']} / 未定级 {sev['未定级']}（含旧版 Lx 记法折算）",
        f"- 任务汇总（results/ 有 summary.yaml 的 {len(task_status)} 个）：done {done} / partially_done {partial} / blocked {blocked}",
        "- 用例量与自动化率以 02-用例库 与各轮执行记录为准（本行人工核对）",
    ]
    return "\n".join(lines), len(bugs), failed, broken

def write_block(block):
    idx = KB / "00-索引.md"
    t = idx.read_text(encoding="utf-8")
    new = f"<!-- METRICS:BEGIN 自动生成，勿手改（metrics-rollup.py） -->\n{block}\n<!-- METRICS:END -->"
    if "<!-- METRICS:BEGIN" in t:
        t = re.sub(r"<!-- METRICS:BEGIN.*?<!-- METRICS:END -->", new, t, flags=re.S)
    else:
        t += "\n## 度量看板\n" + new + "\n"
    idx.write_text(t, encoding="utf-8", newline="\n")

if __name__ == "__main__":
    block, n, f, b = rollup()
    print(block)
    if "--write" in sys.argv:
        write_block(block)
        print(f"\n已写入 00-索引.md 度量看板（BUG {n} = failed {f} + broken {b}）")
