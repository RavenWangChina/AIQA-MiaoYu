# -*- coding: utf-8 -*-
"""基线一致性门禁：校验 results/<task_id>/summary.yaml 与证据完整性。
用法：python docs/workflow/qa/baseline-gate.py <result_dir> [更多目录...]
校验项：①summary.yaml 存在且含 task_id/baseline ②基线 commit 引用格式合法（dev@7-40位hex）
        ③声明的 evidence 文件存在。任一失败退出码 1。"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HEX = re.compile(r"^dev@[0-9a-f]{7,40}$")

def gate(d: Path):
    errs = []
    s = d / "summary.yaml"
    if not s.is_file():
        return [f"{d.name}: 缺 summary.yaml"]
    t = s.read_text(encoding="utf-8", errors="ignore")
    if not re.search(r"^task_id:\s*\S+", t, re.M):
        errs.append(f"{d.name}: summary.yaml 缺 task_id")
    baselines = [b.strip() for b in re.findall(r"^(?:baseline|.*基线.*)[:：]\s*(.+)$", t, re.M) if "@" in b]
    commits = [c for b in baselines for c in re.findall(r"[\w-]+@[0-9a-fA-F]{7,40}", b)]
    if not commits:
        errs.append(f"{d.name}: 未发现可校验的基线 commit 引用（dev@hex）")
    for c in commits:
        if not HEX.match(c.lower()):
            errs.append(f"{d.name}: 基线引用格式非法: {c}")
    for ev in re.findall(r"[\w\-./\\]+\.(?:png|jpg|mp4|txt|log|xml|yaml|json)", t):
        p = d / ev
        if not p.is_file() and not (d / "evidence" / ev).is_file():
            errs.append(f"{d.name}: 证据引用不存在: {ev}")
    return errs

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python baseline-gate.py <result_dir> [...]")
        sys.exit(2)
    all_errs = []
    for arg in sys.argv[1:]:
        all_errs += gate(Path(arg))
    if all_errs:
        print("基线门禁未通过：")
        for e in all_errs:
            print(f"  [FAIL] {e}")
        sys.exit(1)
    print("基线门禁通过")
