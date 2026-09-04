# -*- coding: utf-8 -*-
"""qa-workflow 包自检：结构 / 模板 / 从对话 / 宪法 四类契约。
用法：python scripts/selfcheck.py（在包根执行）
退出码：0=全部通过；1=有缺失（stdout 列出明细）。目标机器部署后先跑本脚本。"""
from __future__ import annotations  # 兼容 Python 3.8：list[str] 等注解延迟求值
import re
import sys
from pathlib import Path

# Windows 管道下 stdout/stderr 默认走 locale 编码（cp936），统一为 utf-8
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PKG = Path(__file__).resolve().parent.parent

EXPECTED_FILES = [
    "README.md", "CLAUDE.md",
    ".claude/agents/qa-archaeologist.md", ".claude/agents/qa-case-positive.md",
    ".claude/agents/qa-case-negative.md", ".claude/agents/qa-executor.md",
    ".claude/agents/qa-reporter.md",
    "qa-knowledge/00-索引.md",
    "qa-knowledge/00b-仓库注册表模板.md", "qa-knowledge/00c-设备池清单模板.md",
    "qa-knowledge/01-系统认知/模块卡片模板.md", "qa-knowledge/01-系统认知/接口清单模板.md",
    "qa-knowledge/01-系统认知/01d-环境依赖卡模板.md",
    "qa-knowledge/01-系统认知/架构总览模板.md",
    "qa-knowledge/02-用例库/L1冒烟模板.yaml", "qa-knowledge/02-用例库/L2功能模板.md",
    "qa-knowledge/02-用例库/L3场景模板.md", "qa-knowledge/02-用例库/L4探索模板.md",
    "qa-knowledge/02-用例库/02e-性能用例模板.yaml", "qa-knowledge/02-用例库/02f-稳定性场景模板.yaml",
    "qa-knowledge/02-用例库/02g-兼容矩阵模板.yaml", "qa-knowledge/02-用例库/02h-安全用例模板.yaml",
    "qa-knowledge/02-用例库/02i-升级迁移用例模板.yaml", "qa-knowledge/02-用例库/02j-设备在环用例模板.yaml",
    "qa-knowledge/02-用例库/02k-逆向对抗矩阵模板.md",
    "qa-knowledge/03-BUG库/模式库模板.md", "qa-knowledge/03-BUG库/报告模板.md",
    "qa-knowledge/03-BUG库/03c-BUG状态跟踪表模板.md", "qa-knowledge/03-BUG库/03d-flaky登记表模板.md",
    "qa-knowledge/04-报告库/轮次模板.md", "qa-knowledge/04-报告库/周期汇报模板.md",
    "tools/install-batch1.ps1",
    "docs/2026-09-02-qa-test-workflow-design.html",
    "docs/部署手册.md",
]

