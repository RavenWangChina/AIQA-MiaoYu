# -*- coding: utf-8 -*-
"""qa-workflow 包结构契约测试：目录树必须与 Task 1 Interfaces 定义完全一致。"""
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent

EXPECTED_FILES = [
    "README.md",
    "CLAUDE.md",
    ".claude/agents/qa-archaeologist.md",
    ".claude/agents/qa-case-positive.md",
    ".claude/agents/qa-case-negative.md",
    ".claude/agents/qa-executor.md",
    ".claude/agents/qa-reporter.md",
    "qa-knowledge/00-索引.md",
    "qa-knowledge/00b-仓库注册表模板.md",
    "qa-knowledge/00c-设备池清单模板.md",
    "qa-knowledge/01-系统认知/模块卡片模板.md",
    "qa-knowledge/01-系统认知/01d-环境依赖卡模板.md",
    "qa-knowledge/01-系统认知/接口清单模板.md",
    "qa-knowledge/01-系统认知/架构总览模板.md",
    "qa-knowledge/02-用例库/L1冒烟模板.yaml",
    "qa-knowledge/02-用例库/L2功能模板.md",
    "qa-knowledge/02-用例库/L3场景模板.md",
    "qa-knowledge/02-用例库/L4探索模板.md",
    "qa-knowledge/02-用例库/02e-性能用例模板.yaml",
    "qa-knowledge/02-用例库/02f-稳定性场景模板.yaml",
    "qa-knowledge/02-用例库/02g-兼容矩阵模板.yaml",
    "qa-knowledge/02-用例库/02h-安全用例模板.yaml",
    "qa-knowledge/02-用例库/02i-升级迁移用例模板.yaml",
    "qa-knowledge/02-用例库/02j-设备在环用例模板.yaml",
    "qa-knowledge/02-用例库/02k-逆向对抗矩阵模板.md",
    "qa-knowledge/03-BUG库/模式库模板.md",
    "qa-knowledge/03-BUG库/报告模板.md",
    "qa-knowledge/03-BUG库/03c-BUG状态跟踪表模板.md",
    "qa-knowledge/03-BUG库/03d-flaky登记表模板.md",
    "qa-knowledge/04-报告库/轮次模板.md",
    "qa-knowledge/04-报告库/周期汇报模板.md",
    "scripts/selfcheck.py",
    "tools/install-batch1.ps1",
    "docs/2026-09-02-qa-test-workflow-design.html",
    "docs/部署手册.md",
]


def test_all_expected_files_exist():
    missing = [f for f in EXPECTED_FILES if not (PKG / f).is_file()]
    assert not missing, f"缺少文件: {missing}"


def test_no_stray_top_level_entries():
    allowed = {
        "README.md", "CLAUDE.md", ".claude", "qa-knowledge",
        "scripts", "tools", "tests", "docs", ".pytest_cache",
    }
    actual = {p.name for p in PKG.iterdir()}
    stray = actual - allowed
    assert not stray, f"包根目录出现多余条目: {stray}"