REQUIRED_SECTIONS = {
    "qa-knowledge/00-索引.md": ["模块清单", "各库状态", "度量看板", "任务队列", "知识过期"],
    "qa-knowledge/00b-仓库注册表模板.md": ["远端", "分支策略", "接入状态", "无形资产"],
    "qa-knowledge/00c-设备池清单模板.md": ["真机", "能力保真度", "占用", "音频", "蓝牙"],
    "qa-knowledge/01-系统认知/01d-环境依赖卡模板.md": ["依赖服务", "健康检查", "快照还原"],
    "qa-knowledge/02-用例库/02e-性能用例模板.yaml": ["k6", "阈值", "启动时间", "内存", "allure"],
    "qa-knowledge/02-用例库/02f-稳定性场景模板.yaml": ["monkey", "长时", "内存泄漏", "观察窗"],
    "qa-knowledge/02-用例库/02g-兼容矩阵模板.yaml": ["设备", "api_level", "分辨率", "allure"],
    "qa-knowledge/02-用例库/02h-安全用例模板.yaml": ["zap", "权限最小化", "敏感数据", "allure"],
    "qa-knowledge/02-用例库/02i-升级迁移用例模板.yaml": ["覆盖安装", "数据保留", "回滚", "allure"],
    "qa-knowledge/02-用例库/02j-设备在环用例模板.yaml": ["蓝牙", "配网", "音频通路", "真机", "客观指标"],
    "qa-knowledge/02-用例库/02k-逆向对抗矩阵模板.md": ["破坏维度", "空值", "断网", "并发", "状态跳跃", "恢复条件", "复现计数"],
    "qa-knowledge/03-BUG库/03c-BUG状态跟踪表模板.md": ["新建", "复核", "已提单", "待验证", "禅道状态"],
    "qa-knowledge/03-BUG库/03d-flaky登记表模板.md": ["flaky", "隔离", "重跑策略", "计数"],
    "qa-knowledge/01-系统认知/模块卡片模板.md": ["入口", "依赖", "接口清单", "数据流", "已知坑", "绑定基线", "过期检测"],
    "qa-knowledge/01-系统认知/接口清单模板.md": ["路径", "参数", "鉴权", "归属模块"],
    "qa-knowledge/02-用例库/L2功能模板.md": ["前置", "步骤", "预期", "TC-", "allure", "双通道", "设计方法"],
    "qa-knowledge/02-用例库/L3场景模板.md": ["场景", "步骤", "预期", "allure", "双通道"],
    "qa-knowledge/02-用例库/L4探索模板.md": ["探索", "观察", "疑点", "charter"],
    "qa-knowledge/03-BUG库/模式库模板.md": ["特征", "高发模块", "反哺"],
    "qa-knowledge/03-BUG库/报告模板.md": ["定级", "复现概率", "环境", "使用的测试方法", "复现步骤", "预期 vs 实际", "证据链", "归因初判", "禅道", "flaky", "broken"],
    "qa-knowledge/04-报告库/轮次模板.md": ["范围", "用例执行结果", "BUG 清单", "证据链索引"],
    "qa-knowledge/04-报告库/周期汇报模板.md": ["本周范围", "进度", "质量态势", "趋势", "风险与求助"],
}

AGENTS = {
    ".claude/agents/qa-archaeologist.md": ["模块卡片", "接口清单", "01-系统认知"],
    ".claude/agents/qa-case-positive.md": ["正向", "做了该做的", "02-用例库"],
    ".claude/agents/qa-case-negative.md": ["破坏者", "逆向", "模式库"],
    ".claude/agents/qa-executor.md": ["checklist", "证据", "Allure"],
    ".claude/agents/qa-reporter.md": ["BUG 报告", "禅道", "周期汇报"],
}
COMMON_RUNTIME = [
    "开工先读知识库 00-索引.md", "只干职能内的事",
    "完整产物写入知识库文件，只回传摘要和产物路径", "从对话之间不通信",
]
ORCHESTRATOR_REQUIRED = [
    "qa-archaeologist", "qa-case-positive", "qa-case-negative", "qa-executor", "qa-reporter",
    "BUG 定级争议", "测试范围取舍", "不可逆动作", "合并去重", "复核",
    "摘要和产物路径", "没有证据=没完成",
]

problems: list[str] = []


def check(desc: str, ok: bool, detail: str = "") -> None:
    if not ok:
        problems.append(f"[{desc}] {detail}")


# 1) 结构
for f in EXPECTED_FILES:
    check("结构", (PKG / f).is_file(), f"缺少文件: {f}")

# 2) 模板
for rel, keys in REQUIRED_SECTIONS.items():
    p = PKG / rel
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        for kw in keys:
            check("模板", kw in text, f"{rel} 缺字段: {kw}")

# 3) 从对话
for rel, keys in AGENTS.items():
    p = PKG / rel
    if not p.is_file():
        continue
    text = p.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    check("从对话", bool(m), f"{rel} 缺 frontmatter")
    if m:
        check("从对话", "name:" in m.group(1), f"{rel} frontmatter 缺 name")
    for kw in COMMON_RUNTIME + keys:
        check("从对话", kw in text, f"{rel} 缺: {kw}")

# 4) 宪法
orch = PKG / "CLAUDE.md"
if orch.is_file():
    text = orch.read_text(encoding="utf-8")
    for kw in ORCHESTRATOR_REQUIRED:
        check("宪法", kw in text, f"CLAUDE.md 缺规则: {kw}")

for section in ["结构", "模板", "从对话", "宪法"]:
    n = sum(1 for p in problems if p.startswith(f"[{section}]"))
    print(f"{section}: {'通过' if n == 0 else f'{n} 项问题'}")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print("selfcheck 全部通过")
